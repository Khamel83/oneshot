# 🎤 Atlas Voice - Enhanced Analysis System

**Turn any AI into your voice twin using privacy-first prompt engineering with comprehensive corpus analysis**

[![Privacy First](https://img.shields.io/badge/Privacy-First-green)](https://github.com/Khamel83/atlas-voice#privacy)
[![Nuclear Safe Room](https://img.shields.io/badge/Architecture-Nuclear%20Safe%20Room-blue)](https://github.com/Khamel83/atlas-voice#architecture)
[![OOS Complete](https://img.shields.io/badge/OOS%20Workflow-Complete-brightgreen)](https://github.com/Khamel83/atlas-voice#oos-workflow)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Khamel83%2Fatlas--voice-blue)](https://github.com/Khamel83/atlas-voice)
[![Open Source](https://img.shields.io/badge/License-MIT-purple)](https://github.com/Khamel83/atlas-voice#license)

---

## 🎯 What It Does

Atlas Voice analyzes your writing patterns and generates custom AI prompts that make any AI (ChatGPT, Claude, etc.) sound exactly like you.

**🔬 Enhanced Analysis**: Complete OOS workflow implementation with 104M+ character corpus analysis, topic clustering, and knowledge boundary mapping.

**🛡️ Privacy-first architecture**: Your original content is never stored, only linguistic patterns are extracted.

**✅ Production Ready**: Complete integration with enhanced AI voice generation and knowledge boundary protection.

**🎯 Current Goal**: "Here's my data, give me a system prompt that makes AI sound like me but as smart as GPT-5"

---

## 🚀 Get Started in 5 Minutes

```bash
# 1. Process your data (emails, chats, documents)
python3 src/main.py nuclear-process /path/to/your/data

# 2. Generate your enhanced voice prompt
python3 oos/ENHANCED_VOICE_INTEGRATOR_SIMPLE.py

# 3. Use your enhanced voice with any AI!
python3 src/enhanced_ai_voice_generator.py
```

---

## 🏢 Nuclear Safe Room Architecture

**Industry-leading privacy protection:**

- **🚪 Room One**: Processes your data (temporary)
- **🔐 Airlock**: Validates and secures transfer
- **🚪 Room Two**: Stores ONLY linguistic patterns

**Zero original content retention** - complete privacy by design.

---

## ✨ Key Features

### **🎤 Voice Analysis**
- Function word frequencies
- Sentence structure patterns
- Vocabulary complexity metrics
- Style markers (casual vs formal)
- Personal phrase patterns

### **🧠 Intelligent Processing**
- Handles any file format automatically
- LLM-powered format detection
- Processes millions of words
- Extracts patterns, not content

### **🔒 Privacy Guarantees**
- Nuclear safe room architecture
- No original content storage
- Complete user control
- Audit logging and compliance

### **🎛️ Natural Interface**
- Smart natural language commands
- Interactive voice assistant
- Privacy dashboard
- Data source management

---

## 📊 Supported Data Sources

**✅ All Formats:**
- Emails (.eml, .mbox)
- Documents (.txt, .md, .docx)
- Spreadsheets (.csv, .xlsx)
- Chat logs (.json, .txt)
- Social media exports
- Any text-containing files

**📈 Scale:**
- Small datasets (100 words)
- Large datasets (millions of words)
- Batch processing
- Memory efficient

---

## 🛠️ Installation

### **Quick Install**
```bash
git clone https://github.com/Khamel83/atlas-voice
cd atlas-voice
pip install click openai sqlite3
export OPENROUTER_API_KEY="your_key_here"
python3 src/main.py --help
```

### **Detailed Setup**
See [SETUP.md](SETUP.md) for complete installation instructions.

---

## 🎯 Usage Examples

### **Professional Voice**
```bash
# Process work emails
python3 src/main.py nuclear-process ~/work/emails

# Generate professional voice
python3 src/main.py generate-voice-prompt

# Use with AI for business communication
```

### **Creative Writing Voice**
```bash
# Process creative writing
python3 src/main.py nuclear-process ~/writing/projects

# Generate creative voice profile
python3 src/main.py generate-voice-prompt --output-dir creative_profiles

# Write stories in your unique style
```

### **Social Media Voice**
```bash
# Process social media content
python3 src/main.py nuclear-process ~/social/exports

# Generate conversational voice
python3 src/main.py generate-voice-prompt

# Create content that sounds like you
```

---

## 🎛️ Commands

### **Smart Interface (Natural Language)**
```bash
python3 src/main.py smart "analyze my emails and create my voice profile"
python3 src/main.py smart --interactive
```

### **Core Processing**
```bash
python3 src/main.py nuclear-process /path/to/data --cleanup-after
python3 src/main.py generate-voice-prompt
python3 src/main.py voice-profiles
```

### **Privacy Management**
```bash
python3 src/main.py privacy-dashboard
python3 src/main.py data-sources
python3 src/main.py privacy-check
```

### **Profile Management**
```bash
python3 src/main.py show-prompt profiles/voice_profile.txt
python3 src/main.py delete-profile profile_name
python3 src/main.py export-prompt profile_name
```

---

## 🔒 Privacy Features

### **Nuclear Safe Room**
- **Room One**: Temporary data processing
- **Airlock**: Cryptographic validation
- **Room Two**: Clean pattern storage

### **Data Minimization**
- Only linguistic patterns extracted
- No content retention
- Statistical analysis only
- Complete deletion capabilities

### **User Control**
- Configurable retention policies
- Automatic cleanup options
- Export and backup controls
- Audit trail logging

---

## 🏗️ Architecture

```
User Data (emails, docs, chats)
          ↓
    🚪 ROOM ONE
    • Process all formats
    • Extract patterns only
    • Calculate checksums
          ↓
    🔐 AIRLOCK
    • Validate integrity
    • Verify completeness
    • Log transfer
          ↓
    🚪 ROOM TWO
    • Store clean patterns
    • No source data
    • Ready for analysis
          ↓
    🎤 YOUR VOICE PROMPT
    • Use with any AI
    • Sound like yourself
    • Privacy guaranteed
```

---

## 📈 Requirements

- **Python 3.8+**
- **OpenRouter API Key** (free tier available)
- **Your writing data** (emails, chats, documents)

---

## 📚 Documentation

- [QUICK_START.md](QUICK_START.md) - Get started in 5 minutes
- [SETUP.md](SETUP.md) - Detailed installation guide
- [NUCLEAR_SAFE_ROOM_DOCS.md](NUCLEAR_SAFE_ROOM_DOCS.md) - Privacy architecture
- [PRIVACY_AUDIT_REPORT.md](PRIVACY_AUDIT_REPORT.md) - Security audit

---

## 🧪 Testing

```bash
# Run privacy checks
python3 src/main.py privacy-check

# Test with demo data
python3 src/nuclear_safe_room.py

# Smart interface test
python3 src/main.py smart "test the system"
```

---

## 🌐 Deployment Ready

**Web application ready:**
- No persistent source data
- Clean database architecture
- Environment variable configuration
- Privacy controls built-in

**Vercel/Netlify compatible:**
- Serverless architecture
- API key management
- Scalable processing
- Privacy compliance

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure privacy compliance
5. Submit a pull request

**Privacy requirements:**
- No user data retention
- Clean architecture
- Audit logging
- Security best practices

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- [Documentation](https://github.com/your-repo/docs)
- [Privacy Policy](https://github.com/your-repo/privacy)
- [Issues](https://github.com/your-repo/issues)
- [Discussions](https://github.com/your-repo/discussions)

---

## 🙏 Acknowledgments

- Privacy-first architecture inspired by security best practices
- LLM integration for intelligent format detection
- OpenAI and OpenRouter for AI capabilities
- Community feedback and testing

---

**🎤 The future of AI communication sounds like you.** ✨

Made with ❤️ for privacy and authenticity.
