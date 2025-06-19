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

def clean_directory(directory: Path, pattern: str = "*", keep_count: int = 0):
    """Clean directory keeping only the latest N files"""
    if not directory.exists():
        return
    
    files = list(directory.glob(pattern))
    if len(files) <= keep_count:
        return
    
    # Sort by modification time (newest first)
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # Remove excess files
    for file_to_remove in files[keep_count:]:
        try:
            file_to_remove.unlink()
        except Exception as e:
            print(f"Failed to remove {file_to_remove}: {e}")

def save_json(data: Dict[str, Any], file_path: Path) -> bool:
    """Save data to JSON file"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Failed to save JSON to {file_path}: {e}")
        return False

def load_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load JSON from {file_path}: {e}")
        return None
