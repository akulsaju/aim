"""
AIM Plugin System
Extensible architecture for adding custom functionality
"""

import json
import importlib
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Type, List
from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """
    Abstract base class for AIM plugins.
    
    All plugins should inherit from this class and implement the required methods.
    """
    
    # Plugin metadata
    name = "BasePlugin"
    version = "1.0.0"
    description = "Base plugin class"
    author = "Unknown"
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize plugin.
        
        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
    
    @abstractmethod
    def execute(self, input_data: Any, **kwargs) -> Any:
        """
        Execute the plugin with given input.
        
        Args:
            input_data: Input data for processing
            **kwargs: Additional arguments
        
        Returns:
            Processing result
        """
        pass
    
    def get_info(self) -> Dict[str, str]:
        """Get plugin information."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author
        }
    
    def validate_config(self) -> bool:
        """Validate plugin configuration. Override to implement validation."""
        return True


class PluginManager:
    """
    Manages plugin loading, registration, and execution.
    
    Handles:
    - Plugin discovery
    - Loading plugins from disk
    - Plugin registration
    - Plugin execution
    """
    
    def __init__(self, plugin_dir: str = None):
        """
        Initialize plugin manager.
        
        Args:
            plugin_dir: Directory containing plugins (default: ./plugins)
        """
        if plugin_dir is None:
            plugin_dir = Path(__file__).parent.parent / 'plugins'
        
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, BasePlugin] = {}
        self.hooks: Dict[str, List[Callable]] = {}
    
    def discover_plugins(self):
        """
        Discover and load all plugins from plugin directory.
        """
        if not self.plugin_dir.exists():
            return
        
        for plugin_path in self.plugin_dir.iterdir():
            if plugin_path.is_dir() and (plugin_path / '__init__.py').exists():
                self._load_plugin_from_dir(plugin_path)
    
    def _load_plugin_from_dir(self, plugin_path: Path):
        """
        Load a plugin from a directory.
        
        Args:
            plugin_path: Path to plugin directory
        """
        try:
            # Check for plugin.json manifest
            manifest_path = plugin_path / 'plugin.json'
            if not manifest_path.exists():
                return
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Load the plugin module
            plugin_name = plugin_path.name
            module_path = str(plugin_path)
            
            # Try to load plugin
            spec = importlib.util.spec_from_file_location(
                plugin_name,
                plugin_path / '__init__.py'
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get plugin class
            if hasattr(module, 'Plugin'):
                plugin_class = module.Plugin
                plugin_instance = plugin_class(manifest.get('config', {}))
                self.register_plugin(plugin_name, plugin_instance)
        
        except Exception as e:
            print(f"Failed to load plugin from {plugin_path}: {e}")
    
    def register_plugin(self, name: str, plugin: BasePlugin):
        """
        Register a plugin.
        
        Args:
            name: Plugin identifier
            plugin: Plugin instance
        """
        if not isinstance(plugin, BasePlugin):
            raise TypeError(f"Plugin must inherit from BasePlugin")
        
        if not plugin.validate_config():
            raise ValueError(f"Invalid plugin configuration for {name}")
        
        self.plugins[name] = plugin
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get a plugin by name.
        
        Args:
            name: Plugin name
        
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(name)
    
    def execute_plugin(self, name: str, input_data: Any, **kwargs) -> Any:
        """
        Execute a plugin.
        
        Args:
            name: Plugin name
            input_data: Input data
            **kwargs: Additional arguments
        
        Returns:
            Plugin output
        """
        plugin = self.get_plugin(name)
        if not plugin:
            raise ValueError(f"Plugin not found: {name}")
        
        return plugin.execute(input_data, **kwargs)
    
    def list_plugins(self) -> List[str]:
        """List all registered plugins."""
        return list(self.plugins.keys())
    
    def get_plugin_info(self, name: str) -> Dict[str, Any]:
        """Get plugin information."""
        plugin = self.get_plugin(name)
        if not plugin:
            raise ValueError(f"Plugin not found: {name}")
        
        return plugin.get_info()
    
    def register_hook(self, hook_name: str, callback: Callable):
        """
        Register a hook callback.
        
        Args:
            hook_name: Name of the hook
            callback: Callback function
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        self.hooks[hook_name].append(callback)
    
    def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Call all callbacks registered for a hook.
        
        Args:
            hook_name: Name of the hook
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            List of callback return values
        """
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                result = callback(*args, **kwargs)
                results.append(result)
        
        return results


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get or create global plugin manager."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        _plugin_manager.discover_plugins()
    return _plugin_manager
