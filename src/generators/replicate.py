# src/generators/replicate.py
"""
Replicate image generator (community and official models)
"""

import requests
import time
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import BaseGenerator, GenerationResult
from ..core.config import MODEL_CONFIGS, Config

class ReplicateGenerator(BaseGenerator):
    """Generator for Replicate models"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "replicate")
        self.base_url = "https://api.replicate.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.version_cache_file = Config.CACHE_DIR / "replicate_versions.json"
        self.version_cache = self._load_version_cache()
    
    def get_available_models(self) -> List[str]:
        """Get available Replicate models"""
        return list(MODEL_CONFIGS["replicate"].keys())
    
    def validate_model(self, model: str) -> bool:
        """Check if model is valid"""
        return model in MODEL_CONFIGS["replicate"]
    
    def generate(self, prompt: str, prompt_id: str, model: str, 
                output_dir: Path, **kwargs) -> GenerationResult:
        """Generate image using Replicate"""
        
        if not self.validate_model(model):
            return GenerationResult(
                success=False,
                prompt_id=prompt_id,
                model=model,
                error=f"Invalid model: {model}"
            )
        
        return self._handle_generation(
            prompt, prompt_id, model, output_dir, 
            self._generate_replicate, **kwargs
        )
    
    def _generate_replicate(self, prompt: str, prompt_id: str, model: str,
                           output_dir: Path, **kwargs) -> Optional[Path]:
        """Internal Replicate generation logic"""
        
        model_config = MODEL_CONFIGS["replicate"][model]
        model_name = model_config["model"]
        model_type = model_config["type"]
        
        # Create prediction
        if model_type == "official":
            prediction = self._create_official_prediction(model_name, prompt, **kwargs)
        else:
            prediction = self._create_community_prediction(model_name, prompt, **kwargs)
        
        if not prediction:
            raise Exception("Failed to create prediction")
        
        # Wait for completion
        result_url = self._wait_for_completion(prediction["id"])
        
        if not result_url:
            raise Exception("Prediction failed or timed out")
        
        # Determine file extension from URL
        extension = "png"
        if result_url.lower().endswith('.svg'):
            extension = "svg"
        elif result_url.lower().endswith(('.jpg', '.jpeg')):
            extension = "jpg"
        
        # Download and save
        return self._download_and_save(result_url, prompt_id, model, output_dir, extension)
    
    def _create_official_prediction(self, model_name: str, prompt: str, **kwargs) -> Optional[Dict]:
        """Create prediction for official models"""
        url = f"{self.base_url}/models/{model_name}/predictions"
        
        payload = {
            "input": {
                "prompt": prompt,
                **kwargs
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=30)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            self.logger.error(f"Official model prediction failed: {response.status_code} {response.text}")
            return None
    
    def _create_community_prediction(self, model_name: str, prompt: str, **kwargs) -> Optional[Dict]:
        """Create prediction for community models with version resolution"""
        
        # Get model version
        version = self._resolve_model_version(model_name)
        if not version:
            raise Exception(f"Could not resolve version for {model_name}")
        
        url = f"{self.base_url}/predictions"
        
        payload = {
            "version": version,
            "input": {
                "prompt": prompt,
                **kwargs
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=30)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            self.logger.error(f"Community model prediction failed: {response.status_code} {response.text}")
            return None
    
    def _resolve_model_version(self, model_name: str) -> Optional[str]:
        """Resolve model version with caching"""
        
        # Check cache first
        if model_name in self.version_cache:
            return self.version_cache[model_name]
        
        # Fetch latest version
        url = f"{self.base_url}/models/{model_name}/versions?limit=1"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    version_id = data["results"][0]["id"]
                    full_version = f"{model_name}:{version_id}"
                    
                    # Cache the result
                    self.version_cache[model_name] = full_version
                    self._save_version_cache()
                    
                    return full_version
            else:
                self.logger.error(f"Failed to get version for {model_name}: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error resolving version for {model_name}: {e}")
        
        return None
    
    def _wait_for_completion(self, prediction_id: str, timeout: int = 120) -> Optional[str]:
        """Wait for prediction to complete and return image URL"""
        
        start_time = time.time()
        url = f"{self.base_url}/predictions/{prediction_id}"
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to check prediction status: {response.status_code}")
                    return None
                
                data = response.json()
                status = data.get("status")
                
                if status == "succeeded":
                    output = data.get("output")
                    if output:
                        # Handle different output formats
                        if isinstance(output, list):
                            return output[0]
                        elif isinstance(output, str):
                            return output
                        else:
                            self.logger.error(f"Unexpected output format: {type(output)}")
                            return None
                
                elif status in ["failed", "canceled"]:
                    error = data.get("error", "Unknown error")
                    self.logger.error(f"Prediction failed: {error}")
                    return None
                
                # Still processing, wait and retry
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error checking prediction: {e}")
                return None
        
        self.logger.error(f"Prediction timed out after {timeout}s")
        return None
    
    def _load_version_cache(self) -> Dict[str, str]:
        """Load version cache from file"""
        try:
            if self.version_cache_file.exists():
                with open(self.version_cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load version cache: {e}")
        
        return {}
    
    def _save_version_cache(self):
        """Save version cache to file"""
        try:
            self.version_cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.version_cache_file, 'w') as f:
                json.dump(self.version_cache, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save version cache: {e}")
    
    def test_connection(self) -> bool:
        """Test Replicate connection"""
        try:
            url = f"{self.base_url}/models"
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Replicate connection test failed: {e}")
            return False