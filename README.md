
# LogoNico Generator

> **Professional AI-powered logo and icon generation system with integrated processing pipeline**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LogoNico is a comprehensive logo and icon generation platform that leverages multiple AI providers to create professional-quality images with an integrated processing pipeline for background removal and format conversion.

## ✨ Features

### 🎨 **Multi-Provider AI Generation**

* **Together AI** - FLUX models (Dev, LoRA, Schnell)
* **Replicate** - Community and official models (Galleri5 Icons, Ideogram V2, Recraft SVG)
* **OpenAI** - DALL-E 3 integration
* **Fal.ai** - Fast inference with multiple model variants

### 🖥️ **Dual Interface**

* **Modern React Web UI** - Interactive gallery with real-time updates
* **Powerful CLI** - Batch processing and automation support

### 🔄 **Integrated Processing Pipeline**

* **AI Background Removal** - Using rembg with multiple model options
* **ICO Conversion** - Multi-size ICO generation for applications
* **Image Optimization** - Size and quality optimization
* **Batch Processing** - Handle multiple images simultaneously

### 🎯 **Advanced Features**

* **Fail-fast Logic** - Skip remaining prompts when rate limits hit
* **Parallel Processing** - Generate multiple images concurrently
* **Real-time Progress** - Live updates and status tracking
* **Consistent Naming** - Organized file naming with metadata
* **Responsive Design** - Resizable panels and mobile-friendly UI

## 🚀 Quick Start

### Prerequisites

* **Python 3.8+**
* **Node.js 16+** (for React UI)
* **API Keys** for at least one provider

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/logonico.git
cd logonico

# Install Python dependencies
pip install -r requirements.txt

# Install React dependencies
cd logonico-ui
npm install
cd ..
```

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
notepad .env  # Windows
nano .env     # Linux/Mac
```

Add your API keys:

```env
TOGETHER_API_KEY=your_together_api_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
OPENAI_API_KEY=your_openai_key_here
FAL_KEY=your_fal_ai_key_here
```

### 3. Test Installation

```bash
# Check system status
python main.py status

# List available models
python main.py list-models
```

### 4. Generate Your First Images

```bash
# Generate with all available models
python main.py generate --all

# Full pipeline with processing
python main.py generate --all --process --remove-bg --create-ico
```

### 5. Launch Web Interface

```bash
# Start Flask backend
python app.py

# In another terminal, start React frontend
cd logonico-ui
npm start
```

Visit `http://localhost:3000` for the web interface!

## 📖 Usage

### CLI Commands

#### System Management

```bash
# Check system status and API keys
python main.py status

# List all available models
python main.py list-models
```

#### Image Generation

```bash
# Generate with all models
python main.py generate --all

# Generate with specific models
python main.py generate --models flux_dev,dalle3,galleri5_icons

# Generate specific prompts only
python main.py generate --all --prompts spark_dialog,magic_wand

# Complete pipeline (recommended)
python main.py generate --all --process --remove-bg --create-ico
```

#### Image Processing

```bash
# Process existing images
python main.py process --remove-bg --create-ico

# Process custom directory
python main.py process --input C:\path\to\images --remove-bg --create-ico
```

### Web Interface

The React web interface provides:

* **Interactive Gallery** - Browse and filter generated images
* **Selection Tools** - Multi-select images for batch operations
* **Real-time Status** - Live generation progress and provider status
* **Resizable Panels** - Customizable layout with drag-to-resize
* **Batch Operations** - Remove backgrounds and convert formats

## 🏗️ Architecture

### Backend (Python)

```
src/
├── core/
│   ├── config.py          # Configuration management
│   ├── models.py          # Model registry and factory
│   └── pipeline.py        # Main generation pipeline
├── generators/
│   ├── base.py            # Abstract base generator
│   ├── together_ai.py     # Together AI implementation
│   ├── replicate.py       # Replicate implementation
│   ├── openai.py          # OpenAI implementation
│   └── fal_ai.py          # Fal.ai implementation
├── processors/
│   ├── background_remover.py  # AI background removal
│   ├── ico_converter.py       # ICO format conversion
│   └── image_optimizer.py     # Image optimization
└── utils/
    ├── naming.py          # File naming conventions
    ├── logging_utils.py   # Structured logging
    └── file_utils.py      # File operations
```

### Frontend (React)

```
logonico-ui/src/
├── components/
│   ├── common/            # Reusable components
│   ├── Layout/            # Layout components
│   ├── Gallery/           # Image gallery
│   ├── Header/            # Application header
│   ├── Sidebar/           # Status and logs
│   └── SelectionPanel/    # Image selection
├── hooks/                 # Custom React hooks
├── services/              # API and utilities
└── styles/                # Styling and themes
```

