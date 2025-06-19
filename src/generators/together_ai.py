"""
Together AI image generator (FLUX models, etc.)
"""

import requests
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import BaseGenerator, GenerationResult
from ..core.config import MODEL_CONFIGS

class TogetherAIGenerator(BaseGenerator):
    """Generator for Together AI models (FLUX, etc.)"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "together_ai")
        self.base_url = "https://api.together.xyz/v1/images/generations"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_available_models(self) -> List[str]:
        """Get available Together AI models"""
        return list(MODEL_CONFIGS["together_ai"].keys())
    
    def validate_model(self, model: str) -> bool:
        """Check if model is valid"""
        return model in MODEL_CONFIGS["together_ai"]
    
    def generate(self, prompt: str, prompt_id: str, model: str, 
                output_dir: Path, **kwargs) -> GenerationResult:
        """Generate image using Together AI"""
        
        if not self.validate_model(model):
            return GenerationResult(
                success=False,
                prompt_id=prompt_id,
                model=model,
                error=f"Invalid model: {model}"
            )
        
        return self._handle_generation(
            prompt, prompt_id, model, output_dir, 
            self._generate_together_ai, **kwargs
        )
    
    def _generate_together_ai(self, prompt: str, prompt_id: str, model: str,
                             output_dir: Path, **kwargs) -> Optional[Path]:
        """Internal Together AI generation logic"""
        
        model_config = MODEL_CONFIGS["together_ai"][model]
        
        # Build request payload
        payload = {
            "model": model_config["model"],
            "prompt": prompt,
            **model_config["params"]
        }
        
        # Override with any kwargs
        payload.update(kwargs)
        
        # Make API request
        response = requests.post(
            self.base_url,
            json=payload,
            headers=self.headers,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"API error {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Extract image URL
        if "data" not in data or not data["data"]:
            raise Exception("No image data in response")
        
        image_url = data["data"][0]["url"]
        
        # Download and save
        return self._download_and_save(image_url, prompt_id, model, output_dir)
    
    def test_connection(self) -> bool:
        """Test Together AI connection"""
        try:
            # Make a simple request to check API access
            test_payload = {
                "model": "black-forest-labs/FLUX.1-schnell",
                "prompt": "test image",
                "width": 512,
                "height": 512,
                "steps": 1,
                "n": 1
            }
            
            response = requests.post(
                self.base_url,
                json=test_payload,
                headers=self.headers,
                timeout=10
            )
            
            # Even if generation fails, 200 means API access is working
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Together AI connection test failed: {e}")
            return False