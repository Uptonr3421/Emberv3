#!/usr/bin/env python3
"""
Example Plugin for Emberv3
==========================

Demonstrates the plugin system functionality with a simple example plugin.
Provides text processing capabilities and integrates with the main system.

Features:
- Text processing utilities
- Integration with Emberv3 API
- Configuration management
- Event handling
- Status monitoring

Usage:
    This plugin is automatically loaded by the plugin manager.
"""

import os
import time
import threading
from typing import Dict, Any, Optional
from plugins import PluginBase

class ExamplePlugin(PluginBase):
    """Example plugin demonstrating the plugin system"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.dependencies = []  # No dependencies for this example
        self.worker_thread: Optional[threading.Thread] = None
        self.is_worker_running = False
        self.processed_count = 0
        self.text_cache = {}
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration"""
        try:
            self.config = config
            self.logger.info(f"🔧 Initializing {self.name} plugin")
            
            # Set default configuration
            self.config.setdefault('enabled', True)
            self.config.setdefault('processing_interval', 5)
            self.config.setdefault('cache_size', 100)
            
            # Initialize text processing cache
            self.text_cache = {}
            self.processed_count = 0
            
            self.logger.info(f"✅ {self.name} plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.name}: {e}")
            return False
    
    def start(self) -> bool:
        """Start the plugin"""
        try:
            if not self.config.get('enabled', True):
                self.logger.info(f"⏸️ {self.name} plugin is disabled")
                return False
            
            self.logger.info(f"🚀 Starting {self.name} plugin")
            
            # Start background worker thread
            self.is_worker_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            self.logger.info(f"✅ {self.name} plugin started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start {self.name}: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the plugin"""
        try:
            self.logger.info(f"🛑 Stopping {self.name} plugin")
            
            # Stop background worker
            self.is_worker_running = False
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=5)
            
            self.logger.info(f"✅ {self.name} plugin stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop {self.name}: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        try:
            self.logger.info(f"🧹 Cleaning up {self.name} plugin")
            
            # Clear cache
            self.text_cache.clear()
            
            # Reset counters
            self.processed_count = 0
            
            self.logger.info(f"✅ {self.name} plugin cleaned up successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup {self.name}: {e}")
            return False
    
    def _worker_loop(self):
        """Background worker thread"""
        interval = self.config.get('processing_interval', 5)
        
        while self.is_worker_running:
            try:
                # Simulate some background processing
                self._process_background_tasks()
                
                # Sleep for the specified interval
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"❌ Worker thread error: {e}")
                time.sleep(1)
    
    def _process_background_tasks(self):
        """Process background tasks"""
        # Clean up cache if it's too large
        cache_size = self.config.get('cache_size', 100)
        if len(self.text_cache) > cache_size:
            # Remove oldest entries
            items_to_remove = len(self.text_cache) - cache_size
            for _ in range(items_to_remove):
                oldest_key = next(iter(self.text_cache))
                del self.text_cache[oldest_key]
            
            self.logger.info(f"🧹 Cleaned cache, removed {items_to_remove} entries")
    
    # Plugin-specific functionality
    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text and return analysis"""
        try:
            # Check cache first
            if text in self.text_cache:
                self.logger.info(f"📋 Retrieved from cache: {text[:50]}...")
                return self.text_cache[text]
            
            # Process the text
            result = {
                'original': text,
                'length': len(text),
                'word_count': len(text.split()),
                'uppercase': text.upper(),
                'lowercase': text.lower(),
                'reversed': text[::-1],
                'processed_at': time.time(),
                'processed_by': self.name
            }
            
            # Cache the result
            self.text_cache[text] = result
            self.processed_count += 1
            
            self.logger.info(f"📝 Processed text: {text[:50]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process text: {e}")
            return {'error': str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get plugin statistics"""
        return {
            'processed_count': self.processed_count,
            'cache_size': len(self.text_cache),
            'is_worker_running': self.is_worker_running,
            'config': self.config
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get extended plugin information"""
        base_info = super().get_info()
        base_info.update({
            'statistics': self.get_statistics(),
            'capabilities': [
                'text_processing',
                'caching',
                'background_processing',
                'statistics'
            ]
        })
        return base_info

# Example usage function
def demo_plugin():
    """Demonstrate the plugin functionality"""
    plugin = ExamplePlugin("example_plugin")
    
    # Initialize
    config = {
        'enabled': True,
        'processing_interval': 2,
        'cache_size': 50
    }
    
    if plugin.initialize(config):
        print("✅ Plugin initialized")
        
        # Start plugin
        if plugin.start():
            print("🚀 Plugin started")
            
            # Test text processing
            result = plugin.process_text("Hello, Emberv3 Plugin System!")
            print(f"📝 Processing result: {result}")
            
            # Get statistics
            stats = plugin.get_statistics()
            print(f"📊 Statistics: {stats}")
            
            # Wait a bit
            time.sleep(3)
            
            # Stop plugin
            plugin.stop()
            plugin.cleanup()
            print("✅ Plugin stopped and cleaned up")
        else:
            print("❌ Failed to start plugin")
    else:
        print("❌ Failed to initialize plugin")

if __name__ == "__main__":
    demo_plugin()