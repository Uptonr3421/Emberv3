#!/usr/bin/env python3
"""
🔥 Ember AI Assistant - Jordan 7B Autonomous Agent Swarm System
Complete system with real-time monitoring, autonomous agent management, and conflict prevention
"""

import os
import sys
import multiprocessing
import time
import webbrowser
import subprocess
import json
import threading
import queue
from pathlib import Path
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import psutil

# Configure logging for swarm coordination
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ember_swarm")

class AgentSwarmOrchestrator:
    """Autonomous agent swarm orchestration system"""
    
    def __init__(self):
        self.active_agents = {}
        self.communication_queue = queue.Queue()
        self.system_health = {"status": "healthy", "issues": []}
        self.debug_loops = {}
        self.real_time_monitor = None
        self.coordination_lock = threading.Lock()
        
    def start_real_time_monitoring(self):
        """Start real-time code change monitoring"""
        logger.info("🔍 Starting real-time code monitoring...")
        
        def monitor_changes():
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class CodeChangeHandler(FileSystemEventHandler):
                def __init__(self, orchestrator):
                    self.orchestrator = orchestrator
                    
                def on_modified(self, event):
                    if event.is_directory:
                        return
                        
                    if event.src_path.endswith(('.py', '.json', '.md')):
                        self.orchestrator.handle_code_change(event.src_path)
            
            observer = Observer()
            observer.schedule(CodeChangeHandler(self), ".", recursive=True)
            observer.start()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
        
        self.real_time_monitor = threading.Thread(target=monitor_changes, daemon=True)
        self.real_time_monitor.start()
        
    def handle_code_change(self, file_path):
        """Handle real-time code changes and prevent conflicts"""
        with self.coordination_lock:
            logger.info(f"📝 Code change detected: {file_path}")
            
            # Check if multiple agents are working on same file
            working_agents = [agent for agent, info in self.active_agents.items() 
                            if file_path in info.get('working_files', [])]
            
            if len(working_agents) > 1:
                logger.warning(f"⚠️  CONFLICT DETECTED: {len(working_agents)} agents on {file_path}")
                self.resolve_file_conflict(file_path, working_agents)
                
            # Update system state
            self.update_ember_state()
            
    def resolve_file_conflict(self, file_path, conflicting_agents):
        """Resolve conflicts when multiple agents work on same file"""
        logger.info(f"🔧 Resolving conflict for {file_path}")
        
        # Prioritize agents based on criticality
        priority_order = ["jordan_main", "model_manager", "api_server", "file_monitor"]
        
        primary_agent = None
        for priority in priority_order:
            for agent in conflicting_agents:
                if priority in agent:
                    primary_agent = agent
                    break
            if primary_agent:
                break
        
        if not primary_agent:
            primary_agent = conflicting_agents[0]
            
        # Route other agents to assist or other tasks
        helper_agents = [a for a in conflicting_agents if a != primary_agent]
        
        logger.info(f"👑 Primary agent: {primary_agent}")
        logger.info(f"🤝 Helper agents: {helper_agents}")
        
        # Send coordination messages
        self.send_agent_message({
            "type": "conflict_resolution",
            "primary_agent": primary_agent,
            "helper_agents": helper_agents,
            "file": file_path,
            "action": "coordinate"
        })
        
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register a new agent in the swarm"""
        with self.coordination_lock:
            self.active_agents[agent_id] = {
                **agent_info,
                "start_time": time.time(),
                "last_heartbeat": time.time(),
                "status": "active"
            }
            logger.info(f"🤖 Agent registered: {agent_id}")
            
    def autonomous_agent_management(self):
        """Autonomously manage agent lifecycle based on system needs"""
        logger.info("🧠 Starting autonomous agent management...")
        
        def management_loop():
            while True:
                try:
                    # Check system load and needs
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    # Determine if we need more or fewer agents
                    if cpu_percent > 80 and len(self.active_agents) > 3:
                        self.shutdown_non_critical_agents()
                    elif cpu_percent < 30 and len(self.system_health["issues"]) > 0:
                        self.spin_up_helper_agents()
                        
                    # Check for stuck agents in debug loops
                    self.check_debug_loops()
                    
                    # Agent health check
                    self.health_check_agents()
                    
                    time.sleep(10)  # Check every 10 seconds
                    
                except Exception as e:
                    logger.error(f"❌ Agent management error: {e}")
                    time.sleep(5)
        
        management_thread = threading.Thread(target=management_loop, daemon=True)
        management_thread.start()
        
    def spin_up_helper_agents(self):
        """Autonomously spin up additional agents when needed"""
        logger.info("🚀 Spinning up helper agents...")
        
        issues = self.system_health["issues"]
        needed_agents = []
        
        for issue in issues:
            if "model" in issue.lower():
                needed_agents.append("model_specialist")
            elif "api" in issue.lower():
                needed_agents.append("api_specialist")
            elif "file" in issue.lower():
                needed_agents.append("file_specialist")
            elif "test" in issue.lower():
                needed_agents.append("test_specialist")
                
        for agent_type in set(needed_agents):
            if agent_type not in self.active_agents:
                self.create_specialist_agent(agent_type)
                
    def shutdown_non_critical_agents(self):
        """Shutdown non-critical agents to reduce resource usage"""
        logger.info("⏹️  Shutting down non-critical agents...")
        
        critical_agents = ["jordan_main", "model_manager", "api_server"]
        
        for agent_id in list(self.active_agents.keys()):
            if not any(critical in agent_id for critical in critical_agents):
                if self.active_agents[agent_id]["status"] == "idle":
                    logger.info(f"⏹️  Shutting down idle agent: {agent_id}")
                    del self.active_agents[agent_id]
                    
    def check_debug_loops(self):
        """Detect and break debug loops"""
        current_time = time.time()
        
        for agent_id, agent_info in self.active_agents.items():
            if agent_info.get("task") == "debugging":
                debug_start = self.debug_loops.get(agent_id, current_time)
                
                if current_time - debug_start > 300:  # 5 minutes in debug
                    logger.warning(f"🔄 Debug loop detected for {agent_id}")
                    self.break_debug_loop(agent_id)
                else:
                    self.debug_loops[agent_id] = debug_start
                    
    def break_debug_loop(self, agent_id):
        """Break an agent out of a debug loop"""
        logger.info(f"🛑 Breaking debug loop for {agent_id}")
        
        self.send_agent_message({
            "type": "break_debug_loop",
            "agent_id": agent_id,
            "action": "reset_task",
            "new_task": "assist_others"
        })
        
        # Reset debug loop tracker
        if agent_id in self.debug_loops:
            del self.debug_loops[agent_id]
            
    def send_agent_message(self, message: Dict[str, Any]):
        """Send message to agent communication system"""
        message["timestamp"] = time.time()
        self.communication_queue.put(message)
        
        # Also write to coordination file for persistence
        with open("AGENT_COORDINATION.md", "a") as f:
            f.write(f"\n### 📨 System Message: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"```json\n{json.dumps(message, indent=2)}\n```\n")
            
    def update_ember_state(self):
        """Update ember state with current agent status"""
        try:
            with open(".ember_state.json", "r") as f:
                state = json.load(f)
                
            state["agent_swarm"] = {
                "active_agents": len(self.active_agents),
                "system_health": self.system_health,
                "last_update": time.time()
            }
            
            with open(".ember_state.json", "w") as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.warning(f"⚠️  Could not update ember state: {e}")

def setup_jordan_environment():
    """Setup environment optimized for Jordan 7B model"""
    logger.info("🔥 Setting up Jordan 7B environment...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, "models")
    
    os.makedirs(models_dir, exist_ok=True)
    
    # Environment variables optimized for Jordan 7B
    os.environ.update({
        "EMBER_HOME": current_dir,
        "EMBER_MODELS_DIR": models_dir,
        "DEBUG": "true",
        "VERBOSE_LOGGING": "true",
        "USE_LOCAL_MODEL": "true",
        "MODEL_NAME": "jordan-7b",
        "TEMPERATURE": "0.7",
        "MAX_TOKENS": "4096",
        "CONTEXT_LENGTH": "8192"
    })
    
    return current_dir, models_dir

def find_jordan_model(models_dir: str) -> Optional[str]:
    """Find Jordan 7B model with intelligent detection"""
    logger.info("🎯 Searching for Jordan 7B model...")
    
    jordan_patterns = [
        "*jordan*7b*.gguf", "*jordan-7b*.gguf", "*jordan_7b*.gguf",
        "*jordan*7*.gguf", "*jordan*.gguf", "*7b*.gguf", "*.gguf"
    ]
    
    models_path = Path(models_dir)
    for pattern in jordan_patterns:
        for model_file in models_path.glob(pattern):
            if model_file.is_file() and model_file.stat().st_size > 1000000:  # > 1MB
                logger.info(f"🎯 Jordan 7B model found: {model_file.name}")
                return str(model_file)
    
    logger.warning("⚠️  Jordan 7B model not found! Add to models/ directory")
    return None

def run_8_point_comprehensive_tests():
    """Run the enhanced 8-point test suite"""
    logger.info("🧪 Running 8-point comprehensive test suite...")
    
    try:
        result = subprocess.run([sys.executable, 'quick_test.py'], 
            capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and "8/8 tests passed" in result.stdout:
            logger.info("✅ All 8 comprehensive tests passed!")
            return True
        else:
            logger.error("❌ Some tests failed!")
            logger.error(result.stdout[-500:])  # Last 500 chars
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Tests timed out!")
        return False
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return False

def auto_push_harmonization():
    """Auto-push with agent harmonization"""
    logger.info("🔄 Auto-push with harmonization...")
    
    try:
        # Check for changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
            capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            # Add and commit
            subprocess.run(['git', 'add', '.'], check=True)
            
            commit_msg = f"Jordan 7B auto-push: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # Push to main
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            logger.info("✅ Successfully harmonized and pushed to main")
        else:
            logger.info("✅ No changes to harmonize")
            
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️  Auto-push failed: {e}")
    except Exception as e:
        logger.error(f"❌ Harmonization error: {e}")

def main():
    """Main entry point for Jordan 7B Autonomous Agent Swarm System"""
    logger.info("🔥 EMBER JORDAN 7B - AUTONOMOUS AGENT SWARM SYSTEM")
    logger.info("=" * 70)
    
    # Initialize orchestrator
    orchestrator = AgentSwarmOrchestrator()
    
    # Setup Jordan 7B environment
    current_dir, models_dir = setup_jordan_environment()
    
    # Find Jordan 7B model
    jordan_model = find_jordan_model(models_dir)
    if jordan_model:
        os.environ["LOCAL_MODEL_PATH"] = jordan_model
        logger.info(f"🎯 Jordan 7B model: {os.path.basename(jordan_model)}")
    
    # Register main agent
    orchestrator.register_agent("jordan_main", {
        "type": "primary",
        "working_files": ["ember_main.py", "start_system.py"],
        "task": "system_orchestration",
        "model_focus": "jordan-7b"
    })
    
    # Start real-time monitoring
    orchestrator.start_real_time_monitoring()
    
    # Start autonomous agent management
    orchestrator.autonomous_agent_management()
    
    # Run comprehensive tests
    if not run_8_point_comprehensive_tests():
        logger.error("❌ Tests failed! System not safe to start.")
        return
    
    # Auto-push harmonization
    auto_push_harmonization()
    
    # Start Jordan 7B system
    logger.info("🚀 Starting Jordan 7B system...")
    
    try:
        from start_system import main as start_main
        system_process = multiprocessing.Process(target=start_main)
        system_process.start()
        
        time.sleep(5)
        
        if system_process.is_alive():
            logger.info("✅ Jordan 7B system operational!")
            
            # Open interface
            time.sleep(3)
            webbrowser.open("http://localhost:8000/docs")
            
            logger.info("🎉 JORDAN 7B EMBER AI ASSISTANT RUNNING!")
            logger.info("🤖 Autonomous agent swarm: ACTIVE")
            logger.info("📝 Real-time monitoring: ACTIVE")
            logger.info("🔄 Auto-harmonization: ACTIVE")
            logger.info("🎯 Model: Jordan 7B Local Generation")
            logger.info("⏹️  Press Ctrl+C to stop")
            
            # Main loop with frequent harmonization
            try:
                while system_process.is_alive():
                    time.sleep(30)  # Every 30 seconds
                    auto_push_harmonization()
                    
            except KeyboardInterrupt:
                logger.info("⏹️  Stopping Jordan 7B system...")
                system_process.terminate()
                system_process.join()
                auto_push_harmonization()  # Final push
                logger.info("✅ Jordan 7B system stopped")
                
        else:
            logger.error("❌ Jordan 7B system failed to start!")
            
    except Exception as e:
        logger.error(f"❌ System error: {e}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()