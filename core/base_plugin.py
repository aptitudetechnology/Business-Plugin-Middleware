"""
Base Plugin Architecture for Business Plugin Middleware
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from flask import Blueprint
import logging


class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
        self.logger = logging.getLogger(f"plugin.{name}")
        self._config = {}
        self._dependencies = []
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self._config
    
    @config.setter
    def config(self, value: Dict[str, Any]):
        """Set plugin configuration"""
        self._config = value
    
    @property
    def dependencies(self) -> List[str]:
        """Get plugin dependencies"""
        return self._dependencies
    
    @abstractmethod
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with application context
        
        Args:
            app_context: Dictionary containing app configuration, database, etc.
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        Cleanup plugin resources
        
        Returns:
            bool: True if cleanup successful, False otherwise
        """
        pass
    
    def get_blueprint(self) -> Optional[Blueprint]:
        """
        Return Flask blueprint for plugin routes (optional)
        
        Returns:
            Blueprint or None if plugin doesn't provide routes
        """
        return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get plugin health status
        
        Returns:
            Dict with health information
        """
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'status': 'healthy' if self.enabled else 'disabled'
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            bool: True if configuration is valid
        """
        return True
    
    def __str__(self):
        return f"{self.name} v{self.version}"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', version='{self.version}', enabled={self.enabled})>"


class WebPlugin(BasePlugin):
    """Base class for plugins that provide web interfaces"""
    
    @abstractmethod
    def get_blueprint(self) -> Blueprint:
        """Web plugins must provide a blueprint"""
        pass
    
    def get_menu_items(self) -> List[Dict[str, str]]:
        """
        Get menu items for the web interface
        
        Returns:
            List of menu item dictionaries with 'name', 'url', 'icon' keys
        """
        return []


class APIPlugin(BasePlugin):
    """Base class for plugins that provide API endpoints"""
    
    @abstractmethod
    def get_api_blueprint(self) -> Blueprint:
        """API plugins must provide an API blueprint"""
        pass
    
    def get_api_documentation(self) -> Dict[str, Any]:
        """
        Get API documentation for the plugin
        
        Returns:
            Dictionary with API documentation
        """
        return {}


class ProcessingPlugin(BasePlugin):
    """Base class for document processing plugins"""
    
    @abstractmethod
    def process_document(self, document_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document
        
        Args:
            document_path: Path to the document file
            metadata: Document metadata
            
        Returns:
            Dictionary with processing results
        """
        pass
    
    def supported_formats(self) -> List[str]:
        """
        Get supported document formats
        
        Returns:
            List of supported file extensions
        """
        return []


class IntegrationPlugin(BasePlugin):
    """Base class for third-party integration plugins"""
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to the external service
        
        Returns:
            bool: True if connection is successful
        """
        pass
    
    @abstractmethod
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync data with external service
        
        Args:
            data: Data to sync
            
        Returns:
            Dictionary with sync results
        """
        pass
