# src/utils/naming.py
"""
Consistent naming conventions for generated files
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

def sanitize_name(name: str) -> str:
    """Convert any string to filesystem-safe name"""
    # Replace spaces and special chars with underscores
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
    # Remove multiple consecutive underscores
    clean = re.sub(r'_+', '_', clean)
    # Remove leading/trailing underscores
    return clean.strip('_').lower()[:50]

def get_timestamp() -> str:
    """Get current timestamp in consistent format"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_filename(prompt_id: str, model: str, extension: str = "png", 
                     include_timestamp: bool = True, suffix: str = "") -> str:
    """
    Generate consistent filename
    Format: {prompt_id}_{model}_{timestamp}{suffix}.{ext}
    """
    clean_id = sanitize_name(prompt_id)
    clean_model = sanitize_name(model.replace("/", "_").replace("-", "_"))
    
    if include_timestamp:
        timestamp = get_timestamp()
        base = f"{clean_id}_{clean_model}_{timestamp}"
    else:
        base = f"{clean_id}_{clean_model}"
    
    if suffix:
        base += f"_{sanitize_name(suffix)}"
    
    return f"{base}.{extension}"

# src/utils/logging_utils.py
"""
Logging utilities for structured logging
"""

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str, log_file: Optional[Path] = None, level: str = "INFO") -> logging.Logger:
    """Set up structured logger"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# src/utils/file_utils.py
"""
File operation utilities
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests

def load_prompts(prompts_file: Path) -> List[Dict[str, Any]]:
    """Load prompts from JSON file"""
    try:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        # Ensure each prompt has an ID
        for i, prompt in enumerate(prompts):
            if 'id' not in prompt:
                # Generate ID from title or use index
                if 'title' in prompt:
                    from .naming import sanitize_name
                    prompt['id'] = sanitize_name(prompt['title'])
                else:
                    prompt['id'] = f"prompt_{i+1}"
        
        return prompts
    except Exception as e:
        raise RuntimeError(f"Failed to load prompts from {prompts_file}: {e}")

def download_image(url: str, output_path: Path, timeout: int = 30) -> bool:
    """Download image from URL to file"""
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(output_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def get_file_size_mb(file_path: Path) -> float:
    """Get file size in MB"""
    return file_path.stat().st_size / (1024 * 1024)

# src/utils/api_utils.py
"""
Common API utilities
"""

import time
import random
from typing import Callable, Any
import logging

def retry_with_backoff(func: Callable, max_retries: int = 3, base_delay: float = 1.0) -> Any:
    """Retry function with exponential backoff"""
    
    logger = logging.getLogger("api_utils")
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
            time.sleep(delay)
    
    raise Exception("Max retries exceeded")

def add_jitter(delay: float, jitter_factor: float = 0.1) -> float:
    """Add random jitter to delay"""
    jitter = delay * jitter_factor * random.uniform(-1, 1)
    return max(0, delay + jitter)