# app.py - LogoNico Flask Web Interface
from flask import Flask, render_template, jsonify, send_file, Response, stream_with_context, request
from pathlib import Path
import json
import re
from datetime import datetime
import os
import shutil
import threading
from flask_cors import CORS
from src.utils.progress_utils import read_progress
from src.core.pipeline import GenerationPipeline
from src.core.models import model_registry
import time, os

app = Flask(__name__)
CORS(app)

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

@app.route('/api/progress')
def api_progress():
    """Return current generation progress"""
    return jsonify(read_progress())


@app.route('/api/logs/stream')
def api_logs_stream():
    """Server-Sent Events stream of live log lines"""
    def generate():
        log_file = LOGS_DIR / "generation.log"
        log_file.parent.mkdir(exist_ok=True)
        # open file, seek to end so we only stream new lines
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line.strip()}\n\n"
                else:
                    # heartbeat every 15s
                    yield "data: \n\n"
                    time.sleep(1)
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


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

@app.route('/api/image/<filename>/delete', methods=['POST'])
def delete_image(filename):
    """Move image to trash folder instead of deleting"""
    import shutil
    
    # Create trash directory if it doesn't exist
    trash_dir = OUTPUT_DIR / "trash"
    trash_dir.mkdir(exist_ok=True)
    
    source_path = RAW_DIR / filename
    if not source_path.exists():
        return jsonify({'error': 'Image not found'}), 404
    
    try:
        # Move to trash with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trash_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        trash_path = trash_dir / trash_filename
        
        shutil.move(str(source_path), str(trash_path))
        
        # Also move processed versions if they exist
        processed_path = PROCESSED_DIR / filename
        if processed_path.exists():
            processed_trash_path = trash_dir / f"processed_{trash_filename}"
            shutil.move(str(processed_path), str(processed_trash_path))
        
        # Also move icon versions if they exist
        ico_filename = filename.rsplit('.', 1)[0] + '.ico'
        ico_path = ICONS_DIR / ico_filename
        if ico_path.exists():
            ico_trash_path = trash_dir / f"icon_{ico_filename.rsplit('.', 1)[0]}_{timestamp}.ico"
            shutil.move(str(ico_path), str(ico_trash_path))
        
        return jsonify({'success': True, 'message': f'Image moved to trash as {trash_filename}'})
    
    except Exception as e:
        return jsonify({'error': f'Failed to delete image: {str(e)}'}), 500

# ================================
# Workflow Management Endpoints
# ================================

@app.route('/api/workflow/models')
def get_available_models():
    """Get list of available models"""
    try:
        # Initialize model registry to get available models
        model_registry.initialize()
        models = []
        for provider, generator in model_registry.get_all_generators().items():
            if generator:  # If generator is working
                for model in generator.get_available_models():
                    models.append(f"{provider}:{model}")
        return jsonify(models)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/prompt-files')
