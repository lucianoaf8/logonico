# app.py - LogoNico Flask Web Interface
from flask import Flask, render_template, jsonify, send_file
from pathlib import Path
import json
import re
from datetime import datetime
import os

app = Flask(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
RAW_DIR = OUTPUT_DIR / "raw"
PROCESSED_DIR = OUTPUT_DIR / "processed"
ICONS_DIR = OUTPUT_DIR / "icons"
LOGS_DIR = PROJECT_ROOT / "logs"

def parse_filename(filename):
    """Parse generated image filename to extract metadata"""
    # Pattern: {prompt_id}_{model}_{timestamp}.{ext}
    # Example: circuit_orb_dalle3_20250619_172354.png
    
    stem = Path(filename).stem
    ext = Path(filename).suffix[1:]  # Remove the dot
    
    # Try to match the pattern
    # Split by underscore and look for timestamp pattern
    parts = stem.split('_')
    
    # Find timestamp (pattern: YYYYMMDD_HHMMSS)
    timestamp_idx = -1
    for i, part in enumerate(parts):
        if len(part) == 8 and part.isdigit():  # YYYYMMDD
            if i + 1 < len(parts) and len(parts[i + 1]) == 6 and parts[i + 1].isdigit():  # HHMMSS
                timestamp_idx = i
                break
    
    if timestamp_idx > 0:
        prompt_parts = parts[:timestamp_idx-1]  # Everything before model
        model_part = parts[timestamp_idx-1]     # Model name
        timestamp_parts = parts[timestamp_idx:timestamp_idx+2]  # Date and time
        
        prompt_id = '_'.join(prompt_parts) if prompt_parts else 'unknown'
        model = model_part
        timestamp = '_'.join(timestamp_parts)
        
        # Try to parse timestamp
        try:
            dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
            created_at = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            created_at = timestamp
    else:
        # Fallback parsing
        prompt_id = parts[0] if parts else 'unknown'
        model = parts[1] if len(parts) > 1 else 'unknown'
        created_at = 'unknown'
    
    # Determine provider from model name
    provider = 'unknown'
    if 'dalle' in model.lower():
        provider = 'openai'
    elif 'flux' in model.lower():
        if 'dev' in model.lower() or 'schnell' in model.lower() or 'lora' in model.lower():
            provider = 'together_ai'
        else:
            provider = 'fal_ai'
    elif 'galleri5' in model.lower():
        provider = 'replicate'
    elif 'ideogram' in model.lower():
        provider = 'replicate'
    elif 'recraft' in model.lower():
        provider = 'replicate'
    
    return {
        'prompt_id': prompt_id,
        'model': model,
        'provider': provider,
        'created_at': created_at,
        'extension': ext,
        'filename': filename
    }

def get_file_size(filepath):
    """Get file size in MB"""
    try:
        size_bytes = filepath.stat().st_size
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return 0

@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')

@app.route('/api/images')
def api_images():
    """Get all generated images with metadata"""
    images = []
    
    if RAW_DIR.exists():
        for img_file in RAW_DIR.iterdir():
            if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                metadata = parse_filename(img_file.name)
                
                images.append({
                    'id': img_file.stem,
                    'filename': img_file.name,
                    'url': f'/api/image/{img_file.name}',
                    'thumbnail_url': f'/api/image/{img_file.name}',  # Same for now
                    'prompt_id': metadata['prompt_id'],
                    'model': metadata['model'],
                    'provider': metadata['provider'],
                    'created_at': metadata['created_at'],
                    'extension': metadata['extension'],
                    'size_mb': get_file_size(img_file),
                    'status': 'success'  # All existing images are successful
                })
    
    # Sort by creation time (newest first)
    images.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(images)

@app.route('/api/image/<filename>')
def serve_image(filename):
    """Serve individual image files"""
    img_path = RAW_DIR / filename
    if img_path.exists():
        return send_file(img_path)
    else:
        return "Image not found", 404

@app.route('/api/stats')
def api_stats():
    """Get generation statistics"""
    images = []
    if RAW_DIR.exists():
        images = list(RAW_DIR.glob('*.*'))
    
    # Count by provider
    provider_counts = {}
    model_counts = {}
    prompt_counts = {}
    
    for img_file in images:
        if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
            metadata = parse_filename(img_file.name)
            
            provider = metadata['provider']
            model = metadata['model']
            prompt = metadata['prompt_id']
            
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            model_counts[model] = model_counts.get(model, 0) + 1
            prompt_counts[prompt] = prompt_counts.get(prompt, 0) + 1
    
    return jsonify({
        'total_images': len(images),
        'providers': provider_counts,
        'models': model_counts,
        'prompts': prompt_counts,
        'success_rate': 100,  # All existing images are successful
        'status': 'complete'  # Since we're viewing completed generation
    })

@app.route('/api/logs')
def api_logs():
    """Get recent logs"""
    logs = []
    
    # Try to read the latest log file
    log_file = LOGS_DIR / "generation.log"
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Get last 20 lines
                for line in lines[-20:]:
                    if line.strip():
                        # Parse log format: timestamp | name | level | message
                        parts = line.strip().split(' | ', 3)
                        if len(parts) >= 4:
                            timestamp = parts[0]
                            level = parts[2]
                            message = parts[3]
                            
                            # Determine status icon
                            if 'SUCCESS' in message or level == 'INFO':
                                status = '✅'
                            elif 'ERROR' in message or level == 'ERROR':
                                status = '❌'
                            elif 'WARNING' in message or level == 'WARNING':
                                status = '⚠️'
                            else:
                                status = 'ℹ️'
                            
                            logs.append({
                                'time': timestamp.split()[1][:8],  # Just HH:MM:SS
                                'status': status,
                                'message': message[:80] + '...' if len(message) > 80 else message
                            })
        except Exception as e:
            logs.append({
                'time': '00:00:00',
                'status': '❌',
                'message': f'Failed to read logs: {e}'
            })
    
    return jsonify(logs)

if __name__ == '__main__':
    # Ensure directories exist
    for dir_path in [OUTPUT_DIR, RAW_DIR, PROCESSED_DIR, ICONS_DIR, LOGS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    print("=== LogoNico Web Interface ===")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Images found: {len(list(RAW_DIR.glob('*.*'))) if RAW_DIR.exists() else 0}")
    print("Starting server at http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)