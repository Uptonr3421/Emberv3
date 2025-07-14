#!/usr/bin/env python3
"""
Create Demo Model for Ember System
Downloads a small GGUF model for testing
"""

import os
import sys
import urllib.request
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def download_demo_model():
    """Download a small demo model"""
    print(f"{Fore.CYAN}📥 Downloading demo model...{Style.RESET_ALL}")
    
    # Create models directory
    models_dir = Path('./models')
    models_dir.mkdir(exist_ok=True)
    
    # Small demo model (example - this is a placeholder URL)
    model_url = "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
    model_name = "phi-3-mini-4k-instruct-q4.gguf"
    model_path = models_dir / model_name
    
    if model_path.exists():
        print(f"  ✅ Model already exists: {model_path}")
        return str(model_path)
    
    print(f"  🌐 Downloading from: {model_url}")
    print(f"  📁 Saving to: {model_path}")
    print(f"  ⚠️  This may take a while...")
    
    try:
        # Download with progress
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"  📊 Progress: {percent}%", end='\r')
        
        urllib.request.urlretrieve(model_url, model_path, progress_hook)
        print(f"\n  ✅ Model downloaded successfully!")
        return str(model_path)
        
    except Exception as e:
        print(f"\n  ❌ Download failed: {e}")
        return None

def create_mock_model():
    """Create a mock model file for testing"""
    print(f"{Fore.CYAN}🎭 Creating mock model for testing...{Style.RESET_ALL}")
    
    models_dir = Path('./models')
    models_dir.mkdir(exist_ok=True)
    
    mock_model_path = models_dir / "mock-model.gguf"
    
    # Create a simple mock file
    with open(mock_model_path, 'w') as f:
        f.write("# This is a mock GGUF model for testing\n")
        f.write("# Real models are binary files and much larger\n")
        f.write("# This allows the system to test path resolution\n")
    
    print(f"  ✅ Mock model created: {mock_model_path}")
    return str(mock_model_path)

def update_env_for_demo():
    """Update .env file for demo configuration"""
    print(f"{Fore.CYAN}🔧 Updating .env for demo...{Style.RESET_ALL}")
    
    # Check if we have any models
    models_dir = Path('./models')
    model_files = list(models_dir.glob('*.gguf')) if models_dir.exists() else []
    
    if model_files:
        model_path = str(model_files[0])
        print(f"  📁 Using model: {model_path}")
        use_local = "true"
    else:
        # Create mock model
        model_path = create_mock_model()
        use_local = "false"  # Since it's just a mock
    
    # Read current .env
    env_content = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.readlines()
    
    # Update or add configuration
    updated_content = []
    updated_vars = set()
    
    for line in env_content:
        if line.strip().startswith('LOCAL_MODEL_PATH='):
            updated_content.append(f'LOCAL_MODEL_PATH={model_path}\n')
            updated_vars.add('LOCAL_MODEL_PATH')
        elif line.strip().startswith('USE_LOCAL_MODEL='):
            updated_content.append(f'USE_LOCAL_MODEL={use_local}\n')
            updated_vars.add('USE_LOCAL_MODEL')
        elif line.strip().startswith('MODEL_NAME='):
            updated_content.append(f'MODEL_NAME=demo-model\n')
            updated_vars.add('MODEL_NAME')
        else:
            updated_content.append(line)
    
    # Add missing variables
    if 'LOCAL_MODEL_PATH' not in updated_vars:
        updated_content.append(f'LOCAL_MODEL_PATH={model_path}\n')
    if 'USE_LOCAL_MODEL' not in updated_vars:
        updated_content.append(f'USE_LOCAL_MODEL={use_local}\n')
    if 'MODEL_NAME' not in updated_vars:
        updated_content.append(f'MODEL_NAME=demo-model\n')
    
    # Write updated .env
    with open('.env', 'w') as f:
        f.writelines(updated_content)
    
    print(f"  ✅ .env updated")
    print(f"  📝 LOCAL_MODEL_PATH={model_path}")
    print(f"  📝 USE_LOCAL_MODEL={use_local}")
    print(f"  📝 MODEL_NAME=demo-model")

def main():
    """Main function"""
    print(f"{Fore.YELLOW}🎯 Setting up Ember Demo Configuration{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    # Try to download a real model first
    print(f"\n{Fore.MAGENTA}Option 1: Download real model{Style.RESET_ALL}")
    model_path = download_demo_model()
    
    if not model_path:
        print(f"\n{Fore.MAGENTA}Option 2: Use mock model{Style.RESET_ALL}")
        model_path = create_mock_model()
    
    # Update environment
    update_env_for_demo()
    
    print(f"\n{Fore.GREEN}✅ Demo configuration complete!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📋 Next steps:{Style.RESET_ALL}")
    print(f"  1. Run: python quick_test.py")
    print(f"  2. If tests pass, run: python start_system.py")
    print(f"  3. Or manually test: python model_manager_linux.py")
    
    print(f"\n{Fore.YELLOW}💡 Note: For real local models, place .gguf files in the models/ directory{Style.RESET_ALL}")

if __name__ == "__main__":
    main()