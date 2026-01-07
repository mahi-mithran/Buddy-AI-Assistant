# 🤖 Buddy AI Assistant

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

**A powerful, multi-model AI assistant with an intuitive GUI, voice capabilities, and file processing support.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#-configuration) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

Buddy AI Assistant is a feature-rich desktop application that brings multiple AI models together in one beautiful interface. Whether you're coding, writing, researching, or just having a conversation, Buddy adapts to your needs with intelligent context awareness and multi-topic management.

## ✨ Features

### 🧠 **Multiple AI Models**
- **Google Gemini 2.0 Flash** - Fast, intelligent responses
- **Groq Llama 3.3** - Powerful open-source reasoning
- **HuggingFace Flan-T5** - Versatile language understanding

### 💬 **Smart Chat Management**
- Multi-topic conversation tracking
- Conversation context memory (last 5 messages)
- Automatic chat history saving
- Export conversations to text files

### 📁 **File Processing**
- Upload and analyze multiple files simultaneously
- Supported formats: PDF, TXT, MD, Python, JavaScript, Java, C++, JSON, CSV
- Image file recognition (PNG, JPG, GIF, BMP, WEBP)
- File content preview window
- Automatic file size validation (5MB limit)

### 🎤 **Voice Capabilities**
- Voice input via microphone
- Text-to-speech responses
- Adjustable speech rate
- Ambient noise adjustment

### 🎨 **Modern UI**
- Clean, gradient-based design
- Color-coded message types
- Responsive layout
- Intuitive sidebar navigation
- Real-time AI model indicator

### 🛠️ **Developer-Friendly**
- Built-in system diagnostics
- API connection testing
- Error handling and logging
- Modular architecture

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Microphone (optional, for voice input)
- Speakers (optional, for voice output)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/buddy-ai-assistant.git
cd buddy-ai-assistant
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up API Keys

Open the script and replace the placeholder API keys with your actual keys:

```python
self.gemini_api_key = "your-gemini-api-key-here"
self.groq_api_key = "your-groq-api-key-here"
self.hf_api_key = "your-huggingface-api-key-here"
```

**Where to get API keys:**
- **Google Gemini**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Groq**: [Groq Console](https://console.groq.com/)
- **HuggingFace**: [HuggingFace Settings](https://huggingface.co/settings/tokens)

### Step 4: Run the Application

```bash
python buddy_ai_assistant.py
```

## 📦 Requirements

Create a `requirements.txt` file with:

```
tkinter
google-genai>=0.3.0
requests>=2.31.0
SpeechRecognition>=3.10.0
pyttsx3>=2.90
PyPDF2>=3.0.0
Pillow>=10.0.0
pywhatkit>=5.4
wikipedia>=1.4.0
pyjokes>=0.6.0
```

## 🎯 Usage

### Basic Chat

1. Launch the application
2. Select an AI model from the sidebar (Gemini, Groq, or HuggingFace)
3. Type your message in the input box
4. Press **Send** or hit **Enter**

### Voice Input

1. Click the **Voice** button
2. Speak your message when prompted
3. The transcribed text will appear in the input box
4. Review and send

### File Upload

1. Click **Attach** to select files
2. Choose one or multiple files
3. Click **Preview** to view file contents
4. Send your message - file context will be included automatically
5. Click **Clear** to remove files

### Managing Topics

- **Switch Topics**: Click on a topic in the sidebar
- **New Topic**: Click **+ New** and enter a name
- **Delete Topic**: Select a topic and click **Delete** (default topics are protected)

### Testing Connections

- Use **Settings > Test All** to verify all AI models
- Or click **Test Connection** for the currently selected model

### Exporting Chats

1. Go to **File > Export Chat**
2. Choose a location and filename
3. Your conversation will be saved as a text file

## ⚙️ Configuration

### Customizing Colors

Edit the color scheme in the `__init__` method:

```python
self.primary_color = "#4f46e5"  # Indigo
self.secondary_color = "#7c3aed"  # Purple
self.accent_color = "#ec4899"  # Pink
```

### Adjusting Speech Rate

Modify the TTS speed:

```python
self.engine.setProperty("rate", 175)  # Words per minute
```

### Changing Context Window

Adjust how many previous messages are included:

```python
context = self.chat_history[self.current_topic][-5:]  # Last 5 messages
```

## 🗂️ Project Structure

```
buddy-ai-assistant/
├── buddy_ai_assistant.py    # Main application file
├── requirements.txt          # Python dependencies
├── chat_history.json        # Saved conversations (auto-generated)
├── README.md                # This file
├── LICENSE                  # MIT License
└── .gitignore              # Git ignore rules
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Areas for Contribution

- 🌐 Add new AI model integrations
- 🎨 Improve UI/UX design
- 📝 Enhance documentation
- 🐛 Fix bugs and issues
- ✨ Suggest new features
- 🌍 Add internationalization support

## 🐛 Known Issues

- Voice recognition requires an active internet connection (Google Speech Recognition API)
- PDF extraction may struggle with complex layouts or scanned documents
- Large files (>5MB) are automatically skipped

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **Google** for the Gemini API
- **Groq** for fast inference capabilities
- **HuggingFace** for open-source models
- **Python Tkinter** for the GUI framework
- All the amazing open-source libraries that made this possible


<div align="center">

**Made with ❤️ and Python**

If you find this project helpful, please consider giving it a ⭐!

</div>
