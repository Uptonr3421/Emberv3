# 🚀 Deployment Guide for Jordan-7B on Hugging Face Spaces

## 📋 Prerequisites

- Your Jordan-7B model file (`uncensored-jordan-7b.gguf`)
- Hugging Face account (free)
- Git installed on your system

## 🔧 Step-by-Step Deployment

### 1. Prepare Your Model
First, upload your Jordan-7B model to Hugging Face:

```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login to Hugging Face
huggingface-cli login

# Upload your model (replace with your model path)
huggingface-cli upload your-username/jordan-7b-model ./path/to/uncensored-jordan-7b.gguf
```

### 2. Fork This Repository
1. Fork this repository to your GitHub account
2. Clone your fork locally
3. Add your model to the `models/` directory

### 3. Update Configuration
Edit `.env` file to match your model:
```env
LOCAL_MODEL_PATH=models/uncensored-jordan-7b.gguf
USE_LOCAL_MODEL=true
MODEL_NAME=uncensored-jordan-7b
```

### 4. Create Hugging Face Space
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in details:
   - **Space name**: `your-username/emberv3-jordan-7b`
   - **License**: MIT
   - **SDK**: Gradio
   - **Hardware**: **t4-medium** (GPU required)
   - **Visibility**: Public or Private

### 5. Deploy to Spaces
```bash
# Clone your new space
git clone https://huggingface.co/spaces/your-username/emberv3-jordan-7b
cd emberv3-jordan-7b

# Copy all files from this repository
cp -r /path/to/emberv3/* .

# Add your model file
cp /path/to/uncensored-jordan-7b.gguf models/

# Commit and push
git add .
git commit -m "Deploy Emberv3 with Jordan-7B model"
git push
```

### 6. Space Configuration
Your space should automatically detect the configuration from `README.md`:
- **Hardware**: t4-medium (GPU)
- **Python**: 3.10
- **SDK**: Gradio 4.8.0
- **App file**: app.py

## 💰 Cost Breakdown

### Hugging Face Spaces Pricing
- **t4-medium**: $0.60/hour
- **t4-large**: $1.20/hour  
- **A10G**: $3.15/hour

### Monthly Costs (24/7 operation)
- **t4-medium**: ~$432/month
- **t4-large**: ~$864/month

**💡 Cost-saving tip**: Set up auto-sleep when inactive to reduce costs!

## 🎯 Alternative Deployment Options

### Option 1: Runpod (More Control)
```bash
# Rent GPU instance
1. Go to runpod.io
2. Create account
3. Select GPU (RTX 4090 recommended)
4. Upload your model and code
5. Run: python app.py
```

### Option 2: Modal (Serverless)
```bash
# Install Modal
pip install modal

# Deploy as serverless function
modal deploy modal_deployment.py
```

### Option 3: Your Own Server
```bash
# Requirements
- 16GB+ RAM
- 8GB+ GPU (RTX 3080+ recommended)
- Ubuntu 20.04+

# Setup
git clone your-repo
cd emberv3
pip install -r requirements.txt
python app.py
```

## 🔍 Monitoring & Maintenance

### Health Checks
Your deployed space will have:
- `/health` endpoint for monitoring
- Real-time logs in Hugging Face interface
- Resource usage tracking

### Updating the Model
```bash
# Update model in space
git pull origin main
cp /path/to/new-model.gguf models/
git add models/
git commit -m "Update Jordan model"
git push
```

## 🚨 Troubleshooting

### Common Issues

1. **Model Loading Failed**
   - Check model path in `.env`
   - Verify model file exists in `models/`
   - Ensure sufficient GPU memory

2. **Out of Memory**
   - Upgrade to t4-large or A10G
   - Reduce batch size in `.env`
   - Use smaller quantization

3. **Slow Response**
   - Check GPU utilization
   - Reduce max_tokens
   - Optimize model parameters

### Debug Commands
```bash
# Check model loading
python -c "from model_manager_linux import ModelManagerLinux; m = ModelManagerLinux(); print(m.initialize())"

# Test generation
python -c "from model_manager_linux import ModelManagerLinux; m = ModelManagerLinux(); m.initialize(); print(m.generate('Hello'))"
```

## 🔐 Security Considerations

- Your model is **uncensored** - use responsibly
- Consider private spaces for sensitive use cases
- Monitor usage logs regularly
- Set up proper access controls

## 📊 Performance Optimization

### Model Settings
```env
# Optimized for t4-medium
MODEL_THREADS=4
GPU_LAYERS=32
BATCH_SIZE=256
CONTEXT_LENGTH=4096
```

### Gradio Settings
```python
# In app.py
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True,
    debug=False,
    max_threads=4  # Optimize for your hardware
)
```

---

## 🎉 Ready to Deploy!

Your Jordan-7B model is now ready for deployment! 

**Next steps:**
1. Upload model to Hugging Face
2. Create Space with GPU hardware
3. Deploy and test
4. Monitor performance

**Questions?** Check the main README.md or open an issue!

---

**🔥 Emberv3 + Jordan-7B = Uncensored AI Power!** 🚀