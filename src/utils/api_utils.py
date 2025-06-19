# src/utils/api_utils.py
"""
Common API utilities
"""

import time
import random
from typing import Callable, Any, Dict
import logging
import requests
from pathlib import Path

def retry_with_backoff(func: Callable, max_retries: int = 3, base_delay: float = 1.0, 
                      exceptions: tuple = (Exception,)) -> Any:
    """Retry function with exponential backoff"""
    
    logger = logging.getLogger("api_utils")
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
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

def validate_api_response(response: requests.Response, expected_fields: list = None) -> bool:
    """Validate API response has expected structure"""
    try:
        if response.status_code not in [200, 201]:
            return False
        
        if expected_fields:
            data = response.json()
            for field in expected_fields:
                if field not in data:
                    return False
        
        return True
    except Exception:
        return False

def safe_api_call(func: Callable, timeout: int = 30, **kwargs) -> Dict[str, Any]:
    """Make safe API call with timeout and error handling"""
    try:
        result = func(timeout=timeout, **kwargs)
        return {"success": True, "data": result, "error": None}
    except requests.exceptions.Timeout:
        return {"success": False, "data": None, "error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "data": None, "error": "Connection error"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "data": None, "error": f"HTTP error: {e}"}
    except Exception as e:
        return {"success": False, "data": None, "error": f"Unexpected error: {e}"}

def rate_limit_delay(calls_per_minute: int = 60):
    """Add delay to respect rate limits"""
    delay = 60.0 / calls_per_minute
    time.sleep(add_jitter(delay))

def cache_api_response(cache_file: Path, response_data: Dict[str, Any], expiry_hours: int = 24):
    """Cache API response to file with expiry"""
    try:
        cache_data = {
            "timestamp": time.time(),
            "expiry_hours": expiry_hours,
            "data": response_data
        }
        
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        logging.warning(f"Failed to cache response: {e}")

def load_cached_response(cache_file: Path) -> Optional[Dict[str, Any]]:
    """Load cached API response if still valid"""
    try:
        if not cache_file.exists():
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            import json
            cache_data = json.load(f)
        
        # Check if cache is expired
        cache_age = time.time() - cache_data["timestamp"]
        cache_expiry = cache_data["expiry_hours"] * 3600
        
        if cache_age > cache_expiry:
            return None
        
        return cache_data["data"]
    except Exception as e:
        logging.warning(f"Failed to load cached response: {e}")
        return None