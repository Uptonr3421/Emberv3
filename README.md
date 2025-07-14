---
title: Emberv3 AI Assistant with Jordan-7B
emoji: 🔥
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 4.8.0
app_file: app.py
pinned: false
license: mit
python_version: 3.10
hardware: t4-medium
---

# 🔥 Emberv3 AI Assistant Framework

**Production-ready AI system with uncensored Jordan-7B model**

## 🚀 Features

- **Uncensored Jordan-7B Model** - No guardrails, maximum freedom
- **FastAPI REST Server** - Full API endpoints
- **Real-time Streaming** - Live response generation
- **File Monitoring** - Automatic context updates
- **System Orchestration** - Multi-component management

## � Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd emberv3

# Install dependencies
pip install -r requirements.txt

# Add your Jordan-7B model to models/
# Update .env with your model path

# Run the system
python start_system.py
```

## ☁️ Cloud Deployment

### Option 1: Hugging Face Spaces (Recommended)
1. Fork this repository
2. Upload your Jordan-7B model to `models/`
3. Deploy as a Space with GPU hardware
4. Cost: ~$0.60/hour

### Option 2: Runpod
1. Create GPU instance
2. Clone repository
3. Upload model and run

## 🔧 Configuration

Update `.env` with your model path:
```env
LOCAL_MODEL_PATH=models/uncensored-jordan-7b.gguf
USE_LOCAL_MODEL=true
MODEL_NAME=uncensored-jordan-7b
```

## 📊 System Requirements

- **RAM**: 16GB+ recommended
- **GPU**: 8GB+ VRAM (optional but recommended)
- **Storage**: 20GB+ for model and system

## �️ API Endpoints

- `GET /` - System status
- `POST /generate` - Text generation
- `GET /health` - Health check
- `GET /models` - Model information

## 🎯 Production Ready

This system is battle-tested and ready for production deployment with:
- ✅ Error handling
- ✅ Logging and monitoring  
- ✅ Resource management
- ✅ API rate limiting
- ✅ Health checks

---

**Ready to deploy your uncensored AI assistant!** 🚀