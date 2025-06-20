# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LogoNico is a professional AI-powered logo and icon generation system with dual interfaces: a Python CLI and React web UI. It supports multiple AI providers (Together AI, Replicate, OpenAI, Fal.ai) with automated background removal and format conversion.

## Development Commands

### Backend Development
```bash
# Setup
pip install -r requirements.txt

# Configure API keys (required)
cp .env.example .env  # Edit with your API keys

# Check system status
python main.py status

# Generate images
python main.py generate --all
python main.py generate --all --process --remove-bg --create-ico

# Start Flask web server
python app.py  # Runs on http://localhost:5000
```

### Frontend Development
```bash
cd logonico-ui
npm install
npm start      # Development server at http://localhost:3000
npm run build  # Production build
npm test       # Run tests
```

### Full System
Start both backend and frontend simultaneously for full web UI functionality.

## Architecture Overview

### Backend (Python)
- **Framework**: Flask web server + CLI interface
- **Pattern**: Plugin-based generator system with abstract `BaseGenerator` class
- **Pipeline**: Fail-fast generation with parallel processing via `ThreadPoolExecutor`
- **Configuration**: Environment-driven with centralized config in `src/core/config.py`

### Frontend (React)
- **State Management**: Context-based with custom hooks for API integration
- **UI Architecture**: Three-panel layout (sidebar, gallery, selection) with resizable panels
- **Styling**: CSS-in-JS with custom CSS variables for theming

### Key Components

**Generator System** (`src/generators/`):
- Abstract `BaseGenerator` with provider implementations
- `ModelRegistry` factory for managing generators
- Rate limit detection and graceful degradation

**Processing Pipeline** (`src/processors/`):
- Background removal using rembg
- ICO file generation with multiple sizes
- Image optimization

**Configuration** (`src/core/config.py`):
- Centralized model and provider configuration
- Environment variable management
- Prompt templates from `config/prompts.json`

## Required Environment Variables

At least one AI provider API key is required:
- `TOGETHER_API_KEY` - Together AI (primary)
- `REPLICATE_API_TOKEN` - Replicate
- `OPENAI_API_KEY` - OpenAI DALL-E 3
- `FAL_KEY` - Fal.ai

Optional configuration:
- `MAX_WORKERS=4` - Parallel generation workers
- `LOG_LEVEL=INFO` - Logging verbosity
- `REMOVE_BACKGROUND=true` - Auto background removal
- `CREATE_ICO=true` - Auto ICO conversion

## Development Patterns

1. **Adding New Generators**: Extend `BaseGenerator` in `src/generators/` and register in `ModelRegistry`
2. **Adding Processors**: Implement in `src/processors/` following existing patterns
3. **Frontend State**: Use custom hooks in `src/hooks/` for API integration
4. **Configuration**: Add new models to `config/prompts.json` and update `config.py`

## File Organization

- Output organized in `output/` with subdirectories: `raw/`, `processed/`, `icons/`
- Standardized naming: `prompt_id_model_timestamp.ext`
- Logs in `logs/` directory with structured JSON format
- Cache in `cache/` for API responses

## Testing and Quality

Run `python main.py status` to verify system configuration and API connectivity before development.