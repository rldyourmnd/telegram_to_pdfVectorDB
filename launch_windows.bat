@echo off
title Telegram Chat PDF Processor
color 0A

echo ========================================
echo    Telegram Chat PDF Processor
echo ========================================
echo.

REM Check if .env file exists
if exist ".env" (
    echo ✅ Found .env configuration file
) else (
    echo ⚠️  No .env file found
    if exist ".env.example" (
        echo 📋 Creating .env from .env.example...
        copy ".env.example" ".env" >nul
        echo ✅ Created .env file - please edit it with your settings
        echo.
        echo 🔧 Opening .env file for editing...
        notepad ".env"
        echo.
        echo Press any key after editing .env file...
        pause >nul
    ) else (
        echo ❌ No .env.example file found!
        echo Please create a .env file with your configuration.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

echo 🔍 Checking dependencies...
python -c "import reportlab, dotenv" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Missing dependencies. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ All dependencies found
)

echo.
echo 🚀 Starting Telegram Chat PDF Processor...
echo.

python process_telegram_chats.py

echo.
echo 🎯 Processing completed!
echo.
pause 