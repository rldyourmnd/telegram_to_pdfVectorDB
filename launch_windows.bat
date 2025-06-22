@echo off
chcp 65001 >nul
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
    echo ❌ Python not found! Please install Python 3.7+ first.
    echo Download from: https://www.python.org/downloads/
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

REM Check if result.json exists
if not exist result.json (
    echo ❌ result.json not found!
    echo Please place your Telegram export file as 'result.json' in this directory
    echo.
    echo How to export:
    echo 1. Open Telegram Desktop
    echo 2. Settings → Advanced → Export Telegram data
    echo 3. Select 'Personal chats' and 'Machine-readable JSON'
    echo 4. Save as 'result.json' in this folder
    echo.
    pause
    exit /b 1
)

echo ✅ result.json found
echo.

REM Create output directories
if not exist chats_clean_pdf mkdir chats_clean_pdf
if not exist metadata mkdir metadata

echo 🚀 Starting processing...
echo.

REM Run the main script
python process_telegram_chats.py

echo.
echo 🎯 Processing completed!
echo.
echo 📁 Check these folders:
echo    - chats_clean_pdf/     (PDF files)
echo    - metadata/            (processing info)
echo.
pause 