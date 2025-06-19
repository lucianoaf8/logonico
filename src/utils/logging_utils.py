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

def log_api_call(logger: logging.Logger, provider: str, model: str, prompt: str, 
                status: str, duration: float = None, error: str = None):
    """Log API call with structured info"""
    
    msg = f"[{provider}] {model} | {prompt[:50]}... | {status}"
    
    if duration:
        msg += f" | {duration:.2f}s"
    
    if status == "SUCCESS":
        logger.info(msg)
    elif status == "FAILED":
        logger.error(f"{msg} | Error: {error}")
    else:
        logger.warning(msg)
