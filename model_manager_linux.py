#!/usr/bin/env python3
"""
Ember Model Manager - Linux Version
Handles both local GGUF models and remote API models with Linux path support
"""

import os
import sys
import json
import time
import logging
import traceback
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
import psutil
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Load environment variables
load_dotenv()

class ModelManagerLinux:
    """
    Linux-compatible model manager for local and remote LLM models
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.local_model = None
        self.openai_client = None
        self.is_initialized = False
        self.config = self._load_config()
        self.stats = {
            'total_generations': 0,
            'local_generations': 0,
            'openai_generations': 0,
            'total_tokens': 0,
            'start_time': time.time()
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('ember_model_linux')
        logger.setLevel(logging.INFO)
        
        # Create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        ch.setFormatter(formatter)
        
        # Add the handler to the logger
        if not logger.handlers:
            logger.addHandler(ch)
        
        return logger
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        # Convert Windows path to Linux path if needed
        local_model_path = os.getenv('LOCAL_MODEL_PATH', '')
        if local_model_path.startswith('C:'):
            # Create a Linux-compatible path
            linux_path = local_model_path.replace('C:\\', '/mnt/c/').replace('\\', '/')
            self.logger.info(f"Converted Windows path to Linux: {linux_path}")
            local_model_path = linux_path
        
        # Also check for a local models directory
        local_models_dir = Path('./models')
        if local_models_dir.exists():
            for model_file in local_models_dir.glob('*.gguf'):
                self.logger.info(f"Found local model: {model_file}")
                local_model_path = str(model_file)
                break
        
        config = {
            'local_model_path': local_model_path,
            'use_local_model': os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true',
            'model_name': os.getenv('MODEL_NAME', 'uncensored-jordan-7b'),
            'backup_model': os.getenv('BACKUP_MODEL', 'gpt-4o-mini'),
            'api_key': os.getenv('API_KEY', ''),
            'max_tokens': int(os.getenv('MAX_TOKENS', '4096')),
            'temperature': float(os.getenv('TEMPERATURE', '0.7')),
            'top_p': float(os.getenv('TOP_P', '0.9')),
            'context_length': int(os.getenv('CONTEXT_LENGTH', '8192')),
            'model_threads': int(os.getenv('MODEL_THREADS', '8')),
            'gpu_layers': int(os.getenv('GPU_LAYERS', '0')),  # Set to 0 for CPU only
            'batch_size': int(os.getenv('BATCH_SIZE', '512')),
        }
        
        return config
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_percent': memory.percent,
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_percent': round((disk.used / disk.total) * 100, 2)
            }
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
            return {"error": str(e)}
    
    def _initialize_local_model(self) -> bool:
        """Initialize local GGUF model"""
        local_path = self.config['local_model_path']
        
        if not local_path:
            self.logger.warning("No local model path configured")
            return False
        
        if not os.path.exists(local_path):
            self.logger.error(f"Local model path not found: {local_path}")
            # Try to create a dummy model for testing
            self._create_dummy_model_info()
            return False
        
        try:
            self.logger.info(f"Loading local model from: {local_path}")
            
            # Try to import and initialize llama-cpp-python
            try:
                from llama_cpp import Llama
                
                self.local_model = Llama(
                    model_path=local_path,
                    n_threads=self.config['model_threads'],
                    n_gpu_layers=self.config['gpu_layers'],
                    n_batch=self.config['batch_size'],
                    n_ctx=self.config['context_length'],
                    verbose=False
                )
                
                self.logger.info("✅ Local model loaded successfully")
                return True
                
            except ImportError:
                self.logger.error("llama-cpp-python not installed or not working")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading local model: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _create_dummy_model_info(self):
        """Create dummy model info for testing when no local model exists"""
        self.logger.info("Creating dummy model configuration for testing")
        self.local_model = None  # Will fall back to OpenAI
    
    def _initialize_openai_client(self) -> bool:
        """Initialize OpenAI client"""
        api_key = self.config['api_key']
        
        if not api_key or api_key == 'your_openai_api_key_here':
            self.logger.warning("OpenAI API key not configured")
            return False
        
        try:
            import openai
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.logger.info("✅ OpenAI client initialized")
            return True
            
        except ImportError:
            self.logger.error("OpenAI library not installed")
            return False
        except Exception as e:
            self.logger.error(f"Error initializing OpenAI client: {e}")
            return False
    
    def initialize(self) -> bool:
        """Initialize the model manager"""
        self.logger.info("🚀 Initializing Ember Model Manager (Linux)...")
        
        # Check system resources
        resources = self._check_system_resources()
        self.logger.info(f"System: {resources.get('memory_used_gb', 0):.1f}GB/{resources.get('memory_total_gb', 0):.1f}GB RAM, CPU: {resources.get('cpu_percent', 0):.1f}%")
        
        local_success = False
        openai_success = False
        
        # Try to initialize local model if enabled
        if self.config['use_local_model']:
            local_success = self._initialize_local_model()
        
        # Try to initialize OpenAI client as backup
        openai_success = self._initialize_openai_client()
        
        # Check if at least one model is available
        if local_success or openai_success:
            self.is_initialized = True
            self.logger.info("✅ Model Manager initialized successfully!")
            
            # Log which models are available
            if local_success:
                self.logger.info(f"🔥 Local model: {self.config['model_name']}")
            if openai_success:
                self.logger.info(f"🌐 OpenAI backup: {self.config['backup_model']}")
            
            return True
        else:
            self.logger.error("❌ Failed to initialize any model!")
            return False
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None, 
                 temperature: Optional[float] = None, top_p: Optional[float] = None) -> str:
        """Generate text using available model"""
        if not self.is_initialized:
            raise RuntimeError("Model manager not initialized")
        
        # Use provided parameters or defaults
        max_tokens = max_tokens or self.config['max_tokens']
        temperature = temperature or self.config['temperature']
        top_p = top_p or self.config['top_p']
        
        # Update stats
        self.stats['total_generations'] += 1
        
        # Try local model first if available
        if self.local_model and self.config['use_local_model']:
            try:
                self.logger.info("🔥 Using local model for generation")
                
                response = self.local_model(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    echo=False
                )
                
                generated_text = response['choices'][0]['text']
                self.stats['local_generations'] += 1
                self.stats['total_tokens'] += len(generated_text.split())
                
                return generated_text
                
            except Exception as e:
                self.logger.error(f"Local model generation failed: {e}")
                # Fall back to OpenAI
        
        # Use OpenAI as fallback
        if self.openai_client:
            try:
                self.logger.info("🌐 Using OpenAI for generation")
                
                response = self.openai_client.chat.completions.create(
                    model=self.config['backup_model'],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                
                generated_text = response.choices[0].message.content
                self.stats['openai_generations'] += 1
                self.stats['total_tokens'] += len(generated_text.split())
                
                return generated_text
                
            except Exception as e:
                self.logger.error(f"OpenAI generation failed: {e}")
                raise RuntimeError(f"All generation methods failed: {e}")
        
        raise RuntimeError("No generation method available")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information"""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'local_model_loaded': self.local_model is not None,
            'openai_client_loaded': self.openai_client is not None,
            'config': self.config,
            'system_resources': self._check_system_resources(),
            'stats': {
                **self.stats,
                'uptime_seconds': uptime,
                'uptime_formatted': self._format_uptime(uptime),
                'avg_tokens_per_generation': (
                    self.stats['total_tokens'] / self.stats['total_generations']
                    if self.stats['total_generations'] > 0 else 0
                )
            }
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format"""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    def test_generation(self) -> bool:
        """Test generation capability"""
        try:
            test_prompt = "Hello, this is a test. Please respond with a brief acknowledgment."
            response = self.generate(test_prompt, max_tokens=50)
            
            print(f"\n{Fore.CYAN}=== GENERATION TEST ==={Style.RESET_ALL}")
            print(f"Prompt: {test_prompt}")
            print(f"Response: {response}")
            print(f"{Fore.GREEN}✅ Generation test successful!{Style.RESET_ALL}")
            
            return True
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Generation test failed: {e}{Style.RESET_ALL}")
            return False
    
    def print_status(self):
        """Print current status"""
        info = self.get_model_info()
        
        print(f"\n{Fore.CYAN}=== EMBER MODEL MANAGER STATUS ==={Style.RESET_ALL}")
        print(f"Initialized: {Fore.GREEN}{'Yes' if self.is_initialized else 'No'}{Style.RESET_ALL}")
        print(f"Local Model: {Fore.GREEN}{'Loaded' if info['local_model_loaded'] else 'Not Available'}{Style.RESET_ALL}")
        print(f"OpenAI Client: {Fore.GREEN}{'Loaded' if info['openai_client_loaded'] else 'Not Available'}{Style.RESET_ALL}")
        print(f"Total Generations: {info['stats']['total_generations']}")
        print(f"Local Generations: {info['stats']['local_generations']}")
        print(f"OpenAI Generations: {info['stats']['openai_generations']}")
        print(f"Total Tokens: {info['stats']['total_tokens']}")
        print(f"Uptime: {info['stats']['uptime_formatted']}")
        
        # System resources
        resources = info['system_resources']
        if 'error' not in resources:
            print(f"System Resources:")
            print(f"  CPU: {resources['cpu_percent']:.1f}%")
            print(f"  Memory: {resources['memory_used_gb']:.1f}GB/{resources['memory_total_gb']:.1f}GB ({resources['memory_percent']:.1f}%)")
            print(f"  Disk: {resources['disk_used_gb']:.1f}GB/{resources['disk_total_gb']:.1f}GB ({resources['disk_percent']:.1f}%)")

def main():
    """Main function for testing model manager"""
    print(f"{Fore.YELLOW}🧪 Testing Ember Model Manager (Linux){Style.RESET_ALL}")
    
    manager = ModelManagerLinux()
    
    # Initialize
    if manager.initialize():
        print(f"\n{Fore.GREEN}✅ Model Manager initialized successfully!{Style.RESET_ALL}")
        
        # Print status
        manager.print_status()
        
        # Test generation
        manager.test_generation()
        
    else:
        print(f"\n{Fore.RED}❌ Model Manager initialization failed!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()