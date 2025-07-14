#!/usr/bin/env python3
"""
Emberv3 Task Management Agent
============================

A sophisticated task management and coordination agent for the Emberv3 system.
Handles task scheduling, priority management, and inter-agent coordination.

Features:
- Task queue management
- Priority-based task scheduling
- Agent workload balancing
- Task dependency resolution
- Performance monitoring
- Automatic task recovery

Usage:
    from agents.task_manager import TaskManager
    
    task_manager = TaskManager()
    task_manager.start()
"""

import os
import json
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('emberv3_task_manager')

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

@dataclass
class Task:
    """Individual task definition"""
    id: str
    name: str
    priority: TaskPriority
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    max_retries: int = 3
    timeout: int = 300  # 5 minutes
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    agent_id: Optional[str] = None
    
    def __lt__(self, other):
        """For priority queue sorting"""
        return self.priority.value < other.priority.value

class AgentWorker:
    """Individual agent worker thread"""
    def __init__(self, agent_id: str, task_manager: 'TaskManager'):
        self.agent_id = agent_id
        self.task_manager = task_manager
        self.is_running = False
        self.current_task: Optional[Task] = None
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.total_execution_time = 0
        self.thread: Optional[threading.Thread] = None
        
    def start(self):
        """Start the agent worker thread"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info(f"🤖 Agent {self.agent_id} started")
    
    def stop(self):
        """Stop the agent worker thread"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info(f"🛑 Agent {self.agent_id} stopped")
    
    def _run(self):
        """Main agent execution loop"""
        while self.is_running:
            try:
                # Get next task from queue
                task = self.task_manager.get_next_task(self.agent_id)
                if task:
                    self._execute_task(task)
                else:
                    time.sleep(0.1)  # Brief pause if no tasks
            except Exception as e:
                logger.error(f"❌ Agent {self.agent_id} error: {e}")
                time.sleep(1)
    
    def _execute_task(self, task: Task):
        """Execute a single task"""
        self.current_task = task
        task.agent_id = self.agent_id
        task.started_at = datetime.now()
        task.status = TaskStatus.RUNNING
        
        logger.info(f"🔄 Agent {self.agent_id} executing task: {task.name}")
        
        try:
            # Execute the task function
            start_time = time.time()
            result = task.function(*task.args, **task.kwargs)
            execution_time = time.time() - start_time
            
            # Update task status
            task.result = result
            task.completed_at = datetime.now()
            task.status = TaskStatus.COMPLETED
            
            # Update agent statistics
            self.completed_tasks += 1
            self.total_execution_time += execution_time
            
            logger.info(f"✅ Task {task.name} completed in {execution_time:.2f}s")
            
        except Exception as e:
            # Handle task failure
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self.failed_tasks += 1
            
            logger.error(f"❌ Task {task.name} failed: {e}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                logger.info(f"🔄 Retrying task {task.name} (attempt {task.retry_count})")
                self.task_manager.retry_task(task)
        
        finally:
            self.current_task = None
            self.task_manager.update_task_status(task)

class TaskManager:
    """Main task management system"""
    
    def __init__(self, max_agents: int = 4):
        self.max_agents = max_agents
        self.task_queue = PriorityQueue()
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, AgentWorker] = {}
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        self.is_running = False
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'average_execution_time': 0,
            'queue_size': 0
        }
        
        # Create agent workers
        for i in range(max_agents):
            agent_id = f"agent_{i+1}"
            self.agents[agent_id] = AgentWorker(agent_id, self)
    
    def start(self):
        """Start the task management system"""
        if not self.is_running:
            self.is_running = True
            
            # Start all agent workers
            for agent in self.agents.values():
                agent.start()
            
            logger.info(f"🚀 Task Manager started with {len(self.agents)} agents")
    
    def stop(self):
        """Stop the task management system"""
        if self.is_running:
            self.is_running = False
            
            # Stop all agent workers
            for agent in self.agents.values():
                agent.stop()
            
            logger.info("🛑 Task Manager stopped")
    
    def add_task(self, 
                 name: str, 
                 function: Callable, 
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 args: tuple = (),
                 kwargs: Optional[dict] = None,
                 dependencies: Optional[List[str]] = None,
                 max_retries: int = 3,
                 timeout: int = 300,
                 scheduled_at: Optional[datetime] = None) -> str:
        """Add a new task to the queue"""
        
        if kwargs is None:
            kwargs = {}
        if dependencies is None:
            dependencies = []
        
        task_id = f"task_{int(time.time()*1000)}_{len(self.tasks)}"
        
        task = Task(
            id=task_id,
            name=name,
            priority=priority,
            function=function,
            args=args,
            kwargs=kwargs,
            dependencies=dependencies,
            max_retries=max_retries,
            timeout=timeout,
            scheduled_at=scheduled_at
        )
        
        self.tasks[task_id] = task
        self.stats['total_tasks'] += 1
        
        # Check if task can be queued immediately
        if self._can_execute_task(task):
            self.task_queue.put(task)
            self.stats['queue_size'] = self.task_queue.qsize()
            logger.info(f"📝 Task added: {name} (Priority: {priority.name})")
        else:
            logger.info(f"⏳ Task scheduled: {name} (Waiting for dependencies)")
        
        return task_id
    
    def get_next_task(self, agent_id: str) -> Optional[Task]:
        """Get the next task from the queue"""
        if not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                self.stats['queue_size'] = self.task_queue.qsize()
                return task
            except:
                return None
        return None
    
    def retry_task(self, task: Task):
        """Retry a failed task"""
        if task.retry_count < task.max_retries:
            task.status = TaskStatus.PENDING
            self.task_queue.put(task)
            self.stats['queue_size'] = self.task_queue.qsize()
    
    def update_task_status(self, task: Task):
        """Update task status and handle completion"""
        if task.status == TaskStatus.COMPLETED:
            self.completed_tasks.append(task.id)
            self.stats['completed_tasks'] += 1
            self._check_dependent_tasks(task.id)
        elif task.status == TaskStatus.FAILED and task.retry_count >= task.max_retries:
            self.failed_tasks.append(task.id)
            self.stats['failed_tasks'] += 1
    
    def _can_execute_task(self, task: Task) -> bool:
        """Check if task dependencies are satisfied"""
        if not task.dependencies:
            return True
        
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        
        return True
    
    def _check_dependent_tasks(self, completed_task_id: str):
        """Check if any pending tasks can now be executed"""
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and 
                completed_task_id in task.dependencies and
                self._can_execute_task(task)):
                self.task_queue.put(task)
                self.stats['queue_size'] = self.task_queue.qsize()
                logger.info(f"📝 Task unblocked: {task.name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_stats = {}
        for agent_id, agent in self.agents.items():
            agent_stats[agent_id] = {
                'completed_tasks': agent.completed_tasks,
                'failed_tasks': agent.failed_tasks,
                'current_task': agent.current_task.name if agent.current_task else None,
                'average_execution_time': (
                    agent.total_execution_time / agent.completed_tasks 
                    if agent.completed_tasks > 0 else 0
                )
            }
        
        return {
            'system_status': 'running' if self.is_running else 'stopped',
            'total_agents': len(self.agents),
            'task_stats': self.stats,
            'agent_stats': agent_stats,
            'queue_size': self.task_queue.qsize(),
            'pending_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            'running_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks)
        }
    
    def get_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                'id': task.id,
                'name': task.name,
                'priority': task.priority.name,
                'status': task.status.value,
                'created_at': task.created_at.isoformat(),
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'execution_time': (
                    (task.completed_at - task.started_at).total_seconds() 
                    if task.started_at and task.completed_at else None
                ),
                'retry_count': task.retry_count,
                'max_retries': task.max_retries,
                'agent_id': task.agent_id,
                'error': task.error
            }
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                logger.info(f"❌ Task cancelled: {task.name}")
                return True
        return False

