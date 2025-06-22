# Telegram Chat PDF Processor

A Python script that converts exported Telegram chats into optimized PDF files for AI vector database processing and personal knowledge management.

## 🚀 Features

- **Smart Chat Processing**: Automatically processes personal chats from Telegram JSON exports
- **Emoji Conversion**: Converts emojis to text descriptions for better AI processing (😀 → [smile])
- **Chronological Numbering**: Adds message sequence numbers `[5/123] Me: message text`
- **Automatic File Splitting**: Splits large chats into multiple 200KB PDF files for optimal vector processing  
- **Cyrillic Support**: Full support for Russian and other Cyrillic languages
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **AI-Optimized Output**: Structured format perfect for n8n workflows and vector databases

## 📋 Requirements

```bash
pip install reportlab
```

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/rldyourmnd/telegram-chat-pdf-processor.git
cd telegram-chat-pdf-processor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📱 Getting Telegram Chat Export

1. Open **Telegram Desktop**
2. Go to **Settings** → **Advanced** → **Export Telegram data**
3. Select **Personal chats** only
4. Choose **JSON** format
5. Save as `result.json` in the script directory

## 🚀 Usage

### Basic Usage
```bash
python process_telegram_chats.py
```

### Custom Input File
```python
from process_telegram_chats import process_telegram_chats_optimized
process_telegram_chats_optimized('your_export.json')
```

## 📁 Output Structure

```
chats_clean_pdf/
├── John_Doe.pdf                    # Single file chat
├── Jane_Smith_part1of3.pdf         # Multi-part chat (part 1)
├── Jane_Smith_part2of3.pdf         # Multi-part chat (part 2)  
├── Jane_Smith_part3of3.pdf         # Multi-part chat (part 3)
└── metadata_summary.json           # Processing metadata
```

## 📊 Message Format

Each message is formatted with chronological numbering:

```
[5/123] Me: Hey, how are you doing?
[6/123] From John: I'm good, thanks! How about you?
[7/123] Me: Great! Want to meet up later?
```

## 🤖 AI Integration

### Recommended n8n Settings
- **Text Splitter**: chunk_size=800, overlap=200
- **Embedding Model**: text-embedding-ada-002 (OpenAI)
- **Vector Dimensions**: 1536 (OpenAI) or 768 (local models)
- **File Processing**: Use 'pdf-parse' node before text splitter

### Search Patterns
- `"Me:"` - Find messages sent by you
- `"From [Name]:"` - Find messages from specific person
- `"[123/456]"` - Search by chronological position
- Person names from metadata for identification

## ⚙️ Configuration

### File Size Optimization
The script automatically adjusts chunk sizes based on message length:
- **Short messages** (<50 chars): 25 messages per chunk
- **Medium messages** (50-150 chars): 18 messages per chunk  
- **Long messages** (>150 chars): 12 messages per chunk

### Maximum File Size
- Default: 200KB per PDF file
- Modify `max_size_kb` parameter in `create_optimized_pdf_parts()`

## 📈 Processing Statistics

The script provides detailed processing information:

```
🎯 Processing completed successfully!
📊 Results:
   ✅ Processed: 15 chats
   📄 Created: 23 PDF files
   💬 Total messages: 5,847
   📦 Total chunks: 892
   📈 Average: 389.8 messages/chat, 38.8 chunks/file
```

## 🔍 Advanced Features

### Emoji Processing
Converts 200+ common emojis to text descriptions:
```python
'😀': '[smile]', '😢': '[cry]', '❤️': '[red_heart]'
```

### Text Cleaning
- Removes excessive whitespace
- Filters non-printable characters
- Preserves punctuation and Cyrillic text
- Truncates very long messages (500 char limit)

### Person Information Extraction
Automatically extracts:
- Person name from chat title
- First/last name separation
- Telegram username (if available)
- Message direction detection

## 🛠️ Building Standalone Executable

Use the included build scripts to create standalone executables:

```bash
# Build standalone version
python build_standalone_final.py
```

The executable will be created in the `dist/` folder with zero dependencies.

## 📝 Metadata Output

The script generates `metadata_summary.json` with detailed information:

```json
{
  "filename": "John_Doe.pdf",
  "person_name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "telegram_username": "@johndoe",
  "chunk_count": 45,
  "file_size_kb": 187.3,
  "total_messages_in_chat": 234,
  "sent_count": 128,
  "received_count": 106
}
```

## 🤝 Use Cases

- **Personal AI Assistant**: Create a chatbot that knows your conversation history
- **Relationship Analysis**: Analyze communication patterns with different people
- **Information Retrieval**: Find specific conversations, plans, or agreements
- **Knowledge Management**: Build a searchable database of your communications
- **Business Intelligence**: Analyze client communications and follow-ups

## 🔧 Troubleshooting

### Font Issues
If you see squares instead of text:
- Install system fonts (Arial, Calibri, Tahoma)
- Check font paths in `setup_fonts()` function

### Large Memory Usage
For very large exports:
- Process chats in smaller batches
- Increase system RAM or use virtual memory
- Consider splitting the JSON export manually

### JSON Format Errors
Ensure your export:
- Uses JSON format (not HTML)
- Includes personal chats only
- Is not corrupted or truncated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Free for commercial use** - You can use this software in commercial projects without any restrictions.

## ⭐ Acknowledgments

- **Author**: Danil Silantev ([@rldyourmnd](https://github.com/rldyourmnd))
- Built for AI-powered personal knowledge management
- Optimized for n8n workflow automation
- Designed for vector database integration
- Supports modern NLP and embedding models

## 🔗 Related Projects

- [n8n](https://n8n.io/) - Workflow automation platform
- [Pinecone](https://www.pinecone.io/) - Vector database
- [OpenAI API](https://openai.com/api/) - Embedding and chat models

---

**Star ⭐ this repo if it helped you build your personal AI assistant!** 