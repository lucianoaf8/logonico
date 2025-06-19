# Logo/Icon Generator (Windows)

Professional logo and icon generation system using multiple AI models with integrated processing pipeline.

## Quick Start (Windows)

### Option 1: Automatic Setup
1. **Download setup script**: Save `setup_windows.bat` to your desired folder
2. **Run setup**: Double-click `setup_windows.bat` or run in Command Prompt
3. **Edit API keys**: The script will open .env file for you to add your keys
4. **Start generating**: Use the commands below

### Option 2: Manual Setup
1. **Create project**:
   ```cmd
   python complete_setup.py
   cd logo-icon-generator
   ```

2. **Configure**:
   ```cmd
   copy .env.example .env
   notepad .env
   ```
   Add your API keys to the .env file

3. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Test setup**:
   ```cmd
   python main.py status
   ```

## Commands (Windows)

### Check System
```cmd
python main.py status                    # Check API keys and models
python main.py list-models              # List all available models
```

### Generate Images
```cmd
# Generate with all available models
python main.py generate --all

# Generate with specific models  
python main.py generate --models flux_dev,dalle3

# Generate specific prompts
python main.py generate --all --prompts spark_dialog,magic_wand

# Full pipeline (generate + background removal + ICO conversion)
python main.py generate --all --process --remove-bg --create-ico
```

### Process Existing Images
```cmd
# Process images in output\raw folder
python main.py process --remove-bg --create-ico

# Process custom folder
python main.py process --input C:\path\to\images --remove-bg --create-ico
```

## Features

- **Multiple AI Providers**: Together AI, Replicate, OpenAI, Fal.ai
- **Parallel Processing**: Generate multiple images simultaneously  
- **Background Removal**: AI-powered background removal
- **ICO Conversion**: Multi-size ICO file creation
- **Consistent Naming**: Organized file naming with model tags
- **Error Handling**: Robust error handling and fallbacks
- **Windows Compatible**: Native Windows support with batch scripts

## Project Structure (Windows)

```
logo-icon-generator\
├── config\prompts.json      # Prompt definitions
├── src\                     # Source code
├── output\                  # Generated images
│   ├── raw\                # Original generated images
│   ├── processed\          # Background removed images
│   └── icons\              # ICO format files
├── logs\                   # Generation logs
├── setup_windows.bat        # Windows setup script
└── main.py                  # CLI entry point
```

## View Results (Windows)

```cmd
# Open output folders in Windows Explorer
explorer output\raw         # Original images
explorer output\processed   # Background removed  
explorer output\icons       # ICO files
explorer logs               # Log files
```

## API Keys Required

Add these to your `.env` file:

- `TOGETHER_API_KEY` - Together AI API key
- `REPLICATE_API_TOKEN` - Replicate API token  
- `OPENAI_API_KEY` - OpenAI API key
- `FAL_KEY` - Fal.ai API key

You only need the keys for the providers you want to use.

## Troubleshooting (Windows)

### Python Not Found
- Install Python from python.org
- Check "Add Python to PATH" during installation
- Restart Command Prompt

### Permission Issues
- Run Command Prompt as Administrator
- Right-click cmd.exe → "Run as administrator"

### Dependencies Issues
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt -v
```
