#!/usr/bin/env python3
"""
Ember Model Manager
Handles both local GGUF models and remote API models with automatic fallback
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

class ModelManager:
    """
    Comprehensive model manager for local and remote LLM models
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.local_model = None
        self.openai_client = None
        self.model_config = self._load_config()
        self.is_initialized = False
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging with colored output"""
        logger = logging.getLogger('ember_model')
        logger.setLevel(logging.DEBUG if os.getenv('DEBUG', 'false').lower() == 'true' else logging.INFO)
        
        # Create console handler with colored formatter
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} | '
            f'{Fore.YELLOW}%(name)s{Style.RESET_ALL} | '
            f'%(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from environment variables"""
        return {
            'use_local_model': os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true',
            'local_model_path': os.getenv('LOCAL_MODEL_PATH', ''),
            'model_name': os.getenv('MODEL_NAME', 'uncensored-jordan-7b'),
            'backup_model': os.getenv('BACKUP_MODEL', 'gpt-4o-mini'),
            'max_tokens': int(os.getenv('MAX_TOKENS', '4096')),
            'temperature': float(os.getenv('TEMPERATURE', '0.7')),
            'top_p': float(os.getenv('TOP_P', '0.9')),
            'context_length': int(os.getenv('CONTEXT_LENGTH', '8192')),
            'model_threads': int(os.getenv('MODEL_THREADS', '8')),
            'gpu_layers': int(os.getenv('GPU_LAYERS', '32')),
            'batch_size': int(os.getenv('BATCH_SIZE', '512')),
            'api_key': os.getenv('API_KEY', ''),
        }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources for model loading"""
        memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count(logical=False)
        
        return {
            'total_memory_gb': round(memory.total / (1024**3), 2),
            'available_memory_gb': round(memory.available / (1024**3), 2),
            'cpu_cores': cpu_count,
            'memory_usage_percent': memory.percent
        }
    
    def _initialize_local_model(self) -> bool:
        """Initialize local GGUF model"""
        try:
            from llama_cpp import Llama
            
            model_path = self.model_config['local_model_path']
            
            if not model_path or not os.path.exists(model_path):
                self.logger.error(f"Local model path not found: {model_path}")
                return False
            
            # Check system resources
            resources = self._check_system_resources()
            self.logger.info(f"System resources: {resources['available_memory_gb']}GB RAM available, {resources['cpu_cores']} CPU cores")
            
            # Initialize model with optimized parameters
            self.logger.info(f"🔥 Loading local model: {model_path}")
            start_time = time.time()
            
            self.local_model = Llama(
                model_path=model_path,
                n_ctx=self.model_config['context_length'],
                n_threads=self.model_config['model_threads'],
                n_gpu_layers=self.model_config['gpu_layers'],
                n_batch=self.model_config['batch_size'],
                verbose=os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'
            )
            
            load_time = time.time() - start_time
            self.logger.info(f"✅ Local model loaded successfully in {load_time:.2f}s")
            
            # Test the model with a simple prompt
            test_response = self.local_model("Hello", max_tokens=10, temperature=0.1)
            self.logger.info(f"🧪 Model test successful: {test_response['choices'][0]['text'][:50]}...")
            
            return True
            
        except ImportError:
            self.logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            return False
        except Exception as e:
            self.logger.error(f"Failed to load local model: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def _initialize_openai_client(self) -> bool:
        """Initialize OpenAI client"""
        try:
            import openai
            
            api_key = self.model_config['api_key']
            if not api_key or api_key == 'your_openai_api_key_here':
                self.logger.warning("OpenAI API key not configured")
                return False
            
            self.openai_client = openai.OpenAI(api_key=api_key)
            
            # Test the connection
            response = self.openai_client.chat.completions.create(
                model=self.model_config['backup_model'],
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                temperature=0.1
            )
            
            self.logger.info(f"✅ OpenAI client initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            return False
    
    def initialize(self) -> bool:
        """Initialize the model manager"""
        self.logger.info("🚀 Initializing Ember Model Manager...")
        
        local_success = False
        openai_success = False
        
        # Try to initialize local model first if configured
        if self.model_config['use_local_model']:
            local_success = self._initialize_local_model()
        
        # Initialize OpenAI client as backup
        openai_success = self._initialize_openai_client()
        
        if not local_success and not openai_success:
            self.logger.error("❌ Failed to initialize any model!")
            return False
        
        self.is_initialized = True
        
        # Log initialization summary
        primary_model = "Local GGUF" if local_success else "OpenAI API"
        backup_model = "OpenAI API" if local_success else "None"
        
        self.logger.info(f"🎯 Model Manager initialized:")
        self.logger.info(f"   Primary: {primary_model}")
        self.logger.info(f"   Backup: {backup_model}")
        
        return True
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using the available model"""
        if not self.is_initialized:
            raise RuntimeError("Model manager not initialized")
        
        # Set default parameters
        max_tokens = kwargs.get('max_tokens', self.model_config['max_tokens'])
        temperature = kwargs.get('temperature', self.model_config['temperature'])
        top_p = kwargs.get('top_p', self.model_config['top_p'])
        
        # Try local model first
        if self.local_model:
            try:
                response = self.local_model(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                return response['choices'][0]['text']
            except Exception as e:
                self.logger.error(f"Local model failed: {str(e)}")
                
        # Fallback to OpenAI
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.model_config['backup_model'],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                return response.choices[0].message.content
            except Exception as e:
                self.logger.error(f"OpenAI model failed: {str(e)}")
        
        raise RuntimeError("No available models to generate response")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        info = {
            'local_model_loaded': self.local_model is not None,
            'openai_client_loaded': self.openai_client is not None,
            'config': self.model_config,
            'system_resources': self._check_system_resources()
        }
        
        if self.local_model:
            info['local_model_path'] = self.model_config['local_model_path']
        
        return info

def main():
    """Main function for testing the model manager"""
    manager = ModelManager()
    
    if manager.initialize():
        print(f"\n{Fore.GREEN}✅ Model Manager initialized successfully!{Style.RESET_ALL}")
        
        # Display model info
        info = manager.get_model_info()
        print(f"\n{Fore.YELLOW}📊 Model Information:{Style.RESET_ALL}")
        print(f"   Local Model: {'✅' if info['local_model_loaded'] else '❌'}")
        print(f"   OpenAI Client: {'✅' if info['openai_client_loaded'] else '❌'}")
        print(f"   System RAM: {info['system_resources']['available_memory_gb']}GB available")
        
        # Test generation
        try:
            print(f"\n{Fore.CYAN}🧪 Testing model generation...{Style.RESET_ALL}")
            response = manager.generate("Hello! Please introduce yourself briefly.", max_tokens=100)
            print(f"\n{Fore.GREEN}Model Response:{Style.RESET_ALL}")
            print(f"   {response}")
            
        except Exception as e:
            print(f"\n{Fore.RED}❌ Generation test failed: {str(e)}{Style.RESET_ALL}")
    
    else:
        print(f"\n{Fore.RED}❌ Model Manager initialization failed!{Style.RESET_ALL}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())