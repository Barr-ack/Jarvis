# J.A.R.V.I.S. AI Assistant

**A powerful, modular AI assistant with voice control, system automation, and advanced vision capabilities.**

## 📋 Overview

J.A.R.V.I.S. is a comprehensive AI assistant designed to help you with a wide range of tasks including system control, file operations, automation, communication, and advanced features. Built with Python and powered by Google GenAI, it combines voice interaction, visual processing, and intelligent automation in a sleek Streamlit interface.

## ✨ Key Features

### 🎤 Voice Interaction
- Wake word detection ("Hey Jarvis")
- Real-time speech recognition and synthesis
- Natural voice responses using ElevenLabs integration
- British accent support

### 👁️ Vision Capabilities
- Live webcam feed processing
- Screen capture and analysis
- Real-time visual understanding and commentary
- Scene detection and description

### 🤖 System Control
- Volume and brightness adjustment
- Application launching and management
- System diagnostics and monitoring
- Process control

### 📁 File Operations
- Create, read, edit, and delete files
- Folder management and organization
- File compression and archival
- Directory traversal and listing

### 🔄 Automation
- Scheduled task execution
- Workflow automation
- System task scheduling
- Routine automation

### 💬 Communication
- Email management
- Message sending (WhatsApp integration via PyWhatKit)
- Web browsing automation
- Clipboard operations

### 📊 Advanced Features
- Web scraping and RSS feed parsing
- Git repository management
- Code execution and testing
- Machine learning utilities
- PDF document handling
- Search functionality

### 📚 Memory Management
- Session memory storage
- Exchange buffer management
- Relevant memory retrieval
- Long-term context preservation

## 🛠️ Tech Stack

- **Core AI**: Google GenAI
- **Frontend**: Streamlit
- **Backend**: Python 3.x
- **Speech**: PyAudio, ElevenLabs
- **Vision**: OpenCV, Pillow
- **System**: PyAutoGUI, PyInput, PSUtil
- **Data Processing**: Pandas, Plotly, Scikit-learn
- **Utilities**: Beautiful Soup, GitPython, Selenium, PyPDF2

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- FFmpeg (for audio processing)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Barr-ack/Jarvis.git
   cd Jarvis
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   ELEVENLABS_API_KEY=your_key_here
   GOOGLE_API_KEY=your_google_genai_key
   ```

5. **Configure settings** (optional)
   Edit `config.json` to customize wake words, system instructions, and other settings.

## 🚀 Usage

### Running the Web Interface
```bash
streamlit run app.py
```
This launches the beautiful Streamlit UI on `http://localhost:8501`

### Running the Core Assistant
```bash
python main.py
```

### Command-line Arguments
```bash
python main.py --help
```

## 📁 Project Structure

```
Jarvis/
├── main.py                      # Core AI loop and entry point
├── app.py                       # Streamlit web interface
├── config_loader.py             # Configuration management
├── memory.py                    # Memory and session management
├── config.json                  # System configuration
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create this)
└── handlers/                    # Modular feature handlers
    ├── system_control.py        # System operations
    ├── file_operations.py       # File management
    ├── communication.py         # Communication features
    ├── automation.py            # Task automation
    ├── advanced_features.py     # Advanced capabilities
    ├── input_control.py         # Input automation
    ├── pdf_handler.py           # PDF processing
    └── tool_declarations.py     # Tool definitions for AI
```

## ⚙️ Configuration

Edit `config.json` to customize:

- **Wake Word**: Trigger phrase for the assistant
- **System Instructions**: Behavioral guidelines for JARVIS
- **Audio Settings**: Sample rates, chunk sizes, channels
- **Default Mode**: Operating mode (assistant, automation, etc.)

Example config snippet:
```json
{
    "wake_word": "Hey Jarvis",
    "CHANNELS": 1,
    "SEND_SAMPLE_RATE": 16000,
    "RECEIVE_SAMPLE_RATE": 24000,
    "CHUNK_SIZE": 1024,
    "default_mode": "assistant"
}
```

## 🎯 Use Cases

- **Personal Assistant**: Voice-controlled task management and automation
- **System Automation**: Scheduled jobs and routine automation
- **Content Analysis**: PDF parsing, web scraping, document processing
- **Development Aid**: Code execution, testing, Git repository management
- **Information Retrieval**: Web search, RSS feeds, real-time data
- **Accessibility**: Voice control for users with mobility limitations

## 🔐 Security Notes

- Keep your API keys secure in the `.env` file
- Never commit `.env` to version control
- Use strong passwords for any integrated services
- Review permissions for system control features

## 🤝 Contributing

To extend JARVIS with new features:

1. Create a new handler in the `handlers/` directory
2. Define the tool in `handlers/tool_declarations.py`
3. Import and initialize in `main.py`
4. Add corresponding UI elements in `app.py` if needed

## 📝 License

This project is created for personal use. Modify and distribute according to your needs.

## 🐛 Troubleshooting

### Audio Issues
- Ensure PyAudio is properly installed
- Check system audio device settings
- Verify microphone and speaker access permissions

### Google GenAI Errors
- Validate your API key in `.env`
- Check your Google Cloud quota limits
- Ensure internet connectivity

### Platform-Specific Issues
- **Windows**: Some handlers (pycaw, wmi) are Windows-only and will be skipped on other platforms
- **Linux/Mac**: Brightness control may need additional permissions

## 📞 Support

For issues and questions:
- Check the configuration in `config.json`
- Review environment variables
- Check console output for detailed error messages
- Verify all dependencies are installed: `pip list`

## 🌟 Future Enhancements

- Multi-language support
- Plugin system for extensibility
- Cloud synchronization for memory
- Advanced gesture control
- Mobile app integration

---

**Created by**: Mr. Barrack  murunga
**Status**: Active Development  
**Last Updated**: January 2026
