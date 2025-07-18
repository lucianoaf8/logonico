# src/core/models.py
"""
Model registry and factory for all image generators
"""

import logging
from typing import Dict, List, Optional, Type
from ..generators.base import BaseGenerator
from ..generators.together_ai import TogetherAIGenerator
from ..generators.replicate import ReplicateGenerator
from ..generators.openai import OpenAIGenerator
from ..generators.fal_ai import FalAIGenerator
from .config import Config

class ModelRegistry:
    """Registry for all available image generation models"""
    
    def __init__(self):
        self.logger = logging.getLogger("model_registry")
        self._generators: Dict[str, BaseGenerator] = {}
        self._initialized = False
    
    def initialize(self) -> Dict[str, bool]:
        """Initialize all available generators based on API keys"""
        
        if self._initialized:
            return self.get_status()
        
        api_keys = Config.validate_api_keys()
        status = {}
        
        # Initialize Together AI
        if api_keys["together_ai"]:
            try:
                generator = TogetherAIGenerator(Config.TOGETHER_API_KEY)
                if generator.test_connection():
                    self._generators["together_ai"] = generator
                    status["together_ai"] = True
                    self.logger.info("Together AI generator initialized")
                else:
                    status["together_ai"] = False
                    self.logger.warning("Together AI connection test failed")
            except Exception as e:
                status["together_ai"] = False
                self.logger.error(f"Failed to initialize Together AI: {e}")
        else:
            status["together_ai"] = False
        
        # Initialize Replicate
        if api_keys["replicate"]:
            try:
                generator = ReplicateGenerator(Config.REPLICATE_API_TOKEN)
                if generator.test_connection():
                    self._generators["replicate"] = generator
                    status["replicate"] = True
                    self.logger.info("Replicate generator initialized")
                else:
                    status["replicate"] = False
                    self.logger.warning("Replicate connection test failed")
            except Exception as e:
                status["replicate"] = False
                self.logger.error(f"Failed to initialize Replicate: {e}")
        else:
            status["replicate"] = False
        
        # Initialize OpenAI
        if api_keys["openai"]:
            try:
                generator = OpenAIGenerator(Config.OPENAI_API_KEY)
                if generator.test_connection():
                    self._generators["openai"] = generator
                    status["openai"] = True
                    self.logger.info("OpenAI generator initialized")
                else:
                    status["openai"] = False
                    self.logger.warning("OpenAI connection test failed")
            except Exception as e:
                status["openai"] = False
                self.logger.error(f"Failed to initialize OpenAI: {e}")
        else:
            status["openai"] = False
        
        # Initialize Fal.ai
        if api_keys["fal_ai"]:
            try:
                generator = FalAIGenerator(Config.FAL_KEY)
                if generator.test_connection():
                    self._generators["fal_ai"] = generator
                    status["fal_ai"] = True
                    self.logger.info("Fal.ai generator initialized")
                else:
                    status["fal_ai"] = False
                    self.logger.warning("Fal.ai connection test failed")
            except Exception as e:
                status["fal_ai"] = False
                self.logger.error(f"Failed to initialize Fal.ai: {e}")
        else:
            status["fal_ai"] = False
        
        self._initialized = True
        
        working_count = sum(status.values())
        total_count = len(status)
        self.logger.info(f"Model registry initialized: {working_count}/{total_count} providers available")
        
        return status
    
    def get_generator(self, provider: str) -> Optional[BaseGenerator]:
        """Get generator for a specific provider"""
        return self._generators.get(provider)
    
    def get_all_generators(self) -> Dict[str, BaseGenerator]:
        """Get all available generators"""
        return self._generators.copy()
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get all available models by provider"""
        models = {}
        for provider, generator in self._generators.items():
            models[provider] = generator.get_available_models()
        return models
    
    def get_model_count(self) -> int:
        """Get total number of available models"""
        total = 0
        for generator in self._generators.values():
            total += len(generator.get_available_models())
        return total
    
    def get_status(self) -> Dict[str, bool]:
        """Get status of all providers"""
        return {provider: provider in self._generators for provider in ["together_ai", "replicate", "openai", "fal_ai"]}
    
    def validate_model_spec(self, model_spec: str) -> tuple[str, str]:
        """
        Validate and parse model specification
        Format: provider:model or just model (will try all providers)
        Returns: (provider, model)
        """
        if ":" in model_spec:
            provider, model = model_spec.split(":", 1)
            
            generator = self.get_generator(provider)
            if not generator:
                raise ValueError(f"Provider '{provider}' not available")
            
            if not generator.validate_model(model):
                raise ValueError(f"Model '{model}' not valid for provider '{provider}'")
            
            return provider, model
        else:
            # Try to find model in any provider
            for provider, generator in self._generators.items():
                if generator.validate_model(model_spec):
                    return provider, model_spec
            
            raise ValueError(f"Model '{model_spec}' not found in any available provider")

# Global registry instance
model_registry = ModelRegistry()

# src/core/pipeline.py
"""
Main pipeline orchestrator for image generation and processing
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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
        
        # Execute generations in parallel
        results = self._execute_generation_tasks(generation_tasks, max_workers or Config.MAX_WORKERS)
        
        # Collect statistics
        total_time = time.time() - start_time
        successful = len([r for r in results if r.success])
        failed = len(results) - successful
        
        stats = {
            "total_tasks": len(generation_tasks),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(results) if results else 0,
            "total_time": total_time,
            "avg_time_per_image": total_time / len(results) if results else 0,
            "results": results
        }
        
        self.logger.info(f"Generation complete: {successful}/{len(results)} successful in {total_time:.1f}s")
        
        return stats
    
    def _execute_generation_tasks(self, tasks: List[Dict], max_workers: int) -> List[Any]:
        """Execute generation tasks in parallel"""
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for task in tasks:
                future = executor.submit(self._generate_single_image, task)
                future_to_task[future] = task
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Task failed: {task['provider']}:{task['model']} {task['prompt']['id']} - {e}")
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
                "total_time": generation_stats["total_time"]
            }
        }
        
        self.logger.info("Complete pipeline finished")
        return complete_results