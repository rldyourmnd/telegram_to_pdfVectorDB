#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo -e "   Telegram Chat PDF Processor"
echo -e "========================================"
echo -e "${NC}"

# Check if .env file exists
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Found .env configuration file${NC}"
else
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    if [ -f ".env.example" ]; then
        echo -e "${BLUE}📋 Creating .env from .env.example...${NC}"
        cp ".env.example" ".env"
        echo -e "${GREEN}✅ Created .env file - please edit it with your settings${NC}"
        echo ""
        echo -e "${BLUE}🔧 Please edit .env file with your settings:${NC}"
        echo "nano .env"
        echo ""
        echo "Press Enter after editing .env file..."
        read
    else
        echo -e "${RED}❌ No .env.example file found!${NC}"
        echo "Please create a .env file with your configuration."
        echo ""
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}🔍 Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python is not installed${NC}"
        echo "Please install Python 3.7+"
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo -e "${GREEN}✅ Python found${NC}"
echo ""

echo -e "${BLUE}🔍 Checking dependencies...${NC}"
$PYTHON_CMD -c "import reportlab, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Missing dependencies. Installing...${NC}"
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ All dependencies found${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Starting Telegram Chat PDF Processor...${NC}"
echo ""

$PYTHON_CMD process_telegram_chats.py

echo ""
echo -e "${GREEN}🎯 Processing completed!${NC}"
echo "" 