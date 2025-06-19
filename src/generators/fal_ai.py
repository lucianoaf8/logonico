# src/generators/fal_ai.py
"""
Fal.ai image generator
"""

import requests
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import BaseGenerator, GenerationResult
from ..core.config import MODEL_CONFIGS

class FalAIGenerator(BaseGenerator):
    """Generator for Fal.ai models"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "fal_ai")
        self.headers = {
            "Authorization": f"Key {api_key}",  # Fal.ai uses "Key" not "Bearer"
            "Content-Type": "application/json"
        }
    
    def get_available_models(self) -> List[str]:
        """Get available Fal.ai models"""
        return list(MODEL_CONFIGS["fal_ai"].keys())
    
    def validate_model(self, model: str) -> bool:
        """Check if model is valid"""
        return model in MODEL_CONFIGS["fal_ai"]
    
    def generate(self, prompt: str, prompt_id: str, model: str, 
                output_dir: Path, **kwargs) -> GenerationResult:
        """Generate image using Fal.ai"""
        
        if not self.validate_model(model):
            return GenerationResult(
                success=False,
                prompt_id=prompt_id,
                model=model,
                error=f"Invalid model: {model}"
            )
        
        return self._handle_generation(
            prompt, prompt_id, model, output_dir, 
            self._generate_fal_ai, **kwargs
        )
    
    def _generate_fal_ai(self, prompt: str, prompt_id: str, model: str,
                        output_dir: Path, **kwargs) -> Optional[Path]:
        """Internal Fal.ai generation logic"""
        
        model_config = MODEL_CONFIGS["fal_ai"][model]
        model_endpoint = model_config["model"]
        
        # Try queue endpoint first (async)
        queue_url = f"https://queue.fal.run/{model_endpoint}"
        
        payload = {
            "prompt": prompt,
            **kwargs
        }
        
        # Submit to queue
        response = requests.post(queue_url, json=payload, headers=self.headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we got a direct response or need to poll
            if "images" in data:
                # Direct response
                image_url = data["images"][0]["url"]
                return self._download_and_save(image_url, prompt_id, model, output_dir)
            
            elif "response_url" in data:
                # Need to poll for results
                result_url = self._poll_fal_queue(data["response_url"])
                if result_url:
                    return self._download_and_save(result_url, prompt_id, model, output_dir)
        
        # Fallback to direct endpoint
        direct_url = f"https://fal.run/{model_endpoint}"
        response = requests.post(direct_url, json=payload, headers=self.headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if "images" in data and data["images"]:
                image_url = data["images"][0]["url"]
                return self._download_and_save(image_url, prompt_id, model, output_dir)
        
        raise Exception(f"Fal.ai generation failed: {response.status_code} {response.text}")
    
    def _poll_fal_queue(self, response_url: str, timeout: int = 120) -> Optional[str]:
        """Poll Fal.ai queue for async results"""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(response_url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for completion
                    if data.get("status") == "COMPLETED" or "images" in data:
                        images = data.get("images", [])
                        if images:
                            return images[0]["url"]
                
                elif response.status_code == 202:
                    # Still processing
                    time.sleep(3)
                    continue
                
                elif response.status_code == 400:
                    # Check if it's "still in progress"
                    try:
                        error_data = response.json()
                        if "still in progress" in error_data.get("detail", "").lower():
                            time.sleep(3)
                            continue
                    except:
                        pass
                    
                    self.logger.warning(f"Fal.ai poll error: {response.status_code}")
                    break
                
                else:
                    self.logger.error(f"Fal.ai poll failed: {response.status_code} {response.text}")
                    break
                    
            except Exception as e:
                self.logger.error(f"Fal.ai polling error: {e}")
                break
        
        self.logger.warning(f"Fal.ai polling timed out after {timeout}s")
        return None
    
    def test_connection(self) -> bool:
        """Test Fal.ai connection"""
        try:
            # Test with a simple model endpoint
            test_url = "https://fal.run/fal-ai/flux/schnell"
            test_payload = {"prompt": "test"}
            
            response = requests.post(test_url, json=test_payload, headers=self.headers, timeout=10)
            
            # Even if generation fails, 200/401 means we can reach the API
            return response.status_code in [200, 400, 401]
        except Exception as e:
            self.logger.error(f"Fal.ai connection test failed: {e}")
            return False