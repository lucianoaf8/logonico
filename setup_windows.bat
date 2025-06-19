@echo off
REM Logo/Icon Generator - Windows Setup Script
echo ===============================================
echo Logo/Icon Generator - Windows Setup
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Create project if it doesn't exist
if not exist "logo-icon-generator" (
    echo Creating project structure...
    python complete_setup.py
    echo.
)

REM Navigate to project directory
cd logo-icon-generator

REM Copy .env.example to .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo Please edit .env file with your API keys:
    echo - TOGETHER_API_KEY
    echo - REPLICATE_API_TOKEN  
    echo - OPENAI_API_KEY
    echo - FAL_KEY
    echo.
    echo Opening .env file for editing...
    timeout /t 2 >nul
    notepad .env
)

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Try running: pip install --upgrade pip
    echo Then run this script again
    pause
    exit /b 1
)

echo.
echo ===============================================
echo Setup Complete!
echo ===============================================
echo.
echo Quick test commands:
echo   python main.py status
echo   python main.py list-models
echo   python main.py generate --all
echo.
echo To get started:
echo 1. Make sure your API keys are set in .env
echo 2. Run: python main.py status
echo 3. Run: python main.py generate --all
echo.

REM Test the installation
echo Testing installation...
python main.py status

if errorlevel 1 (
    echo.
    echo WARNING: There may be issues with the setup
    echo Check your API keys in the .env file
) else (
    echo.
    echo SUCCESS: Setup appears to be working correctly!
)

echo.
echo Setup script complete. Press any key to exit.
pause >nul