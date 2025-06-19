# src/processors/ico_converter.py
"""
ICO file converter using Pillow
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image

class ICOConverter:
    """Convert images to ICO format with multiple sizes"""
    
    def __init__(self, ico_sizes: List[int] = None):
        self.ico_sizes = ico_sizes or [16, 32, 48, 64, 128, 256]
        self.logger = logging.getLogger("processor.ico_converter")
    
    def convert_image(self, input_path: Path, output_path: Path) -> bool:
        """Convert single image to ICO format"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGBA for transparency support
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Create different sizes
                resized_images = []
                
                for size in self.ico_sizes:
                    # Resize maintaining aspect ratio
                    resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    resized_images.append(resized)
                
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save as ICO with multiple sizes
                img.save(
                    output_path, 
                    format='ICO', 
                    sizes=[(size, size) for size in self.ico_sizes],
                    append_images=resized_images[1:] if len(resized_images) > 1 else None
                )
                
            self.logger.info(f"ICO created: {input_path.name} -> {output_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to convert {input_path.name} to ICO: {e}")
            return False
    
    def convert_batch(self, input_paths: List[Path], output_dir: Path) -> List[Path]:
        """Convert multiple images to ICO format"""
        
        successful_outputs = []
        
        for input_path in input_paths:
            # Generate output filename
            output_filename = f"{input_path.stem}.ico"
            output_path = output_dir / output_filename
            
            if self.convert_image(input_path, output_path):
                successful_outputs.append(output_path)
        
        self.logger.info(f"ICO conversion complete: {len(successful_outputs)}/{len(input_paths)} successful")
        return successful_outputs
    
    def verify_ico(self, ico_path: Path) -> bool:
        """Verify ICO file is valid and report sizes"""
        try:
            with Image.open(ico_path) as img:
                # ICO files can contain multiple images
                sizes_found = []
                
                try:
                    # Try to get all sizes
                    for i in range(100):  # Arbitrary limit
                        img.seek(i)
                        sizes_found.append(img.size)
                except EOFError:
                    # Normal - reached end of ICO frames
                    pass
                
                self.logger.info(f"ICO verified: {ico_path.name} contains {len(sizes_found)} sizes: {sizes_found}")
                return True
                
        except Exception as e:
            self.logger.error(f"ICO verification failed for {ico_path.name}: {e}")
            return False
    
    def get_ico_info(self, ico_path: Path) -> dict:
        """Get detailed information about ICO file"""
        info = {
            "valid": False,
            "sizes": [],
            "file_size_kb": 0,
            "format": None
        }
        
        try:
            if ico_path.exists():
                info["file_size_kb"] = ico_path.stat().st_size / 1024
                
                with Image.open(ico_path) as img:
                    info["format"] = img.format
                    
                    # Get all sizes in the ICO
                    try:
                        for i in range(100):
                            img.seek(i)
                            info["sizes"].append(img.size)
                    except EOFError:
                        pass
                    
                    info["valid"] = len(info["sizes"]) > 0
                    
        except Exception as e:
            self.logger.error(f"Failed to get ICO info for {ico_path}: {e}")
        
        return info
