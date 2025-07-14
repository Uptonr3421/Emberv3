# Emberv3 AI Assistant Framework

![Emberv3](https://img.shields.io/badge/Emberv3-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Async%20API-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **A sophisticated, production-ready AI Assistant Framework featuring local LLM integration, real-time monitoring, and collaborative agent architecture.**

## 🌟 **Features**

### 🤖 **AI & Model Management**
- **Local LLM Support**: Phi-3 model with GGUF format
- **Dual Model System**: Local + OpenAI API fallback
- **Real-time Generation**: Streaming text generation
- **Resource Monitoring**: CPU, memory, disk usage tracking
- **Performance Metrics**: Generation speed and token statistics

### 🔧 **System Architecture**
- **Multi-Agent System**: Collaborative background agents
- **Real-time File Monitoring**: Automatic project state tracking
- **REST API Server**: FastAPI with auto-generated documentation
- **Background Processing**: Threaded component management
- **System Orchestration**: One-command startup and shutdown

### 🎯 **Production Ready**
- **Comprehensive Testing**: 5-component test suite
- **Error Handling**: Graceful degradation and recovery
- **Logging System**: Structured logging with timestamps
- **Health Monitoring**: System status and diagnostic endpoints
- **Docker Support**: Containerized deployment ready

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.13+
- Linux/WSL environment
- 8GB+ RAM recommended
- 4GB+ disk space for models

### **Installation**
```bash
# Clone repository
git clone https://github.com/Uptonr3421/Emberv3.git
cd Emberv3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements_complete.txt

# Download AI model
python create_demo_model.py
```

### **Configuration**
Create/edit `.env` file:
```env
# Model Configuration
USE_LOCAL_MODEL=true
LOCAL_MODEL_PATH=models/phi-3-mini-4k-instruct-q4.gguf
MODEL_NAME=demo-model

# API Configuration
API_HOST=localhost
API_PORT=8000

# System Configuration
DEBUG=true
VERBOSE_LOGGING=true
MAX_TOKENS=2048
TEMPERATURE=0.7
```

### **Running the System**
```bash
# Run comprehensive tests
python quick_test.py

# Start the complete system
python start_system.py

# Or run components individually
python api_server.py          # REST API server
python model_manager_linux.py # Model manager only
```

## 🏗️ **Architecture Overview**

```
Emberv3 AI Assistant Framework
├── 🧠 Model Manager (model_manager_linux.py)
│   ├── Local LLM Integration (llama-cpp-python)
│   ├── OpenAI API Fallback
│   └── Performance Monitoring
├── 🌐 API Server (api_server.py)
│   ├── FastAPI REST Endpoints
│   ├── Streaming Generation
│   └── Health Monitoring
├── 👥 Agent System (agents/)
│   ├── File Monitor (file_monitor.py)
│   └── Background Processing
├── 🔧 System Orchestration (start_system.py)
│   ├── Multi-component Startup
│   ├── Dependency Validation
│   └── Graceful Shutdown
└── 🧪 Testing Framework (quick_test.py)
    ├── Component Testing
    ├── Integration Testing
    └── Performance Validation
```

## 📊 **API Documentation**

### **Generation Endpoints**
```bash
# Text generation
POST /generate
{
  "prompt": "Hello, how are you?",
  "max_tokens": 100,
  "temperature": 0.7
}

# Streaming generation
POST /generate/stream
{
  "prompt": "Tell me a story",
  "max_tokens": 500
}
```

### **System Endpoints**
```bash
# Health check
GET /health

# System status
GET /status

# Admin statistics
GET /admin/stats
```

### **Interactive Documentation**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔍 **Testing & Validation**

### **Test Suite Results**
```
🔥 EMBER COMPONENT TESTS 🔥
✅ Dependencies    - All packages installed
✅ Environment     - Configuration loaded
✅ API Imports     - FastAPI components working
✅ Model Manager   - Local Phi-3 model operational
✅ File Monitor    - 22 files tracked
```

### **Performance Metrics**
- **Generation Speed**: 1-2 tokens/second
- **Memory Usage**: ~4GB with Phi-3 model
- **API Response Time**: <100ms (excluding generation)
- **File Monitor**: Real-time change detection

## 🛠️ **Development**

### **Project Structure**
```
Emberv3/
├── agents/                    # Background agents
│   ├── __init__.py
│   └── file_monitor.py       # File system monitoring
├── models/                   # AI models directory
│   ├── README.md
│   └── *.gguf               # Local models (gitignored)
├── venv/                    # Virtual environment
├── .cursorrules             # Hive mind agent rules
├── .env                     # Environment configuration
├── api_server.py            # FastAPI REST server
├── model_manager_linux.py   # Linux model manager
├── start_system.py          # System orchestration
├── quick_test.py            # Testing framework
└── requirements_complete.txt # Dependencies
```

### **Development Guidelines**
- **Main Branch Only**: No feature branches
- **Hive Mind Collaboration**: Multi-agent development
- **Test-Driven**: All changes tested before deployment
- **Documentation First**: Comprehensive docs for all features

### **Adding New Components**
1. Create component in appropriate directory
2. Add to `start_system.py` orchestration
3. Include in `quick_test.py` test suite
4. Update documentation and README

## 🔧 **Configuration Reference**

### **Environment Variables**
| Variable | Description | Default |
|----------|-------------|---------|
| `USE_LOCAL_MODEL` | Enable local model | `true` |
| `LOCAL_MODEL_PATH` | Path to GGUF model | `models/phi-3-mini-4k-instruct-q4.gguf` |
| `API_HOST` | API server host | `localhost` |
| `API_PORT` | API server port | `8000` |
| `DEBUG` | Enable debug logging | `false` |
| `MAX_TOKENS` | Maximum generation tokens | `2048` |
| `TEMPERATURE` | Generation temperature | `0.7` |

### **Model Configuration**
- **Supported Formats**: GGUF, GGML
- **Recommended Models**: Phi-3, Llama-2, Mistral
- **Memory Requirements**: 4GB+ for 7B parameter models
- **Performance**: CPU-optimized inference

## 🚨 **Troubleshooting**

### **Common Issues**
1. **Model Not Found**: Run `python create_demo_model.py`
2. **Memory Issues**: Reduce model size or increase system RAM
3. **Port Conflicts**: Change `API_PORT` in `.env`
4. **Permission Errors**: Ensure proper file permissions

### **Debug Mode**
```bash
# Enable verbose logging
export DEBUG=true
export VERBOSE_LOGGING=true

# Run with debug output
python start_system.py
```

### **Log Locations**
- **System Logs**: Console output with timestamps
- **Error Logs**: Captured in application logs
- **Performance Metrics**: Available via `/admin/stats`

## 🤝 **Contributing**

### **Development Workflow**
1. Fork repository
2. Work on main branch (no feature branches)
3. Run test suite: `python quick_test.py`
4. Submit pull request

### **Code Standards**
- **Python**: PEP 8 compliance
- **Documentation**: Comprehensive docstrings
- **Testing**: All new features tested
- **Error Handling**: Graceful failure modes

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 **Links**

- **Documentation**: [README.md](README.md)
- **API Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/Uptonr3421/Emberv3
- **Issues**: https://github.com/Uptonr3421/Emberv3/issues

---

**Built with ❤️ by the Emberv3 Development Team**

*Powered by Phi-3, FastAPI, and cutting-edge AI technology*