# Logo/Icon Generator - Windows Setup Guide

## 🚀 Quick Setup (Windows)

### Step 1: Create the Project
```cmd
# Save complete_setup.py to your desktop or projects folder
# Open Command Prompt (cmd) or PowerShell in that folder
python complete_setup.py
```

### Step 2: Navigate and Configure
```cmd
cd logo-icon-generator
copy .env.example .env
notepad .env
```

**In the .env file, add your API keys:**
```env
TOGETHER_API_KEY=your_actual_together_api_key_here
REPLICATE_API_TOKEN=r8_your_actual_replicate_token_here
OPENAI_API_KEY=sk-your_actual_openai_key_here
FAL_KEY=your_actual_fal_ai_key_here
```

### Step 3: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 4: Test Setup
```cmd
python main.py status
```

## 📋 Available Commands (Windows)

### System Status & Info
```cmd
# Check system status and API keys
python main.py status

# List all available models
python main.py list-models
```

### Image Generation
```cmd
# Generate with ALL available models (recommended first run)
python main.py generate --all

# Generate with specific models only
python main.py generate --models flux_dev,dalle3,galleri5_icons

# Generate specific prompts only
python main.py generate --all --prompts spark_dialog,magic_wand

# Generate with specific models AND prompts
python main.py generate --models flux_dev,dalle3 --prompts spark_dialog
```

### Complete Pipeline (Generate + Process)
```cmd
# Full pipeline: Generate + Background Removal + ICO conversion
python main.py generate --all --process --remove-bg --create-ico

# Full pipeline with specific models
python main.py generate --models flux_dev,dalle3 --process --remove-bg --create-ico
```

### Process Existing Images
```cmd
# Process images in output\raw folder
python main.py process --remove-bg --create-ico

# Process images from custom folder
python main.py process --input C:\path\to\your\images --remove-bg --create-ico
```

## 📁 Output Structure (Windows)

```
logo-icon-generator\
├── output\
│   ├── raw\          # spark_dialog_flux_dev_20250619_143022.png
│   ├── processed\    # spark_dialog_flux_dev_20250619_143022_nobg.png
│   └── icons\        # spark_dialog_flux_dev_20250619_143022.ico
├── logs\             # generation.log, errors.log
├── config\
│   └── prompts.json  # Your prompt definitions
└── main.py           # Main entry point
```

## 🔧 Windows-Specific Tips

### If Python Command Doesn't Work:
```cmd
# Try these alternatives:
py main.py status
python.exe main.py status
```

### View Generated Images:
```cmd
# Open output folder in Windows Explorer
explorer output\raw

# Open processed folder
explorer output\processed

# Open icons folder  
explorer output\icons
```

### View Logs:
```cmd
# View latest log file
notepad logs\generation.log

# Open logs folder
explorer logs
```

### Edit Prompts:
```cmd
notepad config\prompts.json
```

## 🚨 Troubleshooting (Windows)

### Python Not Found:
1. Install Python from python.org
2. Make sure "Add Python to PATH" is checked during installation
3. Restart Command Prompt

### Permission Errors:
```cmd
# Run Command Prompt as Administrator
# Right-click cmd.exe -> "Run as administrator"
```

### Path Issues:
```cmd
# Use full paths if needed
python C:\path\to\logo-icon-generator\main.py status
```

### Dependencies Issues:
```cmd
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

## 📊 Example Workflow (Windows)

```cmd
# 1. Check what's available
python main.py status
python main.py list-models

# 2. Generate a few test images
python main.py generate --models flux_dev,dalle3 --prompts spark_dialog

# 3. Check results
explorer output\raw

# 4. Run full pipeline on all prompts
python main.py generate --all --process --remove-bg --create-ico

# 5. Check all outputs
explorer output
```

## 🎯 Production Workflow (Windows)

```cmd
# Daily logo generation workflow:
python main.py generate --all --process --remove-bg --create-ico

# Results will be in:
# - output\raw\        (original generated images)  
# - output\processed\  (background removed)
# - output\icons\      (ICO format for applications)
```

## 📝 Notes for Windows Users

- Use `\` for paths (Python handles this automatically)
- File paths are case-insensitive 
- Use `copy` instead of `cp` for copying files
- Use `explorer` to open folders in Windows Explorer
- Use `notepad` to edit text files
- Command Prompt and PowerShell both work
- Avoid spaces in folder names or use quotes: `"C:\My Projects\logo generator"`