def get_prompt_files():
    """Get list of available prompt files"""
    try:
        config_dir = PROJECT_ROOT / "config"
        prompt_files = []
        if config_dir.exists():
            for file in config_dir.glob("*.json"):
                if file.stem != "prompts":  # Exclude default
                    prompt_files.append(file.name)
        return jsonify(prompt_files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/prompts/<filename>')
def get_prompts_from_file(filename):
    """Get prompts from a specific prompt file"""
    try:
        if filename == "default":
            file_path = PROJECT_ROOT / "config" / "prompts.json"
        else:
            file_path = PROJECT_ROOT / "config" / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        return jsonify(prompts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/archive', methods=['POST'])
def archive_current_images():
    """Archive current images before starting new workflow"""
    try:
        # Create archive directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = OUTPUT_DIR / "archive" / timestamp
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archived_count = 0
        
        # Archive raw images
        if RAW_DIR.exists():
            for img_file in RAW_DIR.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                    shutil.move(str(img_file), str(archive_dir / img_file.name))
                    archived_count += 1
        
        # Archive processed images
        if PROCESSED_DIR.exists():
            processed_archive = archive_dir / "processed"
            processed_archive.mkdir(exist_ok=True)
            for img_file in PROCESSED_DIR.iterdir():
                if img_file.is_file():
                    shutil.move(str(img_file), str(processed_archive / img_file.name))
        
        # Archive icon files
        if ICONS_DIR.exists():
            icons_archive = archive_dir / "icons"
            icons_archive.mkdir(exist_ok=True)
            for img_file in ICONS_DIR.iterdir():
                if img_file.is_file():
                    shutil.move(str(img_file), str(icons_archive / img_file.name))
        
        return jsonify({
            'success': True, 
            'archived_count': archived_count,
            'archive_path': str(archive_dir)
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to archive images: {str(e)}'}), 500

@app.route('/api/workflow/start', methods=['POST'])
def start_workflow():
    """Start a new generation workflow"""
    try:
        config = request.get_json()
        
        # Parse configuration
        models = None
        if config.get('models') == 'specific' and config.get('specificModels'):
            models = config['specificModels']
        
        prompts = None
        if config.get('prompts') == 'specific' and config.get('specificPrompts'):
            prompts = config['specificPrompts']
        
        remove_bg = config.get('removeBackground', True)
        create_ico = config.get('createICO', True)
        
        # Start workflow in background thread
        def run_workflow():
            try:
                pipeline = GenerationPipeline()
                if pipeline.initialize():
                    pipeline.run_complete_pipeline(
                        models=models,
                        prompts=prompts,
                        remove_bg=remove_bg,
                        create_ico=create_ico
                    )
            except Exception as e:
                print(f"Workflow execution error: {e}")
        
        # Start workflow in background
        workflow_thread = threading.Thread(target=run_workflow, daemon=True)
        workflow_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Workflow started successfully',
            'config': config
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to start workflow: {str(e)}'}), 500

# ================================
# Image Processing Endpoints
# ================================

@app.route('/api/images/download', methods=['POST'])
def download_selected_images():
    """Create and download a ZIP file containing selected images"""
    try:
        data = request.get_json()
        image_ids = data.get('imageIds', [])
        
        if not image_ids:
            return jsonify({'error': 'No images selected'}), 400
        
        import zipfile
        import io
        
        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Get all images and filter by selected IDs
            if RAW_DIR.exists():
                for img_file in RAW_DIR.iterdir():
                    if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                        # Check if this image ID is in the selected list
                        img_id = img_file.stem
                        if img_id in image_ids:
                            # Add image to ZIP
                            zip_file.write(img_file, img_file.name)
            
            # Also include processed versions if they exist
            if PROCESSED_DIR.exists():
                processed_folder_added = False
                for img_file in PROCESSED_DIR.iterdir():
                    if img_file.is_file():
                        # Check if this corresponds to a selected image
                        img_id = img_file.stem
                        if img_id in image_ids:
                            if not processed_folder_added:
                                processed_folder_added = True
                            zip_file.write(img_file, f"processed/{img_file.name}")
            
            # Also include ICO versions if they exist
            if ICONS_DIR.exists():
                icons_folder_added = False
                for img_file in ICONS_DIR.iterdir():
                    if img_file.is_file() and img_file.suffix.lower() == '.ico':
                        # Check if this corresponds to a selected image
                        img_id = img_file.stem
                        if img_id in image_ids:
                            if not icons_folder_added:
                                icons_folder_added = True
                            zip_file.write(img_file, f"icons/{img_file.name}")
        
        zip_buffer.seek(0)
        
        return send_file(
            io.BytesIO(zip_buffer.read()),
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'selected-images-{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to create download: {str(e)}'}), 500

@app.route('/api/images/remove-background', methods=['POST'])
def remove_background_selected():
    """Remove background from selected images"""
    try:
        data = request.get_json()
        image_ids = data.get('imageIds', [])
        
        if not image_ids:
            return jsonify({'error': 'No images selected'}), 400
        
        # Get selected image files
        selected_files = []
        if RAW_DIR.exists():
            for img_file in RAW_DIR.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    if img_file.stem in image_ids:
                        selected_files.append(img_file)
        
        if not selected_files:
            return jsonify({'error': 'No valid images found for processing'}), 400
        
        # Initialize background remover
        pipeline = GenerationPipeline()
        pipeline.initialize()
        
        if not pipeline.background_remover:
            return jsonify({'error': 'Background remover not available'}), 500
        
        # Process images
        processed_files = pipeline.background_remover.process_batch(selected_files, PROCESSED_DIR)
        
        return jsonify({
            'success': True,
            'processed': len(processed_files),
            'message': f'Background removed from {len(processed_files)} images'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to remove background: {str(e)}'}), 500

@app.route('/api/images/convert-ico', methods=['POST'])
def convert_to_ico_selected():
    """Convert selected images to ICO format"""
    try:
        data = request.get_json()
        image_ids = data.get('imageIds', [])
        
        if not image_ids:
            return jsonify({'error': 'No images selected'}), 400
        
        # Get selected image files (prefer processed versions if available)
        selected_files = []
        
        # Check processed directory first
        if PROCESSED_DIR.exists():
            for img_file in PROCESSED_DIR.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    if img_file.stem in image_ids:
                        selected_files.append(img_file)
        
        # Fill in from raw directory for any missing images
        selected_ids_found = {f.stem for f in selected_files}
        if RAW_DIR.exists():
            for img_file in RAW_DIR.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    if img_file.stem in image_ids and img_file.stem not in selected_ids_found:
                        selected_files.append(img_file)
        
        if not selected_files:
            return jsonify({'error': 'No valid images found for conversion'}), 400
        
        # Initialize ICO converter
        pipeline = GenerationPipeline()
        pipeline.initialize()
        
        if not pipeline.ico_converter:
            return jsonify({'error': 'ICO converter not available'}), 500
        
        # Convert images
        ico_files = pipeline.ico_converter.convert_batch(selected_files, ICONS_DIR)
        
        return jsonify({
            'success': True,
            'converted': len(ico_files),
            'message': f'{len(ico_files)} images converted to ICO format'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to convert to ICO: {str(e)}'}), 500

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