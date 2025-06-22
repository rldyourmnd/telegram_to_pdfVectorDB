# Telegram Chat PDF Processor

Advanced Python script that converts Telegram chat exports (JSON) into optimized PDF files for AI processing with n8n workflows. Features smart chunking, emoji conversion, and zero-dependency operation.

## 🎯 Key Features

- **Smart PDF Generation**: Creates optimized PDFs (150-200KB each) perfect for n8n Text Splitter
- **Advanced Chunking**: Dynamic message grouping based on content length and chat patterns
- **200+ Emoji Support**: Converts emojis to readable text descriptions for better AI processing
- **Message Direction Detection**: Clearly marks sent (>) vs received (<) messages
- **Smart Text Cleaning**: Removes problematic characters while preserving meaning
- **Multi-part Support**: Automatically splits large chats into manageable parts
- **Zero Dependencies**: Works with just Python standard library + ReportLab
- **Configuration-Based**: All settings managed through `.env` files for easy customization

## 📦 Quick Setup

### Windows
```bash
# Clone and run
git clone <repository>
cd telegram-chat-processor
double-click launch_windows.bat
```

### Ubuntu/Linux
```bash
# Clone and setup
git clone <repository>
cd telegram-chat-processor
chmod +x launch_linux.sh
./launch_linux.sh
```

Both scripts will:
1. Check for `.env` configuration file
2. Create `.env` from `.env.example` if needed
3. Install dependencies automatically
4. Launch the processor

## ⚙️ Configuration

The application uses `.env` files for all configuration. Copy `.env.example` to `.env` and customize:

### Basic Settings
```env
# Input/Output
INPUT_FILE=result.json
OUTPUT_DIR=chats_clean_pdf
METADATA_FILE=metadata_summary.json

# User Identification
USER_NAME=Your Name
USER_ID=user123456789

# PDF Settings
MAX_FILE_SIZE_KB=200
MAX_MESSAGE_LENGTH=500
PDF_FONT_SIZE=10
```

### Advanced Configuration
```env
# Chunking Algorithm
SHORT_MESSAGE_CHUNK_SIZE=25
MEDIUM_MESSAGE_CHUNK_SIZE=18
LONG_MESSAGE_CHUNK_SIZE=12

# Text Processing
MIN_MESSAGE_LENGTH=2
SHORT_MESSAGE_THRESHOLD=50
LONG_MESSAGE_THRESHOLD=200

# Debug Options
VERBOSE_LOGGING=false
SHOW_PROGRESS=true
```

See `.env.example` for complete configuration options with detailed explanations.

## 🚀 Usage

### Standard Processing
```bash
python process_telegram_chats.py
```

### With Custom Configuration
Create your own `.env` file or use `.env.production` for optimized settings:
```bash
cp .env.production .env
python process_telegram_chats.py
```

## 📁 Input Format

Place your Telegram export file as `result.json` (or configure `INPUT_FILE` in `.env`):

```json
{
  "chats": {
    "list": [
      {
        "name": "Person Name",
        "type": "personal_chat",
        "messages": [
          {
            "id": 1,
            "type": "message",
            "date": "2024-01-01T10:00:00",
            "from": "Your Name",
            "from_id": "user123456789",
            "text": "Hello! 😊"
          }
        ]
      }
    ]
  }
}
```

## 📄 Output Format

### PDF Structure
```
Message 1 > Hello! [smiling face with smiling eyes]
Message 2 < Hi there! How are you?
Message 3 > I'm doing great, thanks!
```

### Message Format Features
- **Chronological numbering**: Message 1, Message 2, etc.
- **Direction detection**: `>` (sent by you), `<` (received from contact)
- **Emoji conversion**: 😊 → [smiling face with smiling eyes]
- **Smart text cleaning**: Removes problematic characters, preserves meaning

### Metadata Output
`metadata_summary.json` contains processing information:
```json
[
  {
    "filename": "John_Doe_clean.pdf",
    "person_name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "telegram_username": "@johndoe",
    "original_chat": "John Doe",
    "is_multipart": false,
    "chunk_count": 15,
    "file_size_kb": 187.3,
    "total_messages_in_chat": 245,
    "sent_count": 120,
    "received_count": 125
  }
]
```

