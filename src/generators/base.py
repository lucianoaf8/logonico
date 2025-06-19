# src/generators/base.py
"""
Base generator class for all image generation APIs
"""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from ..utils.naming import generate_filename
from ..utils.file_utils import download_image

class GenerationResult:
    """Result of an image generation attempt"""
    
    def __init__(self, success: bool, prompt_id: str, model: str, 
                 file_path: Optional[Path] = None, error: Optional[str] = None,
                 duration: float = 0.0, metadata: Optional[Dict] = None):
        self.success = success
        self.prompt_id = prompt_id
        self.model = model
        self.file_path = file_path
        self.error = error
        self.duration = duration
        self.metadata = metadata or {}
    
    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"GenerationResult({status}, {self.model}, {self.prompt_id})"

class BaseGenerator(ABC):
    """Abstract base class for all image generators"""
    
    def __init__(self, api_key: str, provider_name: str):
        self.api_key = api_key
        self.provider_name = provider_name
        self.logger = logging.getLogger(f"generator.{provider_name}")
        
        if not api_key:
            raise ValueError(f"API key required for {provider_name}")
    
    @abstractmethod
    def generate(self, prompt: str, prompt_id: str, model: str, 
                output_dir: Path, **kwargs) -> GenerationResult:
        """Generate image and save to output_dir"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """Check if model is valid for this provider"""
        pass
    
    def _download_and_save(self, image_url: str, prompt_id: str, model: str, 
                          output_dir: Path, extension: str = "png") -> Optional[Path]:
        """Download image from URL and save with consistent naming"""
        
        filename = generate_filename(prompt_id, model, extension)
        output_path = output_dir / filename
        
        if download_image(image_url, output_path):
            self.logger.info(f"Saved: {filename} ({output_path.stat().st_size / 1024:.1f} KB)")
            return output_path
        else:
            self.logger.error(f"Failed to download image for {prompt_id}")
            return None
    
    def _handle_generation(self, prompt: str, prompt_id: str, model: str,
                          output_dir: Path, generation_func, **kwargs) -> GenerationResult:
        """Common generation handling with timing and error management"""
        
        start_time = time.time()
        
        try:
            self.logger.info(f"[{self.provider_name}] Generating {prompt_id} with {model}")
            
            # Call the specific generation function
            result = generation_func(prompt, prompt_id, model, output_dir, **kwargs)
            
            duration = time.time() - start_time
            
            if result:
                self.logger.info(f"[{self.provider_name}] SUCCESS: {model} | {duration:.2f}s")
                return GenerationResult(
                    success=True,
                    prompt_id=prompt_id, 
                    model=model,
                    file_path=result,
                    duration=duration
                )
            else:
                self.logger.error(f"[{self.provider_name}] FAILED: {model}")
                return GenerationResult(
                    success=False,
                    prompt_id=prompt_id,
                    model=model, 
                    error="Generation returned no result",
                    duration=duration
                )
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            self.logger.error(f"[{self.provider_name}] ERROR: {model} | {error_msg}")
            
            return GenerationResult(
                success=False,
                prompt_id=prompt_id,
                model=model,
                error=error_msg,
                duration=duration
            )
    
    def test_connection(self) -> bool:
        """Test if the API connection is working"""
        try:
            # Simple test - try to get available models or make a minimal API call
            models = self.get_available_models()
            return len(models) > 0
        except Exception as e:
            self.logger.error(f"Connection test failed for {self.provider_name}: {e}")
            return False

# src/generators/together_ai.py
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