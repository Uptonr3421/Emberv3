#!/usr/bin/env python3
"""
File Monitor Agent
Monitors file changes and manages project state automatically
"""

import os
import time
import json
import threading
from pathlib import Path
from typing import Dict, Set, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)
load_dotenv()

class EmberFileHandler(FileSystemEventHandler):
    """Custom file system event handler for Ember project"""
    
    def __init__(self, monitor):
        self.monitor = monitor
        self.ignored_patterns = {
            '.git', '__pycache__', '.pytest_cache', 'venv', 'node_modules',
            '.DS_Store', '.vscode', '.idea', '*.pyc', '*.pyo', '*.swp', '*.tmp'
        }
    
    def should_ignore(self, path: str) -> bool:
        """Check if file should be ignored"""
        path_obj = Path(path)
        
        # Check if any part of the path matches ignored patterns
        for part in path_obj.parts:
            if any(pattern in part for pattern in self.ignored_patterns):
                return True
        
        # Check file extensions
        if path_obj.suffix in ['.pyc', '.pyo', '.swp', '.tmp']:
            return True
            
        return False
    
    def on_modified(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.monitor.handle_file_change('modified', event.src_path)
    
    def on_created(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.monitor.handle_file_change('created', event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.monitor.handle_file_change('deleted', event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory:
            if not self.should_ignore(event.src_path):
                self.monitor.handle_file_change('moved_from', event.src_path)
            if not self.should_ignore(event.dest_path):
                self.monitor.handle_file_change('moved_to', event.dest_path)

class FileMonitor:
    """
    Advanced file monitoring system for Ember project
    """
    
    def __init__(self, watch_directory: str = '.'):
        self.watch_directory = Path(watch_directory).resolve()
        self.observer = Observer()
        self.handler = EmberFileHandler(self)
        self.is_running = False
        self.change_queue: Dict[str, Dict] = {}
        self.project_state = self._load_project_state()
        self.last_activity = time.time()
        
        # Statistics
        self.stats = {
            'files_watched': 0,
            'changes_detected': 0,
            'events_processed': 0,
            'start_time': time.time()
        }
    
    def _load_project_state(self) -> Dict:
        """Load existing project state"""
        state_file = self.watch_directory / '.ember_state.json'
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            'files': {},
            'last_scan': None,
            'version': '1.0'
        }
    
    def _save_project_state(self):
        """Save current project state"""
        state_file = self.watch_directory / '.ember_state.json'
        self.project_state['last_scan'] = time.time()
        
        try:
            with open(state_file, 'w') as f:
                json.dump(self.project_state, f, indent=2)
        except Exception as e:
            print(f"{Fore.RED}Error saving project state: {e}{Style.RESET_ALL}")
    
    def handle_file_change(self, event_type: str, file_path: str):
        """Handle file system events"""
        self.last_activity = time.time()
        self.stats['changes_detected'] += 1
        
        file_path = str(Path(file_path).resolve())
        relative_path = str(Path(file_path).relative_to(self.watch_directory))
        
        # Queue the change
        self.change_queue[file_path] = {
            'event_type': event_type,
            'relative_path': relative_path,
            'timestamp': time.time(),
            'processed': False
        }
        
        # Process if debugging is enabled
        if os.getenv('DEBUG', 'false').lower() == 'true':
            print(f"{Fore.CYAN}[FILE MONITOR]{Style.RESET_ALL} {event_type}: {relative_path}")
        
        # Update project state
        self._update_project_state(relative_path, event_type)
    
    def _update_project_state(self, relative_path: str, event_type: str):
        """Update project state with file changes"""
        file_info = {
            'last_modified': time.time(),
            'event_type': event_type,
            'size': 0
        }
        
        # Get file size if it exists
        full_path = self.watch_directory / relative_path
        if full_path.exists() and full_path.is_file():
            try:
                file_info['size'] = full_path.stat().st_size
            except Exception:
                pass
        
        self.project_state['files'][relative_path] = file_info
        
        # Save state periodically
        if len(self.change_queue) % 10 == 0:
            self._save_project_state()
    
    def scan_existing_files(self):
        """Scan existing files in the directory"""
        print(f"{Fore.YELLOW}[FILE MONITOR]{Style.RESET_ALL} Scanning existing files...")
        
        file_count = 0
        for file_path in self.watch_directory.rglob('*'):
            if file_path.is_file() and not self.handler.should_ignore(str(file_path)):
                relative_path = str(file_path.relative_to(self.watch_directory))
                self._update_project_state(relative_path, 'scanned')
                file_count += 1
        
        self.stats['files_watched'] = file_count
        print(f"{Fore.GREEN}[FILE MONITOR]{Style.RESET_ALL} Scanned {file_count} files")
        self._save_project_state()
    
    def start_monitoring(self):
        """Start file monitoring"""
        if self.is_running:
            return
        
        print(f"{Fore.GREEN}[FILE MONITOR]{Style.RESET_ALL} Starting file monitoring...")
        print(f"{Fore.CYAN}[FILE MONITOR]{Style.RESET_ALL} Watching: {self.watch_directory}")
        
        # Scan existing files
        self.scan_existing_files()
        
        # Setup observer
        self.observer.schedule(self.handler, str(self.watch_directory), recursive=True)
        self.observer.start()
        self.is_running = True
        
        # Start background processing thread
        processing_thread = threading.Thread(target=self._process_changes, daemon=True)
        processing_thread.start()
        
        print(f"{Fore.GREEN}[FILE MONITOR]{Style.RESET_ALL} File monitoring active")
    
    def stop_monitoring(self):
        """Stop file monitoring"""
        if not self.is_running:
            return
        
        print(f"{Fore.YELLOW}[FILE MONITOR]{Style.RESET_ALL} Stopping file monitoring...")
        self.observer.stop()
        self.observer.join()
        self.is_running = False
        self._save_project_state()
        print(f"{Fore.RED}[FILE MONITOR]{Style.RESET_ALL} File monitoring stopped")
    
    def _process_changes(self):
        """Background thread to process file changes"""
        while self.is_running:
            try:
                # Process queued changes
                for file_path, change_info in list(self.change_queue.items()):
                    if not change_info['processed']:
                        self._process_single_change(file_path, change_info)
                        change_info['processed'] = True
                        self.stats['events_processed'] += 1
                
                # Clean up old processed changes
                current_time = time.time()
                self.change_queue = {
                    path: info for path, info in self.change_queue.items()
                    if current_time - info['timestamp'] < 300  # Keep for 5 minutes
                }
                
                time.sleep(1)
                
            except Exception as e:
                print(f"{Fore.RED}[FILE MONITOR ERROR]{Style.RESET_ALL} {e}")
                time.sleep(5)
    
    def _process_single_change(self, file_path: str, change_info: Dict):
        """Process a single file change"""
        # Add any specific processing logic here
        if os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true':
            print(f"{Fore.MAGENTA}[PROCESSING]{Style.RESET_ALL} {change_info['event_type']}: {change_info['relative_path']}")
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        uptime = time.time() - self.stats['start_time']
        return {
            **self.stats,
            'uptime_seconds': uptime,
            'uptime_formatted': self._format_duration(uptime),
            'queue_size': len(self.change_queue),
            'last_activity': self._format_duration(time.time() - self.last_activity) + ' ago',
            'is_running': self.is_running
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    
    def print_status(self):
        """Print current monitoring status"""
        stats = self.get_statistics()
        
        print(f"\n{Fore.CYAN}=== FILE MONITOR STATUS ==={Style.RESET_ALL}")
        print(f"Status: {Fore.GREEN}{'Running' if stats['is_running'] else 'Stopped'}{Style.RESET_ALL}")
        print(f"Uptime: {stats['uptime_formatted']}")
        print(f"Files Watched: {stats['files_watched']}")
        print(f"Changes Detected: {stats['changes_detected']}")
        print(f"Events Processed: {stats['events_processed']}")
        print(f"Queue Size: {stats['queue_size']}")
        print(f"Last Activity: {stats['last_activity']}")
        print(f"Watch Directory: {self.watch_directory}")

def main():
    """Main function for running file monitor"""
    monitor = FileMonitor()
    
    try:
        monitor.start_monitoring()
        
        # Keep running and print status periodically
        while True:
            time.sleep(30)
            monitor.print_status()
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Received interrupt signal...{Style.RESET_ALL}")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()