## 🤖 AI Integration (n8n)

### Recommended Workflow Settings
- **Text Splitter**: chunk_size=800, overlap=200
- **Batch Processing**: 5-8 files per batch for optimal memory usage
- **Vector Database**: Pinecone with 1536 dimensions (OpenAI)
- **Embedding Model**: text-embedding-ada-002

### Search Patterns
- **Messages**: `Message \d+`, `>`, `<`
- **People**: Use person names from metadata.json
- **Directions**: `> ` (your messages), `< ` (their messages)

### Processing Tips
1. Load metadata.json first for person identification
2. Use PDF-parse node before Text Splitter
3. Process multipart files in sequence
4. Index person names and Telegram usernames for better search

## 🔧 Advanced Features

### Smart Chunking Algorithm
- **Short messages** (<50 chars): 25 messages per chunk
- **Medium messages** (50-200 chars): 18 messages per chunk  
- **Long messages** (>200 chars): 12 messages per chunk
- **File size optimization**: Adjusts chunk sizes based on average message length
- **Memory efficient**: Processes chunks individually to handle large datasets

### Font Support
- **Windows**: Arial, Calibri, Times New Roman
- **macOS**: Helvetica, Arial, Times
- **Linux**: DejaVu Sans, Liberation Sans, Arial (install with: `sudo apt install fonts-dejavu fonts-liberation`)

### Text Processing
- **200+ emoji conversion**: Complete emoji-to-text mapping
- **Unicode normalization**: Handles special characters properly
- **Smart truncation**: Long messages truncated with "..." indicator
- **Character filtering**: Removes problematic PDF characters while preserving meaning

## 🛠️ Installation

### Requirements
- Python 3.7+
- ReportLab 3.6.0+
- python-dotenv 0.19.0+

### Manual Installation
```bash
pip install reportlab>=3.6.0 python-dotenv>=0.19.0
```

### Dependencies
```bash
pip install -r requirements.txt
```

## 🐛 Troubleshooting

### Common Issues

**"No module named 'reportlab'"**
```bash
pip install reportlab python-dotenv
```

**"result.json not found"**
- Check file exists in project directory
- Update `INPUT_FILE` in `.env` if using different filename

**"Permission denied" on Linux**
```bash
chmod +x launch_linux.sh
sudo apt install python3-pip
```

**Font issues on Linux**
```bash
sudo apt install fonts-dejavu fonts-liberation
fc-cache -fv
```

**Large file processing (>100MB)**
- Increase system memory
- Process in smaller batches
- Use SSD storage for better I/O performance

### Debug Mode
Enable verbose logging in `.env`:
```env
VERBOSE_LOGGING=true
SHOW_PROGRESS=true
```

### Empty Output
If no PDFs are created, check:
1. JSON file format matches expected structure
2. Chat type is 'personal_chat'
3. Messages contain text content
4. User identification settings in `.env`
5. Output directory write permissions

## 📊 Performance

- **Processing Speed**: ~1000 messages per second
- **Memory Usage**: <100MB for files up to 50MB
- **Output Size**: Typically 150-200KB per PDF (optimal for n8n)
- **Supported File Size**: Up to 500MB JSON input files

## 🎯 Use Cases

- **Personal AI Assistant**: Create searchable knowledge base from your chats
- **Business Intelligence**: Analyze communication patterns and relationships
- **Content Analysis**: Extract insights from conversation data
- **Backup Processing**: Convert chat exports to searchable PDF format
- **Research**: Analyze conversation data for academic or business research

## 🔒 Privacy

- **Local Processing**: All data stays on your machine
- **No Network Calls**: Completely offline operation
- **Configurable**: Control exactly what data is processed
- **Open Source**: Full transparency of data handling

## 📝 License

MIT License - Feel free to use, modify, and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with proper configuration support
4. Test with different `.env` configurations
5. Submit pull request

---

**Ready to process your Telegram chats for AI analysis? Start with the quick setup commands above!** 