# src/core/pipeline.py - Modified with fail-fast logic
"""
Main pipeline orchestrator for image generation and processing
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from collections import defaultdict

from .config import Config
from .models import model_registry
from ..utils.file_utils import load_prompts
from ..utils.logging_utils import setup_logger
from ..processors.background_remover import BackgroundRemover
from ..processors.ico_converter import ICOConverter
from ..processors.image_optimizer import ImageOptimizer

class GenerationPipeline:
    """Main pipeline for image generation and processing"""
    
    def __init__(self):
        self.logger = setup_logger("pipeline", Config.LOGS_DIR / "generation.log", Config.LOG_LEVEL)
        self.background_remover = None
        self.ico_converter = None
        self.image_optimizer = None
        
        # Fail-fast tracking
        self.failed_models: Set[str] = set()  # Track failed provider:model combinations
        
        # Ensure directories exist
        Config.ensure_directories()
    
    def initialize(self) -> bool:
        """Initialize the pipeline and all generators"""
        self.logger.info("Initializing generation pipeline...")
        
        # Initialize model registry
        status = model_registry.initialize()
        
        working_providers = sum(status.values())
        if working_providers == 0:
            self.logger.error("No API providers are working. Check your API keys in .env file")
            return False
        
        # Initialize processors
        if Config.REMOVE_BACKGROUND:
            self.background_remover = BackgroundRemover()
        
        if Config.CREATE_ICO:
            self.ico_converter = ICOConverter(Config.ICO_SIZES)
        
        self.image_optimizer = ImageOptimizer()
        
        self.logger.info(f"Pipeline initialized with {working_providers} providers and {model_registry.get_model_count()} models")
        return True
    
    def generate_images(self, models: List[str] = None, prompts: List[str] = None, 
                       max_workers: int = None) -> Dict[str, Any]:
        """
        Generate images with specified models and prompts
        
        Args:
            models: List of model specs (provider:model or just model)
            prompts: List of prompt IDs to generate (None = all)
            max_workers: Number of parallel workers
        
        Returns:
            Dictionary with generation results and statistics
        """
        
        start_time = time.time()
        
        # Reset failed models tracking
        self.failed_models.clear()
        
        # Load prompts
        prompt_data = load_prompts(Config.get_prompts_file())
        
        if prompts:
            # Filter to specified prompts
            prompt_data = [p for p in prompt_data if p.get("id") in prompts]
        
        if not prompt_data:
            raise ValueError("No valid prompts found")
        
        # Determine models to use
        if models:
            model_specs = []
            for model_spec in models:
                try:
                    provider, model = model_registry.validate_model_spec(model_spec)
                    model_specs.append((provider, model))
                except ValueError as e:
                    self.logger.warning(f"Skipping invalid model spec '{model_spec}': {e}")
        else:
            # Use all available models
            model_specs = []
            for provider, generator in model_registry.get_all_generators().items():
                for model in generator.get_available_models():
                    model_specs.append((provider, model))
        
        if not model_specs:
            raise ValueError("No valid models specified")
        
        self.logger.info(f"Starting generation: {len(prompt_data)} prompts × {len(model_specs)} models = {len(prompt_data) * len(model_specs)} images")
        
        # Generate all combinations
        generation_tasks = []
        for prompt in prompt_data:
            for provider, model in model_specs:
                generation_tasks.append({
                    "prompt": prompt,
                    "provider": provider,
                    "model": model
                })
        
        # Execute generations with fail-fast logic
        results = self._execute_generation_tasks_failfast(generation_tasks, max_workers or Config.MAX_WORKERS)
        
        # Collect statistics
        total_time = time.time() - start_time
        successful = len([r for r in results if r.success])
        failed = len(results) - successful
        skipped = len(generation_tasks) - len(results)
        
        stats = {
            "total_tasks": len(generation_tasks),
            "executed": len(results),
            "skipped": skipped,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(results) if results else 0,
            "total_time": total_time,
            "avg_time_per_image": total_time / len(results) if results else 0,
            "failed_models": list(self.failed_models),
            "results": results
        }
        
        self.logger.info(f"Generation complete: {successful}/{len(results)} successful, {skipped} skipped, in {total_time:.1f}s")
        if self.failed_models:
            self.logger.info(f"Failed models (skipped subsequent prompts): {', '.join(self.failed_models)}")
        
        return stats
    
    def _execute_generation_tasks_failfast(self, tasks: List[Dict], max_workers: int) -> List[Any]:
        """Execute generation tasks with fail-fast logic for failed models"""
        
        results = []
        
        # Group tasks by provider:model for fail-fast logic
        tasks_by_model = defaultdict(list)
        for task in tasks:
            model_key = f"{task['provider']}:{task['model']}"
            tasks_by_model[model_key].append(task)
        
        # Process each model group
        for model_key, model_tasks in tasks_by_model.items():
            if model_key in self.failed_models:
                self.logger.info(f"Skipping {len(model_tasks)} tasks for failed model: {model_key}")
                continue
            
            self.logger.info(f"Processing {len(model_tasks)} tasks for model: {model_key}")
            
            # Try first task for this model
            first_task = model_tasks[0]
            first_result = self._generate_single_image(first_task)
            results.append(first_result)
            
            # If first task failed with certain errors, skip remaining tasks for this model
            if not first_result.success and self._should_skip_model(first_result.error):
                self.failed_models.add(model_key)
                self.logger.warning(f"Model {model_key} failed with: {first_result.error}")
                self.logger.warning(f"Skipping remaining {len(model_tasks) - 1} tasks for this model")
                continue
            
            # If first task succeeded or failed with a non-fatal error, process remaining tasks
            if len(model_tasks) > 1:
                remaining_tasks = model_tasks[1:]
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit remaining tasks for this model
                    future_to_task = {}
                    for task in remaining_tasks:
                        # Double-check model hasn't failed while we were processing
                        if model_key not in self.failed_models:
                            future = executor.submit(self._generate_single_image, task)
                            future_to_task[future] = task
                    
                    # Collect results
                    for future in as_completed(future_to_task):
                        task = future_to_task[future]
                        try:
                            result = future.result()
                            results.append(result)
                            
                            # Check if this result should cause us to skip future tasks
                            if not result.success and self._should_skip_model(result.error):
                                self.failed_models.add(model_key)
                                self.logger.warning(f"Model {model_key} failed during batch, marking as failed")
                                
                        except Exception as e:
                            self.logger.error(f"Task execution failed: {task['provider']}:{task['model']} {task['prompt']['id']} - {e}")
                            # Create failed result
                            from ..generators.base import GenerationResult
                            failed_result = GenerationResult(
                                success=False,
                                prompt_id=task['prompt']['id'],
                                model=f"{task['provider']}:{task['model']}",
                                error=str(e)
                            )
                            results.append(failed_result)
        
        return results
    
    def _should_skip_model(self, error_message: str) -> bool:
        """Determine if an error should cause us to skip remaining tasks for a model"""
        if not error_message:
            return False
        
        error_lower = error_message.lower()
        
        # Rate limiting errors
        if "rate limit" in error_lower or "429" in error_lower:
            return True
        
        # Authentication errors
        if "unauthorized" in error_lower or "401" in error_lower or "invalid api key" in error_lower:
            return True
        
        # Quota exceeded errors
        if "quota" in error_lower or "insufficient" in error_lower:
            return True
        
        # Service unavailable errors
        if "503" in error_lower or "service unavailable" in error_lower:
            return True
        
        # Model not found or unavailable
        if "model not found" in error_lower or "404" in error_lower:
            return True
        
        return False
    
    def _generate_single_image(self, task: Dict) -> Any:
        """Generate a single image"""
        
        prompt = task["prompt"]
        provider = task["provider"]
        model = task["model"]
        
        generator = model_registry.get_generator(provider)
        if not generator:
            raise Exception(f"Generator not available: {provider}")
        
        return generator.generate(
            prompt=prompt["prompt"],
            prompt_id=prompt["id"],
            model=model,
            output_dir=Config.RAW_DIR
        )
    
    def process_images(self, input_dir: Path = None, remove_bg: bool = None, 
                      create_ico: bool = None) -> Dict[str, List[Path]]:
        """
        Process existing images (background removal, ICO conversion)
        
        Args:
            input_dir: Directory containing images to process
            remove_bg: Whether to remove backgrounds
            create_ico: Whether to create ICO files
        
        Returns:
            Dictionary with lists of processed file paths
        """
        
        input_dir = input_dir or Config.RAW_DIR
        remove_bg = remove_bg if remove_bg is not None else Config.REMOVE_BACKGROUND
        create_ico = create_ico if create_ico is not None else Config.CREATE_ICO
        
        if not input_dir.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        
        # Find image files
        image_files = []
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            image_files.extend(input_dir.glob(f"*{ext}"))
        
        if not image_files:
            self.logger.warning(f"No image files found in {input_dir}")
            return {"processed": [], "icons": []}
        
        self.logger.info(f"Processing {len(image_files)} images")
        
        processed_files = []
        ico_files = []
        
        # Background removal
        if remove_bg and self.background_remover:
            self.logger.info("Removing backgrounds...")
            # Filter out SVG files for background removal
            bg_removal_files = [f for f in image_files if f.suffix.lower() != '.svg']
            if bg_removal_files:
                processed_files = self.background_remover.process_batch(bg_removal_files, Config.PROCESSED_DIR)
                source_files_for_ico = processed_files
            else:
                source_files_for_ico = image_files
        else:
            source_files_for_ico = image_files
        
        # ICO conversion
        if create_ico and self.ico_converter:
            self.logger.info("Converting to ICO...")
            # Filter out SVG files for ICO conversion
            ico_conversion_files = [f for f in source_files_for_ico if f.suffix.lower() != '.svg']
            if ico_conversion_files:
                ico_files = self.ico_converter.convert_batch(ico_conversion_files, Config.ICONS_DIR)
        
        self.logger.info(f"Processing complete: {len(processed_files)} processed, {len(ico_files)} ICO files")
        
        return {
            "processed": processed_files,
            "icons": ico_files
        }
    
    def run_complete_pipeline(self, models: List[str] = None, prompts: List[str] = None,
                             remove_bg: bool = True, create_ico: bool = True) -> Dict[str, Any]:
        """
        Run the complete pipeline: generate + process
        
        Returns:
            Complete results including generation stats and processed files
        """
        
        self.logger.info("Starting complete pipeline...")
        
        # Generation phase
        generation_stats = self.generate_images(models, prompts)
        
        # Get successful generation files
        successful_files = []
        for result in generation_stats["results"]:
            if result.success and result.file_path:
                successful_files.append(result.file_path)
        
        # Processing phase
        if successful_files:
            processing_results = self.process_images(
                input_dir=Config.RAW_DIR,
                remove_bg=remove_bg,
                create_ico=create_ico
            )
        else:
            processing_results = {"processed": [], "icons": []}
        
        # Combine results
        complete_results = {
            "generation": generation_stats,
            "processing": processing_results,
            "summary": {
                "images_generated": generation_stats["successful"],
                "images_processed": len(processing_results["processed"]),
                "ico_files_created": len(processing_results["icons"]),
                "total_time": generation_stats["total_time"],
                "failed_models": generation_stats["failed_models"],
                "tasks_skipped": generation_stats["skipped"]
            }
        }
        
        self.logger.info("Complete pipeline finished")
        return complete_results