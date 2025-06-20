"""
Logo/Icon Generator - Main CLI Entry Point (Windows)

Usage:
    python main.py generate --all                          # Generate with all models
    python main.py generate --models flux_dev,dalle3       # Generate with specific models
    python main.py generate --prompts spark_dialog         # Generate specific prompts
    python main.py process --remove-bg --create-ico        # Process existing images
    python main.py status                                  # Show system status
    python main.py list-models                            # List all available models
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.pipeline import GenerationPipeline
from src.core.models import model_registry
from src.core.config import Config
from src.utils.logging_utils import setup_logger

def setup_cli_logger():
    """Setup logger for CLI output (also writes to generation.log for UI streaming)"""
    from src.core.config import Config
    return setup_logger("main", Config.LOGS_DIR / "generation.log", level="INFO")

def cmd_status(args):
    """Show system status"""
    logger = setup_cli_logger()
    
    logger.info("=== Logo/Icon Generator Status ===")
    
    # Check API keys
    api_status = Config.validate_api_keys()
    logger.info("\nAPI Keys:")
    for provider, available in api_status.items():
        status = "✓ Available" if available else "✗ Missing"
        logger.info(f"  {provider.replace('_', '.').title()}: {status}")
    
    # Initialize and check generators
    logger.info("\nGenerators:")
    try:
        generator_status = model_registry.initialize()
        for provider, working in generator_status.items():
            status = "✓ Working" if working else "✗ Failed"
            logger.info(f"  {provider.replace('_', '.').title()}: {status}")
        
        # Show model counts
        models = model_registry.get_available_models()
        total_models = sum(len(provider_models) for provider_models in models.values())
        logger.info(f"\nTotal available models: {total_models}")
        
        for provider, provider_models in models.items():
            if provider_models:
                logger.info(f"  {provider.replace('_', '.').title()}: {len(provider_models)} models")
    
    except Exception as e:
        logger.error(f"Failed to initialize generators: {e}")
    
    # Check directories
    logger.info("\nDirectories:")
    dirs_to_check = [
        ("Config", Config.CONFIG_DIR),
        ("Output", Config.OUTPUT_DIR),
        ("Raw Images", Config.RAW_DIR),
        ("Processed", Config.PROCESSED_DIR),
        ("Icons", Config.ICONS_DIR),
        ("Logs", Config.LOGS_DIR)
    ]
    
    for name, path in dirs_to_check:
        exists = "✓" if path.exists() else "✗"
        logger.info(f"  {name}: {exists} {path}")
    
    # Check prompts file
    prompts_file = Config.get_prompts_file()
    if prompts_file.exists():
        try:
            from src.utils.file_utils import load_prompts
            prompts = load_prompts(prompts_file)
            logger.info(f"\nPrompts: ✓ {len(prompts)} prompts loaded from {prompts_file}")
        except Exception as e:
            logger.error(f"Prompts: ✗ Failed to load {prompts_file}: {e}")
    else:
        logger.error(f"Prompts: ✗ File not found: {prompts_file}")

def cmd_list_models(args):
    """List all available models"""
    logger = setup_cli_logger()
    
    try:
        model_registry.initialize()
        models = model_registry.get_available_models()
        
        logger.info("=== Available Models ===")
        
        for provider, provider_models in models.items():
            if provider_models:
                logger.info(f"\n{provider.replace('_', '.').title()}:")
                for model in provider_models:
                    logger.info(f"  - {model}")
                    # Show full spec for CLI usage
                    logger.info(f"    Usage: --models {provider}:{model}")
    
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return 1
    
    return 0

def cmd_generate(args):
    """Generate images"""
    logger = setup_cli_logger()
    
    try:
        # Initialize pipeline
        pipeline = GenerationPipeline()
        if not pipeline.initialize():
            logger.error("Failed to initialize pipeline")
            return 1
        
        # Parse models
        models = None
        if args.models:
            models = [m.strip() for m in args.models.split(",")]
        elif not args.all:
            logger.error("Must specify either --all or --models")
            return 1
        
        # Parse prompts
        prompts = None
        if args.prompts:
            prompts = [p.strip() for p in args.prompts.split(",")]
        
        # Run generation
        if args.process:
            # Run complete pipeline
            results = pipeline.run_complete_pipeline(
                models=models,
                prompts=prompts,
                remove_bg=args.remove_bg,
                create_ico=args.create_ico
            )
            
            # Print summary
            summary = results["summary"]
            logger.info("=== Pipeline Complete ===")
            logger.info(f"Images generated: {summary['images_generated']}")
            logger.info(f"Images processed: {summary['images_processed']}")
            logger.info(f"ICO files created: {summary['ico_files_created']}")
            logger.info(f"Total time: {summary['total_time']:.1f}s")
        
        else:
            # Just generation
            results = pipeline.generate_images(models=models, prompts=prompts)
            
            logger.info("=== Generation Complete ===")
            logger.info(f"Success rate: {results['success_rate']:.1%} ({results['successful']}/{results['total_tasks']})")
            logger.info(f"Total time: {results['total_time']:.1f}s")
            logger.info(f"Avg time per image: {results['avg_time_per_image']:.1f}s")
        
        # Save detailed results
        results_file = Config.LOGS_DIR / "last_generation_results.json"
        with open(results_file, 'w') as f:
            # Convert results to JSON-serializable format
            json_results = results.copy()
            json_results["results"] = [
                {
                    "success": r.success,
                    "prompt_id": r.prompt_id,
                    "model": r.model,
                    "file_path": str(r.file_path) if r.file_path else None,
                    "error": r.error,
                    "duration": r.duration
                }
                for r in results["results"] if hasattr(results, "results") and "results" in results
            ]
            json.dump(json_results, f, indent=2, default=str)
        
        logger.info(f"Detailed results saved to: {results_file}")
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def cmd_process(args):
    """Process existing images"""
    logger = setup_cli_logger()
    
    try:
        pipeline = GenerationPipeline()
        pipeline.initialize()
        
        input_dir = Path(args.input) if args.input else Config.RAW_DIR
        
        results = pipeline.process_images(
            input_dir=input_dir,
            remove_bg=args.remove_bg,
            create_ico=args.create_ico
        )
        
        logger.info("=== Processing Complete ===")
        logger.info(f"Images processed: {len(results['processed'])}")
        logger.info(f"ICO files created: {len(results['icons'])}")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return 1
    
    return 0

def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Logo/Icon Generator - Generate and process images using multiple AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                                   # Check system status
  %(prog)s list-models                             # List available models
  %(prog)s generate --all                          # Generate with all models
  %(prog)s generate --models flux_dev,dalle3       # Use specific models
  %(prog)s generate --all --process --remove-bg    # Generate + process pipeline
  %(prog)s process --remove-bg --create-ico        # Process existing images
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    
    # List models command
    list_parser = subparsers.add_parser("list-models", help="List all available models")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate images")
    gen_group = gen_parser.add_mutually_exclusive_group(required=True)
    gen_group.add_argument("--all", action="store_true", help="Use all available models")
    gen_group.add_argument("--models", help="Comma-separated list of models (e.g., flux_dev,dalle3)")
    
    gen_parser.add_argument("--prompts", help="Comma-separated list of prompt IDs to generate")
    gen_parser.add_argument("--process", action="store_true", help="Run complete pipeline (generate + process)")
    gen_parser.add_argument("--remove-bg", action="store_true", help="Remove backgrounds during processing")
    gen_parser.add_argument("--create-ico", action="store_true", help="Create ICO files during processing")
    
    # Process command
    proc_parser = subparsers.add_parser("process", help="Process existing images")
    proc_parser.add_argument("--input", help="Input directory (default: output/raw)")
    proc_parser.add_argument("--remove-bg", action="store_true", help="Remove backgrounds")
    proc_parser.add_argument("--create-ico", action="store_true", help="Create ICO files")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handlers
    if args.command == "status":
        return cmd_status(args)
    elif args.command == "list-models":
        return cmd_list_models(args)
    elif args.command == "generate":
        return cmd_generate(args)
    elif args.command == "process":
        return cmd_process(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())