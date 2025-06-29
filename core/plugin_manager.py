"""
Plugin Manager for Business Plugin Middleware
"""
import os
import sys
import importlib
import importlib.util
from typing import Dict, List,                # Categorize the plugin
                self._categorize_plugin(plugin_instance)
                
                logger.info(f"Initialized plugin: {plugin_name}")
                return True
            else:
                raise PluginError(f"Plugin {plugin_name} initialization failed")
                
        except Exception as e:
            logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
            self._failed_plugins.append(plugin_name)
            return Falseype, Any
from pathlib import Path
from loguru import logger
from flask import Flask, Blueprint

from .base_plugin import BasePlugin, WebPlugin, APIPlugin, ProcessingPlugin, IntegrationPlugin
from .exceptions import PluginError, PluginNotFoundError, PluginDependencyError


class PluginManager:
    """Manages plugin loading, initialization, and lifecycle"""
    
    def __init__(self, plugins_directory: str, config: Any = None):
        self.plugins_directory = Path(plugins_directory)
        self.config = config
        
        # Plugin storage
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self._initialized_plugins: List[str] = []
        self._failed_plugins: List[str] = []
        
        # Plugin categories
        self._web_plugins: List[WebPlugin] = []
        self._api_plugins: List[APIPlugin] = []
        self._processing_plugins: List[ProcessingPlugin] = []
        self._integration_plugins: List[IntegrationPlugin] = []
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugins directory
        
        Returns:
            List of plugin names found
        """
        discovered = []
        
        if not self.plugins_directory.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_directory}")
            return discovered
        
        for plugin_dir in self.plugins_directory.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('_'):
                plugin_file = plugin_dir / 'plugin.py'
                if plugin_file.exists():
                    discovered.append(plugin_dir.name)
                    logger.debug(f"Discovered plugin: {plugin_dir.name}")
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a plugin by name
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            plugin_path = self.plugins_directory / plugin_name / 'plugin.py'
            
            if not plugin_path.exists():
                raise PluginNotFoundError(f"Plugin file not found: {plugin_path}")
            
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}.plugin", 
                plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugins.{plugin_name}.plugin"] = module
            spec.loader.exec_module(module)
            
            # Find the plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr != BasePlugin and
                    not attr.__name__.startswith('Base')):
                    plugin_class = attr
                    break
            
            if not plugin_class:
                raise PluginError(f"No valid plugin class found in {plugin_name}")
            
            # Store the plugin class
            self._plugin_classes[plugin_name] = plugin_class
            logger.info(f"Loaded plugin class: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            self._failed_plugins.append(plugin_name)
            return False
    
    def initialize_plugin(self, plugin_name: str, app_context: Dict[str, Any]) -> bool:
        """
        Initialize a loaded plugin
        
        Args:
            plugin_name: Name of the plugin to initialize
            app_context: Application context (config, database, etc.)
            
        Returns:
            bool: True if initialized successfully
        """
        try:
            if plugin_name not in self._plugin_classes:
                if not self.load_plugin(plugin_name):
                    return False
            
            plugin_class = self._plugin_classes[plugin_name]
            plugin_instance = plugin_class(plugin_name)
            
            # Set plugin configuration if available
            if self.config and hasattr(self.config, 'get_plugin_config'):
                plugin_config = self.config.get_plugin_config(plugin_name)
                if plugin_config:
                    plugin_instance.config = plugin_config
            
            # Validate configuration
            if not plugin_instance.validate_config(plugin_instance.config):
                raise PluginError(f"Invalid configuration for plugin {plugin_name}")
            
            # Check dependencies
            if not self._check_dependencies(plugin_instance):
                raise PluginDependencyError(f"Unmet dependencies for plugin {plugin_name}")
            
            # Initialize the plugin
            if plugin_instance.initialize(app_context):
                self._plugins[plugin_name] = plugin_instance
                self._initialized_plugins.append(plugin_name)
                
                # Categorize the plugin
                self._categorize_plugin(plugin_instance)
                
                logger.info(f"Initialized plugin: {plugin_name}")
                return True
            else:
                raise PluginError(f"Plugin initialization failed: {plugin_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
            self._failed_plugins.append(plugin_name)
            return False
    
    def _check_dependencies(self, plugin: BasePlugin) -> bool:
        """Check if plugin dependencies are met"""
        for dep in plugin.dependencies:
            if dep not in self._initialized_plugins:
                logger.error(f"Dependency not met: {dep} for plugin {plugin.name}")
                return False
        return True
    
    def _categorize_plugin(self, plugin: BasePlugin):
        """Categorize plugin by type"""
        if isinstance(plugin, WebPlugin):
            self._web_plugins.append(plugin)
        if isinstance(plugin, APIPlugin):
            self._api_plugins.append(plugin)
        if isinstance(plugin, ProcessingPlugin):
            self._processing_plugins.append(plugin)
        if isinstance(plugin, IntegrationPlugin):
            self._integration_plugins.append(plugin)
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """
        Discover and load all available plugins
        
        Returns:
            Dictionary mapping plugin names to load success status
        """
        discovered = self.discover_plugins()
        results = {}
        
        for plugin_name in discovered:
            results[plugin_name] = self.load_plugin(plugin_name)
        
        return results
    
    def initialize_all_plugins(self, app_context: Dict[str, Any]) -> Dict[str, bool]:
        """
        Initialize all loaded plugins
        
        Args:
            app_context: Application context
            
        Returns:
            Dictionary mapping plugin names to initialization success status
        """
        results = {}
        
        # Sort plugins by dependencies (basic dependency resolution)
        sorted_plugins = self._sort_plugins_by_dependencies()
        
        for plugin_name in sorted_plugins:
            results[plugin_name] = self.initialize_plugin(plugin_name, app_context)
        
        return results
    
    def _sort_plugins_by_dependencies(self) -> List[str]:
        """Sort plugins by their dependencies"""
        # Simple topological sort for now
        # In a more complex system, you'd implement proper dependency resolution
        return list(self._plugin_classes.keys())
    
    def register_blueprints(self, app: Flask):
        """Register all plugin blueprints with the Flask app"""
        # Register web plugin blueprints
        for plugin in self._web_plugins:
            blueprint = plugin.get_blueprint()
            if blueprint:
                app.register_blueprint(blueprint, url_prefix=f'/plugins/{plugin.name}')
                logger.info(f"Registered web blueprint for plugin: {plugin.name}")
        
        # Register API plugin blueprints
        for plugin in self._api_plugins:
            api_blueprint = plugin.get_api_blueprint()
            if api_blueprint:
                app.register_blueprint(api_blueprint, url_prefix=f'/api/plugins/{plugin.name}')
                logger.info(f"Registered API blueprint for plugin: {plugin.name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a plugin instance by name"""
        return self._plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: Type[BasePlugin]) -> List[BasePlugin]:
        """Get all plugins of a specific type"""
        return [plugin for plugin in self._plugins.values() 
                if isinstance(plugin, plugin_type)]
    
    def get_web_plugins(self) -> List[WebPlugin]:
        """Get all web plugins"""
        return self._web_plugins
    
    def get_api_plugins(self) -> List[APIPlugin]:
        """Get all API plugins"""
        return self._api_plugins
    
    def get_processing_plugins(self) -> List[ProcessingPlugin]:
        """Get all processing plugins"""
        return self._processing_plugins
    
    def get_integration_plugins(self) -> List[IntegrationPlugin]:
        """Get all integration plugins"""
        return self._integration_plugins
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all plugins"""
        return {
            'total_discovered': len(self._plugin_classes),
            'initialized': len(self._initialized_plugins),
            'failed': len(self._failed_plugins),
            'plugins': {
                name: plugin.get_health_status() 
                for name, plugin in self._plugins.items()
            },
            'failed_plugins': self._failed_plugins
        }
    
    def shutdown_all_plugins(self):
        """Shutdown and cleanup all plugins"""
        for plugin_name, plugin in self._plugins.items():
            try:
                plugin.cleanup()
                logger.info(f"Cleaned up plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin_name}: {e}")
        
        self._plugins.clear()
        self._initialized_plugins.clear()
        self._web_plugins.clear()
        self._api_plugins.clear()
        self._processing_plugins.clear()
        self._integration_plugins.clear()
    
    def reload_plugin(self, plugin_name: str, app_context: Dict[str, Any]) -> bool:
        """Reload a specific plugin"""
        if plugin_name in self._plugins:
            # Cleanup existing plugin
            try:
                self._plugins[plugin_name].cleanup()
            except Exception as e:
                logger.warning(f"Error cleaning up plugin {plugin_name}: {e}")
            
            # Remove from tracking
            del self._plugins[plugin_name]
            if plugin_name in self._initialized_plugins:
                self._initialized_plugins.remove(plugin_name)
            
            # Remove from categories
            self._web_plugins = [p for p in self._web_plugins if p.name != plugin_name]
            self._api_plugins = [p for p in self._api_plugins if p.name != plugin_name]
            self._processing_plugins = [p for p in self._processing_plugins if p.name != plugin_name]
            self._integration_plugins = [p for p in self._integration_plugins if p.name != plugin_name]
        
        # Remove from class cache to force reload
        if plugin_name in self._plugin_classes:
            del self._plugin_classes[plugin_name]
        
        # Reload and initialize
        return self.initialize_plugin(plugin_name, app_context)
    
    def reload_plugins(self, app_context: Dict[str, Any] = None) -> Dict[str, bool]:
        """Reload all plugins with updated configuration"""
        if app_context is None:
            app_context = {}
        
        results = {}
        plugins_to_reload = list(self._plugins.keys())
        
        for plugin_name in plugins_to_reload:
            try:
                logger.info(f"Reloading plugin: {plugin_name}")
                success = self.reload_plugin(plugin_name, app_context)
                results[plugin_name] = success
            except Exception as e:
                logger.error(f"Failed to reload plugin {plugin_name}: {e}")
                results[plugin_name] = False
        
        return results
