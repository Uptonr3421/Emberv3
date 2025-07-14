#!/usr/bin/env python3
"""
Ember System Startup Script
Orchestrates all components of the Ember AI Assistant system
"""

import os
import sys
import time
import signal
import threading
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

class EmberSystemManager:
    """
    Manages the entire Ember system startup and coordination
    """
    
    def __init__(self):
        self.is_running = False
        self.components = {}
        self.threads = {}
        self.startup_time = None
        self.shutdown_requested = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n{Fore.YELLOW}🔔 Received signal {signum}, initiating shutdown...{Style.RESET_ALL}")
        self.shutdown_requested = True
        self.shutdown_system()
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        print(f"{Fore.CYAN}🔍 Checking dependencies...{Style.RESET_ALL}")
        
        required_modules = [
            'colorama', 'dotenv', 'psutil', 'watchdog', 
            'fastapi', 'uvicorn', 'pydantic', 'llama_cpp', 'openai'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module.replace('_', '-'))
                print(f"  ✅ {module}")
            except ImportError:
                missing_modules.append(module)
                print(f"  ❌ {module}")
        
        if missing_modules:
            print(f"{Fore.RED}Missing dependencies: {', '.join(missing_modules)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Run: pip install {' '.join(missing_modules)}{Style.RESET_ALL}")
            return False
        
        print(f"{Fore.GREEN}✅ All dependencies satisfied{Style.RESET_ALL}")
        return True
    
    def check_environment(self) -> bool:
        """Check environment configuration"""
        print(f"{Fore.CYAN}🔧 Checking environment configuration...{Style.RESET_ALL}")
        
        # Check critical environment variables
        required_vars = ['DEBUG', 'VERBOSE_LOGGING']
        optional_vars = ['API_KEY', 'LOCAL_MODEL_PATH', 'USE_LOCAL_MODEL']
        
        config_ok = True
        
        for var in required_vars:
            if not os.getenv(var):
                print(f"  ❌ {var} not set")
                config_ok = False
            else:
                print(f"  ✅ {var} = {os.getenv(var)}")
        
        for var in optional_vars:
            value = os.getenv(var, 'not set')
            if value == 'not set':
                print(f"  ⚠️  {var} = {value}")
            else:
                print(f"  ✅ {var} = {value}")
        
        # Check for .env file
        env_file = Path('.env')
        if env_file.exists():
            print(f"  ✅ .env file found")
        else:
            print(f"  ⚠️  .env file not found")
        
        return config_ok
    
    def start_file_monitor(self) -> bool:
        """Start the file monitoring system"""
        print(f"{Fore.CYAN}📁 Starting file monitor...{Style.RESET_ALL}")
        
        try:
            def run_file_monitor():
                try:
                    from agents.file_monitor import FileMonitor
                    monitor = FileMonitor()
                    monitor.start_monitoring()
                    self.components['file_monitor'] = monitor
                    
                    # Keep running until shutdown
                    while not self.shutdown_requested:
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"{Fore.RED}❌ File monitor error: {e}{Style.RESET_ALL}")
            
            thread = threading.Thread(target=run_file_monitor, daemon=True)
            thread.start()
            self.threads['file_monitor'] = thread
            
            time.sleep(2)  # Give it time to start
            print(f"{Fore.GREEN}✅ File monitor started{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to start file monitor: {e}{Style.RESET_ALL}")
            return False
    
    def start_model_manager(self) -> bool:
        """Start the model manager"""
        print(f"{Fore.CYAN}🧠 Starting model manager...{Style.RESET_ALL}")
        
        try:
            # Try Linux version first
            try:
                from model_manager_linux import ModelManagerLinux
                manager = ModelManagerLinux()
            except ImportError:
                # Fall back to original version
                from model_manager import ModelManager
                manager = ModelManager()
            
            success = manager.initialize()
            if success:
                self.components['model_manager'] = manager
                print(f"{Fore.GREEN}✅ Model manager started{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Model manager initialization failed{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to start model manager: {e}{Style.RESET_ALL}")
            return False
    
    def start_api_server(self) -> bool:
        """Start the API server"""
        print(f"{Fore.CYAN}🌐 Starting API server...{Style.RESET_ALL}")
        
        try:
            def run_api_server():
                try:
                    # Set environment variables for the server
                    os.environ['PYTHONPATH'] = os.getcwd()
                    
                    # Run the API server
                    cmd = [sys.executable, 'api_server.py']
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=os.getcwd()
                    )
                    
                    self.components['api_server'] = process
                    
                    # Monitor the process
                    while process.poll() is None and not self.shutdown_requested:
                        time.sleep(1)
                    
                except Exception as e:
                    print(f"{Fore.RED}❌ API server error: {e}{Style.RESET_ALL}")
            
            thread = threading.Thread(target=run_api_server, daemon=True)
            thread.start()
            self.threads['api_server'] = thread
            
            time.sleep(3)  # Give it time to start
            print(f"{Fore.GREEN}✅ API server started on http://localhost:8000{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to start API server: {e}{Style.RESET_ALL}")
            return False
    
    def start_preload_system(self) -> bool:
        """Start the preload system"""
        print(f"{Fore.CYAN}⚡ Starting preload system...{Style.RESET_ALL}")
        
        try:
            # Run preload.py
            result = subprocess.run(
                [sys.executable, 'preload.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"{Fore.GREEN}✅ Preload system completed{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Preload system failed: {result.stderr}{Style.RESET_ALL}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"{Fore.RED}❌ Preload system timed out{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to start preload system: {e}{Style.RESET_ALL}")
            return False
    
    def start_system(self) -> bool:
        """Start the entire Ember system"""
        print(f"\n{Fore.YELLOW}🔥 STARTING EMBER AI ASSISTANT SYSTEM 🔥{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        self.startup_time = time.time()
        
        # Pre-flight checks
        if not self.check_dependencies():
            return False
        
        if not self.check_environment():
            print(f"{Fore.YELLOW}⚠️  Environment check failed, continuing anyway...{Style.RESET_ALL}")
        
        # Start components in order
        components_to_start = [
            ('preload_system', self.start_preload_system),
            ('model_manager', self.start_model_manager),
            ('file_monitor', self.start_file_monitor),
            ('api_server', self.start_api_server),
        ]
        
        for component_name, start_func in components_to_start:
            if not start_func():
                print(f"{Fore.RED}❌ Failed to start {component_name}{Style.RESET_ALL}")
                return False
            time.sleep(1)
        
        self.is_running = True
        startup_duration = time.time() - self.startup_time
        
        print(f"\n{Fore.GREEN}✅ EMBER SYSTEM STARTED SUCCESSFULLY!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🕐 Startup time: {startup_duration:.2f} seconds{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🌐 API Documentation: http://localhost:8000/docs{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💚 System Health: http://localhost:8000/health{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 System Status: http://localhost:8000/status{Style.RESET_ALL}")
        
        return True
    
    def shutdown_system(self):
        """Shutdown the entire system"""
        if not self.is_running:
            return
        
        print(f"\n{Fore.YELLOW}🔄 Shutting down Ember system...{Style.RESET_ALL}")
        
        self.shutdown_requested = True
        
        # Stop components
        for name, component in self.components.items():
            print(f"  Stopping {name}...")
            try:
                if hasattr(component, 'stop_monitoring'):
                    component.stop_monitoring()
                elif hasattr(component, 'terminate'):
                    component.terminate()
                elif hasattr(component, 'close'):
                    component.close()
            except Exception as e:
                print(f"    Error stopping {name}: {e}")
        
        # Wait for threads to complete
        for name, thread in self.threads.items():
            if thread.is_alive():
                print(f"  Waiting for {name} thread...")
                thread.join(timeout=5)
        
        self.is_running = False
        print(f"{Fore.GREEN}✅ Ember system shutdown complete{Style.RESET_ALL}")
    
    def run_monitoring_loop(self):
        """Run the main monitoring loop"""
        if not self.is_running:
            return
        
        print(f"\n{Fore.CYAN}📊 Starting monitoring loop...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop the system{Style.RESET_ALL}")
        
        try:
            while self.is_running and not self.shutdown_requested:
                # Print status every 30 seconds
                time.sleep(30)
                
                if self.is_running:
                    uptime = time.time() - self.startup_time
                    hours, remainder = divmod(uptime, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    print(f"\n{Fore.CYAN}🔥 Ember System Status{Style.RESET_ALL}")
                    print(f"  Uptime: {int(hours)}h {int(minutes)}m {int(seconds)}s")
                    print(f"  Components: {len(self.components)} running")
                    print(f"  Threads: {len([t for t in self.threads.values() if t.is_alive()])} active")
                    
                    # Check component health
                    for name, component in self.components.items():
                        if hasattr(component, 'is_running'):
                            status = "🟢" if component.is_running else "🔴"
                        else:
                            status = "🟡"
                        print(f"  {status} {name}")
                        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🔔 Received keyboard interrupt{Style.RESET_ALL}")
        finally:
            self.shutdown_system()

def main():
    """Main function"""
    print(f"{Fore.MAGENTA}🚀 Ember AI Assistant System Launcher{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Version: 3.0.0{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Platform: Linux{Style.RESET_ALL}")
    
    manager = EmberSystemManager()
    
    if manager.start_system():
        manager.run_monitoring_loop()
    else:
        print(f"{Fore.RED}❌ Failed to start Ember system{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()