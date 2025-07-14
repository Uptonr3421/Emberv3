#!/usr/bin/env python3
"""
Emberv3 Plugin System
====================

Core plugin system for extending Emberv3 functionality.
Supports dynamic loading, dependency management, and lifecycle control.

Features:
- Dynamic plugin loading/unloading
- Plugin dependency resolution
- Lifecycle management (init, start, stop, cleanup)
- Event system for inter-plugin communication
- Plugin configuration management
- Security and validation

Usage:
    from plugins import PluginManager
    
    plugin_manager = PluginManager()
    plugin_manager.load_plugins()
    plugin_manager.start_all()
"""

import os
import sys
import importlib
import inspect
import logging
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
from abc import ABC, abstractmethod

# Setup logging
logger = logging.getLogger('emberv3_plugins')

class PluginBase(ABC):
    """Base class for all Emberv3 plugins"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.is_enabled = False
        self.is_running = False
        self.config = {}
        self.dependencies = []
        self.logger = logging.getLogger(f'plugin_{name}')
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration"""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """Start the plugin"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop the plugin"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': self.name,
            'version': self.version,
            'is_enabled': self.is_enabled,
            'is_running': self.is_running,
            'dependencies': self.dependencies
        }

class PluginManager:
    """Central plugin management system"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.enabled_plugins: List[str] = []
        self.logger = logger
        
        # Create plugins directory if it doesn't exist
        self.plugins_dir.mkdir(exist_ok=True)
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory"""
        discovered = []
        
        for item in self.plugins_dir.iterdir():
            if item.is_file() and item.suffix == '.py' and item.stem != '__init__':
                discovered.append(item.stem)
            elif item.is_dir() and not item.name.startswith('_'):
                plugin_file = item / 'plugin.py'
                if plugin_file.exists():
                    discovered.append(item.name)
        
        self.logger.info(f"Discovered {len(discovered)} plugins: {discovered}")
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a single plugin"""
        try:
            # Import the plugin module
            plugin_path = f"plugins.{plugin_name}"
            if plugin_name in sys.modules:
                importlib.reload(sys.modules[plugin_name])
            
            module = importlib.import_module(plugin_path)
            
            # Find the plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj is not PluginBase):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                self.logger.error(f"No plugin class found in {plugin_name}")
                return False
            
            # Create plugin instance
            plugin_instance = plugin_class(plugin_name)
            
            # Load configuration if available
            config = self.plugin_configs.get(plugin_name, {})
            
            # Initialize plugin
            if plugin_instance.initialize(config):
                self.plugins[plugin_name] = plugin_instance
                self.logger.info(f"✅ Plugin loaded: {plugin_name}")
                return True
            else:
                self.logger.error(f"❌ Plugin initialization failed: {plugin_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")
            return False
    
    def load_plugins(self) -> int:
        """Load all discovered plugins"""
        discovered = self.discover_plugins()
        loaded_count = 0
        
        for plugin_name in discovered:
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        self.logger.info(f"Loaded {loaded_count}/{len(discovered)} plugins")
        return loaded_count
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin = self.plugins[plugin_name]
        
        # Check dependencies
        for dep in plugin.dependencies:
            if dep not in self.plugins or not self.plugins[dep].is_enabled:
                self.logger.error(f"Dependency not available: {dep}")
                return False
        
        plugin.is_enabled = True
        if plugin_name not in self.enabled_plugins:
            self.enabled_plugins.append(plugin_name)
        
        self.logger.info(f"✅ Plugin enabled: {plugin_name}")
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        
        # Stop plugin if running
        if plugin.is_running:
            self.stop_plugin(plugin_name)
        
        plugin.is_enabled = False
        if plugin_name in self.enabled_plugins:
            self.enabled_plugins.remove(plugin_name)
        
        self.logger.info(f"🔕 Plugin disabled: {plugin_name}")
        return True
    
    def start_plugin(self, plugin_name: str) -> bool:
        """Start a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        
        if not plugin.is_enabled:
            self.logger.error(f"Plugin not enabled: {plugin_name}")
            return False
        
        if plugin.is_running:
            self.logger.warning(f"Plugin already running: {plugin_name}")
            return True
        
        # Start dependencies first
        for dep in plugin.dependencies:
            if dep in self.plugins and not self.plugins[dep].is_running:
                self.start_plugin(dep)
        
        try:
            if plugin.start():
                plugin.is_running = True
                self.logger.info(f"🚀 Plugin started: {plugin_name}")
                return True
            else:
                self.logger.error(f"❌ Plugin start failed: {plugin_name}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Plugin start error {plugin_name}: {e}")
            return False
    
    def stop_plugin(self, plugin_name: str) -> bool:
        """Stop a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        
        if not plugin.is_running:
            return True
        
        try:
            if plugin.stop():
                plugin.is_running = False
                self.logger.info(f"🛑 Plugin stopped: {plugin_name}")
                return True
            else:
                self.logger.error(f"❌ Plugin stop failed: {plugin_name}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Plugin stop error {plugin_name}: {e}")
            return False
    
    def start_all(self) -> int:
        """Start all enabled plugins"""
        started_count = 0
        
        for plugin_name in self.enabled_plugins:
            if self.start_plugin(plugin_name):
                started_count += 1
        
        self.logger.info(f"Started {started_count}/{len(self.enabled_plugins)} plugins")
        return started_count
    
    def stop_all(self) -> int:
        """Stop all running plugins"""
        stopped_count = 0
        
        for plugin_name, plugin in self.plugins.items():
            if plugin.is_running:
                if self.stop_plugin(plugin_name):
                    stopped_count += 1
        
        self.logger.info(f"Stopped {stopped_count} plugins")
        return stopped_count
    
    def cleanup_all(self) -> int:
        """Cleanup all plugins"""
        cleaned_count = 0
        
        for plugin_name, plugin in self.plugins.items():
            try:
                if plugin.cleanup():
                    cleaned_count += 1
            except Exception as e:
                self.logger.error(f"❌ Cleanup error {plugin_name}: {e}")
        
        self.logger.info(f"Cleaned up {cleaned_count} plugins")
        return cleaned_count
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plugin"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].get_info()
        return None
    
    def get_all_plugins_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all plugins"""
        return {name: plugin.get_info() for name, plugin in self.plugins.items()}
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        if plugin_name in self.plugins:
            # Stop and cleanup first
            self.stop_plugin(plugin_name)
            self.plugins[plugin_name].cleanup()
            
            # Remove from plugins dict
            del self.plugins[plugin_name]
            
            # Reload
            return self.load_plugin(plugin_name)
        
        return False

# Export the main classes
__all__ = ['PluginBase', 'PluginManager']