#!/usr/bin/env python3
"""
Quick Test Script for Ember Components
Tests each component individually to ensure they work
"""

import os
import sys
import time
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

def test_model_manager():
    """Test the model manager"""
    print(f"{Fore.CYAN}🧪 Testing Model Manager...{Style.RESET_ALL}")
    
    try:
        # Try Linux version first
        try:
            from model_manager_linux import ModelManagerLinux
            manager = ModelManagerLinux()
            print(f"  Using Linux model manager")
        except ImportError:
            from model_manager import ModelManager
            manager = ModelManager()
            print(f"  Using standard model manager")
        
        # Initialize
        success = manager.initialize()
        if success:
            print(f"  ✅ Model manager initialized")
            
            # Get info
            info = manager.get_model_info()
            print(f"  Local model: {'✅' if info['local_model_loaded'] else '❌'}")
            print(f"  OpenAI client: {'✅' if info['openai_client_loaded'] else '❌'}")
            
            # Test generation if possible
            try:
                response = manager.generate("Hello, world!", max_tokens=10)
                print(f"  ✅ Generation test: {response[:50]}...")
            except Exception as e:
                print(f"  ❌ Generation test failed: {e}")
                
            return True
        else:
            print(f"  ❌ Model manager initialization failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Model manager test failed: {e}")
        return False

def test_file_monitor():
    """Test the file monitor"""
    print(f"{Fore.CYAN}🧪 Testing File Monitor...{Style.RESET_ALL}")
    
    try:
        from agents.file_monitor import FileMonitor
        
        monitor = FileMonitor()
        print(f"  ✅ File monitor created")
        
        # Test scan
        monitor.scan_existing_files()
        print(f"  ✅ File scan completed")
        
        # Get stats
        stats = monitor.get_statistics()
        print(f"  Files watched: {stats['files_watched']}")
        print(f"  Changes detected: {stats['changes_detected']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ File monitor test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print(f"{Fore.CYAN}🧪 Testing Environment...{Style.RESET_ALL}")
    
    # Check key environment variables
    env_vars = {
        'DEBUG': os.getenv('DEBUG', 'false'),
        'VERBOSE_LOGGING': os.getenv('VERBOSE_LOGGING', 'false'),
        'USE_LOCAL_MODEL': os.getenv('USE_LOCAL_MODEL', 'false'),
        'LOCAL_MODEL_PATH': os.getenv('LOCAL_MODEL_PATH', 'not set'),
        'MODEL_NAME': os.getenv('MODEL_NAME', 'not set'),
        'API_KEY': 'configured' if os.getenv('API_KEY') and os.getenv('API_KEY') != 'your_openai_api_key_here' else 'not configured'
    }
    
    for var, value in env_vars.items():
        print(f"  {var}: {value}")
    
    # Check .env file
    if os.path.exists('.env'):
        print(f"  ✅ .env file exists")
    else:
        print(f"  ❌ .env file missing")
    
    return True

def test_dependencies():
    """Test required dependencies"""
    print(f"{Fore.CYAN}🧪 Testing Dependencies...{Style.RESET_ALL}")
    
    dependencies = [
        'colorama', 'dotenv', 'psutil', 'watchdog',
        'fastapi', 'uvicorn', 'pydantic', 'openai'
    ]
    
    optional_deps = ['llama_cpp']
    
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep.replace('_', '-'))
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} (required)")
            all_good = False
    
    for dep in optional_deps:
        try:
            __import__(dep.replace('_', '-'))
            print(f"  ✅ {dep} (optional)")
        except ImportError:
            print(f"  ⚠️  {dep} (optional - for local models)")
    
    return all_good

def test_api_imports():
    """Test API server imports"""
    print(f"{Fore.CYAN}🧪 Testing API Imports...{Style.RESET_ALL}")
    
    try:
        from fastapi import FastAPI
        print(f"  ✅ FastAPI")
        
        from fastapi.middleware.cors import CORSMiddleware
        print(f"  ✅ CORS Middleware")
        
        from pydantic import BaseModel
        print(f"  ✅ Pydantic")
        
        import uvicorn
        print(f"  ✅ Uvicorn")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API imports failed: {e}")
        return False

def main():
    """Run all tests"""
    print(f"\n{Fore.YELLOW}🔥 EMBER COMPONENT TESTS 🔥{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Environment", test_environment),
        ("API Imports", test_api_imports),
        ("Model Manager", test_model_manager),
        ("File Monitor", test_file_monitor),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{Fore.MAGENTA}🧪 {test_name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*30}{Style.RESET_ALL}")
        
        try:
            result = test_func()
            results[test_name] = result
            
            if result:
                print(f"  {Fore.GREEN}✅ {test_name} PASSED{Style.RESET_ALL}")
            else:
                print(f"  {Fore.RED}❌ {test_name} FAILED{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"  {Fore.RED}❌ {test_name} ERROR: {e}{Style.RESET_ALL}")
            results[test_name] = False
    
    # Summary
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📊 TEST SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Fore.GREEN}✅ PASS" if result else f"{Fore.RED}❌ FAIL"
        print(f"  {status}{Style.RESET_ALL} {test_name}")
    
    print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed{Style.RESET_ALL}")
    
    if passed == total:
        print(f"{Fore.GREEN}🎉 All tests passed! System ready to start.{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.YELLOW}⚠️  Some tests failed. Check the output above.{Style.RESET_ALL}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n{Fore.GREEN}✅ Ready to run: python start_system.py{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}❌ Fix issues before running the full system{Style.RESET_ALL}")
    
    sys.exit(0 if success else 1)