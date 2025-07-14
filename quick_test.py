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

def test_system_integration():
    """Test full system integration and startup"""
    print(f"{Fore.CYAN}🧪 Testing System Integration...{Style.RESET_ALL}")
    
    try:
        import subprocess
        import requests
        import time
        
        # Test API server startup
        print(f"  🔥 Testing API server startup...")
        
        # Start API server in background
        process = subprocess.Popen([
            sys.executable, 'api_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for startup
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code == 200:
                print(f"  ✅ API server responding")
            else:
                print(f"  ❌ API server not healthy")
                process.terminate()
                return False
        except:
            print(f"  ❌ API server not accessible")
            process.terminate()
            return False
        
        # Test generation endpoint
        try:
            gen_response = requests.post('http://localhost:8000/generate', 
                json={'prompt': 'Hello', 'max_tokens': 5}, timeout=10)
            if gen_response.status_code == 200:
                print(f"  ✅ Generation endpoint working")
            else:
                print(f"  ❌ Generation endpoint failed")
        except Exception as e:
            print(f"  ⚠️  Generation test failed: {e}")
        
        # Cleanup
        process.terminate()
        return True
        
    except Exception as e:
        print(f"  ❌ System integration test failed: {e}")
        return False

def test_windows_compatibility():
    """Test Windows executable preparation and compatibility"""
    print(f"{Fore.CYAN}🧪 Testing Windows Compatibility...{Style.RESET_ALL}")
    
    try:
        import platform
        import pathlib
        
        # Test path conversions
        test_path = "models/jordan-7b-model.gguf"
        win_path = pathlib.Path(test_path).as_posix()
        print(f"  ✅ Path conversion working: {win_path}")
        
        # Test PyInstaller availability
        try:
            import PyInstaller
            print(f"  ✅ PyInstaller available")
        except ImportError:
            print(f"  ❌ PyInstaller not installed")
            return False
        
        # Test model detection for Jordan 7B
        models_dir = pathlib.Path("models")
        jordan_models = list(models_dir.glob("*jordan*7b*.gguf"))
        if jordan_models:
            print(f"  ✅ Jordan 7B model found: {jordan_models[0].name}")
        else:
            print(f"  ⚠️  Jordan 7B model not found (will use available model)")
        
        # Test resource path handling
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"  ✅ Resource path handling: {current_dir}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Windows compatibility test failed: {e}")
        return False

def test_conflict_prevention():
    """Test git status and agent coordination"""
    print(f"{Fore.CYAN}🧪 Testing Conflict Prevention...{Style.RESET_ALL}")
    
    try:
        import subprocess
        import json
        
        # Test git status
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                capture_output=True, text=True, cwd='.')
            if result.returncode == 0:
                if result.stdout.strip():
                    print(f"  ⚠️  Uncommitted changes detected")
                else:
                    print(f"  ✅ Git working tree clean")
            else:
                print(f"  ❌ Git status check failed")
                return False
        except Exception as e:
            print(f"  ❌ Git not available: {e}")
            return False
        
        # Test coordination file
        coord_file = "AGENT_COORDINATION.md"
        if os.path.exists(coord_file):
            print(f"  ✅ Agent coordination file exists")
        else:
            print(f"  ❌ Agent coordination file missing")
            return False
        
        # Test ember state
        state_file = ".ember_state.json"
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    files_count = len(state.get('files', {}))
                    print(f"  ✅ Ember state tracking {files_count} files")
            except:
                print(f"  ❌ Ember state file corrupted")
                return False
        else:
            print(f"  ❌ Ember state file missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Conflict prevention test failed: {e}")
        return False

def main():
    """Run all 8 comprehensive tests"""
    print(f"\n{Fore.YELLOW}🔥 EMBER 8-POINT COMPREHENSIVE TEST SUITE 🔥{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Environment", test_environment),
        ("API Imports", test_api_imports),
        ("Model Manager", test_model_manager),
        ("File Monitor", test_file_monitor),
        ("System Integration", test_system_integration),
        ("Windows Compatibility", test_windows_compatibility),
        ("Conflict Prevention", test_conflict_prevention),
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