## 🎨 Customization

### Adding Custom Prompts

Edit `config/prompts.json`:

```json
[
  {
    "id": "my_custom_prompt",
    "title": "Custom Logo Design",
    "prompt": "Modern minimalist logo with clean lines and professional appearance..."
  }
]
```

### Adding New AI Providers

1. Create generator in `src/generators/`
2. Inherit from `BaseGenerator`
3. Implement required methods
4. Add to `MODEL_CONFIGS` in `config.py`
5. Register in `models.py`

### Custom Processing

Add processors in `src/processors/`:

* Implement batch processing methods
* Add to pipeline configuration
* Update CLI and web interface

## 📊 Output Structure

```
output/
├── raw/                   # Original generated images
│   └── spark_dialog_flux_dev_20250619_143022.png
├── processed/             # Background removed images
│   └── spark_dialog_flux_dev_20250619_143022_nobg.png
└── icons/                 # ICO format files
    └── spark_dialog_flux_dev_20250619_143022.ico
```

## 🔧 Configuration

### Environment Variables

```env
# API Keys
TOGETHER_API_KEY=your_key
REPLICATE_API_TOKEN=your_token
OPENAI_API_KEY=your_key
FAL_KEY=your_key

# Processing Settings
DEFAULT_SIZE=1024
MAX_WORKERS=4
TIMEOUT_SECONDS=120
MAX_RETRIES=3
REMOVE_BACKGROUND=true
CREATE_ICO=true

# Logging
LOG_LEVEL=INFO
```

### Model Configuration

Models are configured in `src/core/config.py`:

```python
MODEL_CONFIGS = {
    "together_ai": {
        "flux_dev": {
            "model": "black-forest-labs/FLUX.1-dev",
            "params": {"width": 1024, "height": 1024, "steps": 30}
        }
    }
}
```

## 🚨 Troubleshooting

### Common Issues

#### API Rate Limits

* **Issue** : `429 Rate limit exceeded`
* **Solution** : The system automatically skips remaining prompts for rate-limited models
* **Prevention** : Upgrade API plans or use fewer concurrent requests

#### Memory Issues

* **Issue** : Out of memory during processing
* **Solution** : Reduce `MAX_WORKERS` in `.env`
* **Alternative** : Process images in smaller batches

#### Dependencies

```bash
# Upgrade pip and reinstall
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# React dependencies
cd logonico-ui
npm install --force
```

### Getting Help

* Check logs in `logs/generation.log`
* Run `python main.py status` for system diagnostics
* Verify API keys are valid
* Ensure sufficient disk space in `output/` directory

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/logonico.git
cd logonico

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Install React development tools
cd logonico-ui
npm install
npm install --save-dev @testing-library/react
```

### Running Tests

```bash
# Python tests
pytest tests/

# React tests
cd logonico-ui
npm test
```

### Code Style

```bash
# Python formatting
black src/
flake8 src/

# React formatting
cd logonico-ui
npm run lint
npm run format
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://claude.ai/chat/LICENSE) file for details.

## 🙏 Acknowledgments

* **AI Providers** : Together AI, Replicate, OpenAI, Fal.ai
* **Image Processing** : rembg for background removal
* **UI Framework** : React and styled-components
* **Backend** : Flask and Python ecosystem

## 🔗 API Reference

### REST API Endpoints

#### Images

* `GET /api/images` - List all generated images
* `GET /api/image/<filename>` - Serve individual image file

#### Statistics

* `GET /api/stats` - Generation statistics and provider status

#### Logs

* `GET /api/logs` - Recent generation logs

### CLI Reference

```bash
# Generation
python main.py generate [--all | --models MODEL_LIST] [--prompts PROMPT_LIST] [--process] [--remove-bg] [--create-ico]

# Processing
python main.py process [--input DIRECTORY] [--remove-bg] [--create-ico]

# System
python main.py status
python main.py list-models
```

## 📈 Performance

### Benchmarks

* **Generation Speed** : ~3-5 images/minute (depends on providers)
* **Processing Speed** : ~10-20 images/minute for background removal
* **Memory Usage** : ~500MB base + ~100MB per concurrent generation
* **Storage** : ~1-3MB per generated image

### Optimization Tips

* Use `--models` to limit to fastest providers
* Increase `MAX_WORKERS` for better parallelization
* Use SSD storage for faster I/O
* Monitor API quotas to avoid rate limits

---

## 🌟 Star History

⭐ **If LogoNico helped you create amazing logos, please star this repository!**

---

**Happy Logo Creating! 🎨✨**
