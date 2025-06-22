# Telegram Chat PDF Processor

Convert your Telegram chat exports to optimized PDF files ready for AI processing and vector databases.

## 🚀 Quick Start (Windows)

1. **Clone the repository:**
   ```bash
   git clone git@github.com:rldyourmnd/telegram_to_pdfVectorDB.git
   cd telegram_to_pdfVectorDB
   ```

2. **Export your Telegram chats:**
   - Open Telegram Desktop
   - Go to Settings → Advanced → Export Telegram data
   - Select "Personal chats" and "Machine-readable JSON"
   - Save the export as `result.json` in the project folder

3. **Run the processor:**
   - Double-click `launch_windows.bat`
   - The script will automatically install dependencies and process your chats

## 📁 Output Structure

```
project/
├── chats_clean_pdf/          # Generated PDF files
├── metadata/                 # Processing metadata
│   └── metadata_summary.json
├── result.json              # Your Telegram export
└── launch_windows.bat       # Easy launcher
```

## ⚙️ Configuration

Create a `.env` file to customize settings:

```env
# File paths
INPUT_FILE=result.json
OUTPUT_DIR=chats_clean_pdf
METADATA_DIR=metadata
METADATA_FILE=metadata_summary.json

# User identification
USER_NAME=YourName
USER_ID=your_user_id

# PDF settings
MAX_FILE_SIZE_KB=200
PDF_FONT_SIZE=10
PDF_LINE_SPACING=1.2
PDF_MARGIN_TOP=72
PDF_MARGIN_BOTTOM=72
PDF_MARGIN_LEFT=72
PDF_MARGIN_RIGHT=72

# Processing settings
SHORT_MESSAGE_THRESHOLD=50
LONG_MESSAGE_THRESHOLD=500
SHORT_MESSAGE_CHUNK_SIZE=15
MEDIUM_MESSAGE_CHUNK_SIZE=8
LONG_MESSAGE_CHUNK_SIZE=3

# Font paths (Windows)
WINDOWS_FONTS=C:/Windows/Fonts/arial.ttf,C:/Windows/Fonts/calibri.ttf
MACOS_FONTS=/System/Library/Fonts/Arial.ttf,/System/Library/Fonts/Helvetica.ttc
LINUX_FONTS=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf

# Debug options
VERBOSE_LOGGING=false
DEBUG_MODE=false
```

## 🔧 Manual Installation

If you prefer manual setup:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the processor
python process_telegram_chats.py
```

## 📊 Features

- **Optimized for AI**: PDFs sized for vector databases (max 200KB by default)
- **Smart chunking**: Dynamic chunk sizing based on message length
- **Memory efficient**: Processes large chats in parts
- **Clean formatting**: Optimized text format for AI processing
- **Metadata tracking**: Complete processing information
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🤖 n8n Integration

Perfect for n8n workflows:

1. **Text Splitter settings**: 
   - Chunk size: 800
   - Overlap: 200

2. **Batch processing**: 5-8 files at a time for optimal memory usage

3. **Search patterns**: 
   - `Me:` for your messages
   - `From [NAME]:` for contact messages

4. **Embedding models**:
   - OpenAI: `text-embedding-ada-002` (1536 dimensions)
   - Local: Any 768-dimension model

## 📋 Processing Statistics

The processor provides detailed statistics:
- Total chats processed
- Messages per chat
- PDF files created
- Chunk distribution
- Large chats split into multiple parts

## 🛠️ Requirements

- Python 3.7+
- Windows/macOS/Linux
- Telegram Desktop (for export)

## 📝 License

MIT License - feel free to use and modify! 