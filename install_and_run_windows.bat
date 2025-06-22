@echo off
echo ========================================
echo Telegram Chat PDF Processor - Windows
echo ========================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python...
    
    :: Download Python installer
    echo Downloading Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python_installer.exe'"
    
    :: Install Python silently
    echo Installing Python...
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Wait for installation
    timeout /t 10 /nobreak >nul
    
    :: Clean up installer
    del python_installer.exe
    
    :: Refresh environment variables
    call refreshenv.cmd >nul 2>&1
    
    echo Python installation completed.
) else (
    echo Python is already installed.
)

:: Verify Python installation
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python installation failed or not found in PATH
    echo Please install Python manually from https://python.org
    pause
    exit /b 1
)

:: Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pip...
    python -m ensurepip --upgrade
)

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install required packages
echo Installing required packages...
python -m pip install reportlab

:: Check if main script exists
if not exist "process_telegram_chats.py" (
    echo ERROR: process_telegram_chats.py not found!
    echo Please make sure the script is in the same directory.
    pause
    exit /b 1
)

:: Check if input file exists
if not exist "result.json" (
    echo WARNING: result.json not found!
    echo Please make sure your Telegram export file is named 'result.json'
    echo and placed in the same directory.
    pause
)

:: Run the main script
echo.
echo ========================================
echo Running Telegram Chat PDF Processor...
echo ========================================
echo.

python process_telegram_chats.py

:: Check if script ran successfully
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Processing completed successfully!
    echo Check the 'chats_clean_pdf' folder for results.
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ERROR: Script execution failed!
    echo ========================================
)

echo.
echo Press any key to exit...
pause >nul 