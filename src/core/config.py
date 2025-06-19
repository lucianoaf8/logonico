"""
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