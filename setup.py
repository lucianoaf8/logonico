#!/usr/bin/env python
"""
Complete setup script for logo-icon-generator project (Windows)
This creates the entire project structure and all code files.
"""

import os
from pathlib import Path

def create_file(filepath: Path, content: str):
    """Create a file with the given content if it does not already exist"""
    if filepath.exists():
        print(f"Exists, skipping: {filepath}")
        return
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding='utf-8')
    print(f"Created: {filepath}")

def main():
    # Use current working directory as the project root instead of creating a nested folder
    base_dir = Path.cwd()
    print(f"Creating complete project in: {base_dir.absolute()}")
    
    # Create directory structure
    directories = [
        "src\\core",
        "src\\generators", 
        "src\\processors",
        "src\\utils",
        "config",
        "output\\raw",
        "output\\processed", 
        "output\\icons",
        "logs",
        "cache",
        "tests"
    ]
    
    for dir_path in directories:
        (base_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    init_files = [
        "src\\__init__.py",
        "src\\core\\__init__.py", 
        "src\\generators\\__init__.py",
        "src\\processors\\__init__.py",
        "src\\utils\\__init__.py"
    ]
    
    for init_file in init_files:
        init_path = base_dir / init_file
        if not init_path.exists():
            init_path.touch()
            print(f"Created: {init_path}")
        else:
            print(f"Exists, skipping: {init_path}")
    
    # Create .env.example
    env_example = '''# API Keys - Copy to .env and fill in your keys
TOGETHER_API_KEY=your_together_api_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
OPENAI_API_KEY=your_openai_api_key_here
FAL_KEY=your_fal_ai_key_here

# Optional Settings
LOG_LEVEL=INFO
MAX_WORKERS=4
DEFAULT_SIZE=1024
TIMEOUT_SECONDS=120
MAX_RETRIES=3
REMOVE_BACKGROUND=true
CREATE_ICO=true
'''
    create_file(base_dir / ".env.example", env_example)
    
    # Create requirements.txt
    requirements = '''requests>=2.31.0
python-dotenv>=1.0.0
Pillow>=10.2.0
rembg>=2.0.50
openai>=1.12.0
pathlib
typing
concurrent.futures
argparse
'''
    create_file(base_dir / "requirements.txt", requirements)
    
    # Create sample prompts.json
    prompts = '''[
  {
    "id": "spark_dialog", 
    "title": "Spark Dialog Bubble + Circuit",
    "prompt": "Minimalist, futuristic Chrome extension icon. A speech bubble representing conversation, overlaid with a glowing electric spark and subtle circuit or neural network lines inside or around the bubble. Neon blue and indigo gradient, crisp vector style, modern and sophisticated, high contrast. No text or letters. Suitable for small sizes."
  },
  {
    "id": "magic_wand",
    "title": "Magic Wand + Text Cursor", 
    "prompt": "Minimalist, modern Chrome extension icon. A sleek magic wand crossing a classic text cursor (I-beam), with small glowing pixel stars or sparkles suggesting enhancement or transformation. Futuristic color scheme with black, white, and neon blue accents. High-contrast, crisp vector style, easily recognizable at small sizes, no text or letters."
  },
  {
    "id": "terminal_spark",
    "title": "Terminal/Prompt Brackets + Spark",
    "prompt": "Modern, futuristic Chrome extension icon. Features classic prompt brackets (e.g., > or >>>) inside a rounded rectangle or terminal window, with an electric blue spark or glowing lines to suggest AI generation or automation. Indigo and blue gradient, subtle 3D shadow, minimalist vector style, high visibility at small sizes. No text or letters."
  },
  {
    "id": "ai_circuit",
    "title": "AI Circuit Node + Text",
    "prompt": "Futuristic, minimalist Chrome extension icon. Abstract neural node or circuit motif, with small stylized text glyphs or a subtle P shape integrated, suggesting prompt and AI intelligence. Silver, blue, and holographic gradients, crisp vector lines, modern and sophisticated, easily recognizable at small sizes. No full words or obvious letters."
  },
  {
    "id": "bubble_circuit",
    "title": "Bubble + Circuit (Combined, Default Suggestion)",
    "prompt": "Minimalist, futuristic Chrome extension icon, featuring a speech bubble merged with a glowing circuit or neural network motif. Neon blue and indigo gradients, subtle spark or glow, crisp vector lines. Modern, sophisticated, suitable for an AI prompt assistant. High-contrast, easily recognizable at small sizes. No text or letters."
  }
]'''
    create_file(base_dir / "config" / "prompts.json", prompts)
    
    # Core configuration
    config_py = '''"""
Configuration management for logo-icon-generator
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration management"""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    OUTPUT_DIR = BASE_DIR / "output"
    RAW_DIR = OUTPUT_DIR / "raw"
    PROCESSED_DIR = OUTPUT_DIR / "processed"
    ICONS_DIR = OUTPUT_DIR / "icons"
    LOGS_DIR = BASE_DIR / "logs"
    CACHE_DIR = BASE_DIR / "cache"
    CONFIG_DIR = BASE_DIR / "config"
    
    # API Keys
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    FAL_KEY = os.getenv("FAL_KEY", "")
    
    # Generation Settings
    DEFAULT_SIZE = int(os.getenv("DEFAULT_SIZE", "1024"))
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "120"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # Processing Settings
    REMOVE_BACKGROUND = os.getenv("REMOVE_BACKGROUND", "true").lower() == "true"
    CREATE_ICO = os.getenv("CREATE_ICO", "true").lower() == "true"
    ICO_SIZES = [16, 32, 48, 64, 128, 256]
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def ensure_directories(cls):
        """Create required directories"""
        for dir_path in [cls.RAW_DIR, cls.PROCESSED_DIR, cls.ICONS_DIR, 
                        cls.LOGS_DIR, cls.CACHE_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_prompts_file(cls) -> Path:
        """Get path to prompts.json"""
        return cls.CONFIG_DIR / "prompts.json"
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Validate which API keys are available"""
        return {
            "together_ai": len(cls.TOGETHER_API_KEY) > 10,
            "replicate": len(cls.REPLICATE_API_TOKEN) > 10,
            "openai": len(cls.OPENAI_API_KEY) > 10,
            "fal_ai": len(cls.FAL_KEY) > 10
        }

# Model configurations
MODEL_CONFIGS = {
    "together_ai": {
        "flux_dev": {
            "model": "black-forest-labs/FLUX.1-dev",
            "params": {"width": 1024, "height": 1024, "steps": 30, "n": 1}
        },
        "flux_lora": {
            "model": "black-forest-labs/FLUX.1-dev-lora", 
            "params": {
                "width": 1024, "height": 1024, "steps": 30, "n": 1,
                "response_format": "url",
                "image_loras": [{
                    "path": "https://huggingface.co/Shakker-Labs/FLUX.1-dev-LoRA-Logo-Design",
                    "scale": 0.8
                }]
            }
        },
        "flux_schnell": {
            "model": "black-forest-labs/FLUX.1-schnell",
            "params": {"width": 1024, "height": 1024, "steps": 4, "n": 1}
        }
    },
    "replicate": {
        "galleri5_icons": {
            "model": "galleri5/icons",
            "type": "community"
        },
        "flux_schnell": {
            "model": "black-forest-labs/flux-schnell", 
            "type": "official"
        },
        "ideogram_v2": {
            "model": "ideogram-ai/ideogram-v2",
            "type": "official"
        },
        "recraft_svg": {
            "model": "recraft-ai/recraft-v3-svg",
            "type": "official"
        }
    },
    "openai": {
        "dalle3": {
            "model": "dall-e-3",
            "params": {"size": "1024x1024", "quality": "standard", "n": 1}
        }
    },
    "fal_ai": {
        "flux_dev": {
            "model": "fal-ai/flux/dev"
        },
        "recraft": {
            "model": "fal-ai/recraft-20b"
        },
        "flux_schnell": {
            "model": "fal-ai/flux/schnell"
        }
    }
}
'''
    create_file(base_dir / "src" / "core" / "config.py", config_py)
    
    # Main CLI file
    main_py = '''#!/usr/bin/env python3
"""
Logo/Icon Generator - Main CLI Entry Point

Usage:
    python main.py status                                  # Check system status
    python main.py list-models                            # List all available models  
    python main.py generate --all                          # Generate with all models
    python main.py generate --models flux_dev,dalle3       # Generate with specific models
    python main.py generate --all --process --remove-bg    # Generate + full processing
    python main.py process --remove-bg --create-ico        # Process existing images
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
    """Setup logger for CLI output"""
    return setup_logger("main", level="INFO")

def cmd_status(args):
    """Show system status"""
    logger = setup_cli_logger()
    
    logger.info("=== Logo/Icon Generator Status ===")
    
    # Check API keys
    api_status = Config.validate_api_keys()
    logger.info("\\nAPI Keys:")
    for provider, available in api_status.items():
        status = "✓ Available" if available else "✗ Missing"
        logger.info(f"  {provider.replace('_', '.').title()}: {status}")
    
    # Initialize and check generators
    logger.info("\\nGenerators:")
    try:
        generator_status = model_registry.initialize()
        for provider, working in generator_status.items():
            status = "✓ Working" if working else "✗ Failed"
            logger.info(f"  {provider.replace('_', '.').title()}: {status}")
        
        # Show model counts
        models = model_registry.get_available_models()
        total_models = sum(len(provider_models) for provider_models in models.values())
        logger.info(f"\\nTotal available models: {total_models}")
        
        for provider, provider_models in models.items():
            if provider_models:
                logger.info(f"  {provider.replace('_', '.').title()}: {len(provider_models)} models")
    
    except Exception as e:
        logger.error(f"Failed to initialize generators: {e}")

def cmd_list_models(args):
    """List all available models"""
    logger = setup_cli_logger()
    
    try:
        model_registry.initialize()
        models = model_registry.get_available_models()
        
        logger.info("=== Available Models ===")
        
        for provider, provider_models in models.items():
            if provider_models:
                logger.info(f"\\n{provider.replace('_', '.').title()}:")
                for model in provider_models:
                    logger.info(f"  - {model}")
    
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
    
    parser = argparse.ArgumentParser(description="Logo/Icon Generator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    
    # List models command
    list_parser = subparsers.add_parser("list-models", help="List all available models")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate images")
    gen_group = gen_parser.add_mutually_exclusive_group(required=True)
    gen_group.add_argument("--all", action="store_true", help="Use all available models")
    gen_group.add_argument("--models", help="Comma-separated list of models")
    
    gen_parser.add_argument("--prompts", help="Comma-separated list of prompt IDs")
    gen_parser.add_argument("--process", action="store_true", help="Run complete pipeline")
    gen_parser.add_argument("--remove-bg", action="store_true", help="Remove backgrounds")
    gen_parser.add_argument("--create-ico", action="store_true", help="Create ICO files")
    
    # Process command
    proc_parser = subparsers.add_parser("process", help="Process existing images")
    proc_parser.add_argument("--input", help="Input directory")
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
'''
    create_file(base_dir / "main.py", main_py)
    
    # README
    readme = '''# Logo/Icon Generator (Windows)

Professional logo and icon generation system using multiple AI models with integrated processing pipeline.

## Quick Start (Windows)

### Option 1: Automatic Setup
1. **Download setup script**: Save `setup_windows.bat` to your desired folder
2. **Run setup**: Double-click `setup_windows.bat` or run in Command Prompt
3. **Edit API keys**: The script will open .env file for you to add your keys
4. **Start generating**: Use the commands below

### Option 2: Manual Setup
1. **Create project**:
   ```cmd
   python complete_setup.py
   cd logo-icon-generator
   ```

2. **Configure**:
   ```cmd
   copy .env.example .env
   notepad .env
   ```
   Add your API keys to the .env file

3. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Test setup**:
   ```cmd
   python main.py status
   ```

## Commands (Windows)

### Check System
```cmd
python main.py status                    # Check API keys and models
python main.py list-models              # List all available models
```

### Generate Images
```cmd
# Generate with all available models
python main.py generate --all

# Generate with specific models  
python main.py generate --models flux_dev,dalle3

# Generate specific prompts
python main.py generate --all --prompts spark_dialog,magic_wand

# Full pipeline (generate + background removal + ICO conversion)
python main.py generate --all --process --remove-bg --create-ico
```

### Process Existing Images
```cmd
# Process images in output\\raw folder
python main.py process --remove-bg --create-ico

# Process custom folder
python main.py process --input C:\\path\\to\\images --remove-bg --create-ico
```

## Features

- **Multiple AI Providers**: Together AI, Replicate, OpenAI, Fal.ai
- **Parallel Processing**: Generate multiple images simultaneously  
- **Background Removal**: AI-powered background removal
- **ICO Conversion**: Multi-size ICO file creation
- **Consistent Naming**: Organized file naming with model tags
- **Error Handling**: Robust error handling and fallbacks
- **Windows Compatible**: Native Windows support with batch scripts

## Project Structure (Windows)

```
logo-icon-generator\\
├── config\\prompts.json      # Prompt definitions
├── src\\                     # Source code
├── output\\                  # Generated images
│   ├── raw\\                # Original generated images
│   ├── processed\\          # Background removed images
│   └── icons\\              # ICO format files
├── logs\\                   # Generation logs
├── setup_windows.bat        # Windows setup script
└── main.py                  # CLI entry point
```

## View Results (Windows)

```cmd
# Open output folders in Windows Explorer
explorer output\\raw         # Original images
explorer output\\processed   # Background removed  
explorer output\\icons       # ICO files
explorer logs               # Log files
```

## API Keys Required

Add these to your `.env` file:

- `TOGETHER_API_KEY` - Together AI API key
- `REPLICATE_API_TOKEN` - Replicate API token  
- `OPENAI_API_KEY` - OpenAI API key
- `FAL_KEY` - Fal.ai API key

You only need the keys for the providers you want to use.

## Troubleshooting (Windows)

### Python Not Found
- Install Python from python.org
- Check "Add Python to PATH" during installation
- Restart Command Prompt

### Permission Issues
- Run Command Prompt as Administrator
- Right-click cmd.exe → "Run as administrator"

### Dependencies Issues
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt -v
```
'''
    create_file(base_dir / "README.md", readme)
    
    print(f"\n✅ Complete project created in: {base_dir.absolute()}")
    print("\nNext steps:")
    print("1. cp .env.example .env")
    print("2. Edit .env with your API keys")
    print("3. pip install -r requirements.txt")
    print("4. python main.py status")
    print("5. python main.py generate --all")

if __name__ == "__main__":
    main()