# Example usage functions
def example_task_function(name: str, duration: int = 1):
    """Example task function for testing"""
    logger.info(f"🔧 Executing task: {name}")
    time.sleep(duration)
    return f"Task {name} completed successfully"

def example_ai_generation_task(prompt: str, max_tokens: int = 100):
    """Example AI generation task"""
    logger.info(f"🤖 Generating AI response for: {prompt}")
    time.sleep(2)  # Simulate AI generation time
    return f"AI Response to '{prompt}': This is a simulated AI response."

def example_file_processing_task(file_path: str):
    """Example file processing task"""
    logger.info(f"📁 Processing file: {file_path}")
    time.sleep(1)
    return f"File {file_path} processed successfully"

# Demo function
def run_demo():
    """Run a demonstration of the task manager"""
    print("🚀 Starting TaskManager Demo")
    
    # Create and start task manager
    task_manager = TaskManager(max_agents=3)
    task_manager.start()
    
    # Add some example tasks
    task_manager.add_task("High Priority Task", example_task_function, 
                         TaskPriority.HIGH, args=("urgent_task", 2))
    
    task_manager.add_task("AI Generation", example_ai_generation_task,
                         TaskPriority.MEDIUM, args=("What is AI?", 150))
    
    task_manager.add_task("File Processing", example_file_processing_task,
                         TaskPriority.LOW, args=("data.txt",))
    
    # Add dependent tasks
    task1_id = task_manager.add_task("Base Task", example_task_function,
                                   TaskPriority.MEDIUM, args=("base", 1))
    
    task_manager.add_task("Dependent Task", example_task_function,
                         TaskPriority.MEDIUM, args=("dependent", 1),
                         dependencies=[task1_id])
    
    # Monitor for a while
    print("📊 Monitoring task execution...")
    for i in range(10):
        time.sleep(1)
        status = task_manager.get_status()
        print(f"Queue: {status['queue_size']}, "
              f"Completed: {status['completed_tasks']}, "
              f"Failed: {status['failed_tasks']}")
    
    # Stop the system
    task_manager.stop()
    print("✅ Demo completed")

if __name__ == "__main__":
    run_demo()