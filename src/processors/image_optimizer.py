# src/processors/image_optimizer.py
"""
Image optimization processor
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from PIL import Image, ImageEnhance

class ImageOptimizer:
    """Optimize images for size and quality"""
    
    def __init__(self):
        self.logger = logging.getLogger("processor.image_optimizer")
    
    def optimize_image(self, input_path: Path, output_path: Path, 
                      max_size_kb: int = 500, quality: int = 85, 
                      enhance: bool = False) -> bool:
        """Optimize single image for file size and optionally enhance"""
        try:
            with Image.open(input_path) as img:
                original_size = input_path.stat().st_size / 1024
                
                # Apply enhancements if requested
                if enhance:
                    img = self._enhance_image(img)
                
                # Convert to RGB if needed (for JPEG optimization)
                if img.mode in ('RGBA', 'LA'):
                    # Keep RGBA for PNG, convert to RGB for JPEG
                    if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                        # Create white background for JPEG
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Determine format and optimize
                if output_path.suffix.lower() == '.png':
                    img.save(output_path, 'PNG', optimize=True)
                elif output_path.suffix.lower() in ['.jpg', '.jpeg']:
                    img.save(output_path, 'JPEG', quality=quality, optimize=True)
                else:
                    # Default to PNG
                    output_path = output_path.with_suffix('.png')
                    img.save(output_path, 'PNG', optimize=True)
                
                # Check file size
                file_size_kb = output_path.stat().st_size / 1024
                compression_ratio = (original_size - file_size_kb) / original_size * 100
                
                self.logger.info(f"Optimized: {input_path.name} -> {output_path.name} "
                               f"({original_size:.1f} KB -> {file_size_kb:.1f} KB, "
                               f"{compression_ratio:.1f}% reduction)")
                
                # If still too large, try reducing quality/size
                if file_size_kb > max_size_kb and output_path.suffix.lower() in ['.jpg', '.jpeg']:
                    self._reduce_quality(output_path, max_size_kb, quality)
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to optimize {input_path.name}: {e}")
            return False
    
    def _enhance_image(self, img: Image.Image) -> Image.Image:
        """Apply enhancements to improve image quality"""
        try:
            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # Enhance sharpness slightly
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            # Enhance color slightly
            if img.mode in ('RGB', 'RGBA'):
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.05)
            
            return img
        except Exception as e:
            self.logger.warning(f"Failed to enhance image: {e}")
            return img
    
    def _reduce_quality(self, image_path: Path, max_size_kb: int, initial_quality: int):
        """Reduce JPEG quality to meet size requirements"""
        try:
            with Image.open(image_path) as img:
                quality = initial_quality
                
                while quality > 30:  # Don't go below 30% quality
                    quality -= 10
                    img.save(image_path, 'JPEG', quality=quality, optimize=True)
                    
                    file_size_kb = image_path.stat().st_size / 1024
                    if file_size_kb <= max_size_kb:
                        self.logger.info(f"Reduced quality to {quality}% for size optimization")
                        break
                        
        except Exception as e:
            self.logger.warning(f"Failed to reduce quality for {image_path.name}: {e}")
    
    def resize_image(self, input_path: Path, output_path: Path, 
                    target_size: Tuple[int, int], maintain_aspect: bool = True) -> bool:
        """Resize image to target dimensions"""
        try:
            with Image.open(input_path) as img:
                if maintain_aspect:
                    img.thumbnail(target_size, Image.Resampling.LANCZOS)
                else:
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(output_path, optimize=True)
                
            self.logger.info(f"Resized: {input_path.name} -> {output_path.name} to {img.size}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resize {input_path.name}: {e}")
            return False
    
    def batch_optimize(self, input_paths: List[Path], output_dir: Path, **kwargs) -> List[Path]:
        """Optimize multiple images"""
        
        successful_outputs = []
        
        for input_path in input_paths:
            output_path = output_dir / input_path.name
            
            if self.optimize_image(input_path, output_path, **kwargs):
                successful_outputs.append(output_path)
        
        self.logger.info(f"Optimization complete: {len(successful_outputs)}/{len(input_paths)} successful")
        return successful_outputs
    
    def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """Analyze image properties"""
        analysis = {
            "valid": False,
            "size": (0, 0),
            "mode": None,
            "format": None,
            "file_size_kb": 0,
            "has_transparency": False,
            "color_count": 0
        }
        
        try:
            if image_path.exists():
                analysis["file_size_kb"] = image_path.stat().st_size / 1024
                
                with Image.open(image_path) as img:
                    analysis["valid"] = True
                    analysis["size"] = img.size
                    analysis["mode"] = img.mode
                    analysis["format"] = img.format
                    analysis["has_transparency"] = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                    
                    # Count colors (approximate)
                    try:
                        if img.mode in ('RGB', 'RGBA'):
                            colors = img.convert('RGB').getcolors(maxcolors=256*256*256)
                            analysis["color_count"] = len(colors) if colors else "256+"
                        else:
                            analysis["color_count"] = len(img.getcolors(maxcolors=256)) if img.getcolors(maxcolors=256) else "256+"
                    except:
                        analysis["color_count"] = "Unknown"
                        
        except Exception as e:
            self.logger.error(f"Failed to analyze {image_path}: {e}")
        
        return analysis
    
    def create_thumbnail(self, input_path: Path, output_path: Path, 
                        size: Tuple[int, int] = (128, 128)) -> bool:
        """Create thumbnail of image"""
        try:
            with Image.open(input_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save as PNG to preserve quality
                img.save(output_path, 'PNG', optimize=True)
                
            self.logger.info(f"Thumbnail created: {input_path.name} -> {output_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create thumbnail for {input_path.name}: {e}")
            return False