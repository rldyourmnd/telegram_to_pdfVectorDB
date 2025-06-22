#!/bin/bash

echo "========================================"
echo "Telegram Chat PDF Processor - Ubuntu"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for system-wide installation
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. Python will be installed system-wide."
    SUDO_CMD=""
else
    print_status "Running as regular user. May need sudo for installation."
    SUDO_CMD="sudo"
fi

# Update package list
print_status "Updating package list..."
$SUDO_CMD apt update

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "Python 3 is already installed (version $PYTHON_VERSION)"
    PYTHON_CMD="python3"
else
    print_status "Python 3 not found. Installing Python 3..."
    
    # Install Python 3 and essential packages
    $SUDO_CMD apt install -y python3 python3-pip python3-venv python3-dev
    
    if [ $? -eq 0 ]; then
        print_status "Python 3 installation completed."
        PYTHON_CMD="python3"
    else
        print_error "Failed to install Python 3!"
        exit 1
    fi
fi

# Check if pip is available
if command -v pip3 &> /dev/null; then
    print_status "pip3 is available"
    PIP_CMD="pip3"
elif $PYTHON_CMD -m pip --version &> /dev/null; then
    print_status "pip is available via python3 -m pip"
    PIP_CMD="$PYTHON_CMD -m pip"
else
    print_status "Installing pip..."
    $SUDO_CMD apt install -y python3-pip
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    else
        PIP_CMD="$PYTHON_CMD -m pip"
    fi
fi

# Upgrade pip
print_status "Upgrading pip..."
$PIP_CMD install --upgrade pip --user

# Install required system packages for PDF generation
print_status "Installing system dependencies..."
$SUDO_CMD apt install -y python3-tk python3-dev build-essential

# Install required Python packages
print_status "Installing required Python packages..."

# Create a virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install packages in virtual environment
print_status "Installing reportlab..."
pip install reportlab

# Verify installation
if python -c "import reportlab" 2>/dev/null; then
    print_status "All dependencies installed successfully!"
else
    print_error "Failed to install required packages!"
    exit 1
fi

# Check if main script exists
if [ ! -f "process_telegram_chats.py" ]; then
    print_error "process_telegram_chats.py not found!"
    print_error "Please make sure the script is in the same directory."
    exit 1
fi

# Check if input file exists
if [ ! -f "result.json" ]; then
    print_warning "result.json not found!"
    print_warning "Please make sure your Telegram export file is named 'result.json'"
    print_warning "and placed in the same directory."
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Run the main script
echo ""
echo "========================================"
echo "Running Telegram Chat PDF Processor..."
echo "========================================"
echo ""

python process_telegram_chats.py

# Check if script ran successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    print_status "Processing completed successfully!"
    print_status "Check the 'chats_clean_pdf' folder for results."
    echo "========================================"
else
    echo ""
    echo "========================================"
    print_error "Script execution failed!"
    echo "========================================"
    exit 1
fi

# Deactivate virtual environment
deactivate

echo ""
print_status "Installation and execution completed!"
print_status "Virtual environment created in 'venv' directory"
print_status "To run the script again, use: source venv/bin/activate && python process_telegram_chats.py" 