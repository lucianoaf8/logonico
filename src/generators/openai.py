# src/generators/openai.py
"""
OpenAI DALL-E image generator
"""

import openai
from pathlib import Path
from typing import List, Optional

from .base import BaseGenerator, GenerationResult
from ..core.config import MODEL_CONFIGS

class OpenAIGenerator(BaseGenerator):
    """Generator for OpenAI DALL-E models"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "openai")
        self.client = openai.OpenAI(api_key=api_key)
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return list(MODEL_CONFIGS["openai"].keys())
    
    def validate_model(self, model: str) -> bool:
        """Check if model is valid"""
        return model in MODEL_CONFIGS["openai"]
    
    def generate(self, prompt: str, prompt_id: str, model: str, 
                output_dir: Path, **kwargs) -> GenerationResult:
        """Generate image using OpenAI DALL-E"""
        
        if not self.validate_model(model):
            return GenerationResult(
                success=False,
                prompt_id=prompt_id,
                model=model,
                error=f"Invalid model: {model}"
            )
        
        return self._handle_generation(
            prompt, prompt_id, model, output_dir, 
            self._generate_openai, **kwargs
        )
    
    def _generate_openai(self, prompt: str, prompt_id: str, model: str,
                        output_dir: Path, **kwargs) -> Optional[Path]:
        """Internal OpenAI generation logic"""
        
        model_config = MODEL_CONFIGS["openai"][model]
        
        # Build parameters
        params = {
            "model": model_config["model"],
            "prompt": f"logo, minimalist, {prompt}",  # Add prefix for better results
            **model_config["params"]
        }
        
        # Override with any kwargs
        params.update(kwargs)
        
        # Generate image
        response = self.client.images.generate(**params)
        
        # Extract image URL
        image_url = response.data[0].url
        
        # Download and save
        return self._download_and_save(image_url, prompt_id, model, output_dir)
    
    def test_connection(self) -> bool:
        """Test OpenAI connection"""
        try:
            # Try to list models to test API access
            models = self.client.models.list()
            return len(models.data) > 0
        except Exception as e:
            self.logger.error(f"OpenAI connection test failed: {e}")
            return False
