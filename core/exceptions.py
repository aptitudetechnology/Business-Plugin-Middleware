"""
Custom exceptions for the Business Plugin Middleware
"""


class MiddlewareError(Exception):
    """Base exception for middleware errors"""
    pass


class PluginError(MiddlewareError):
    """Base exception for plugin-related errors"""
    pass


class PluginNotFoundError(PluginError):
    """Raised when a plugin cannot be found"""
    pass


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load"""
    pass


class PluginInitializationError(PluginError):
    """Raised when a plugin fails to initialize"""
    pass


class PluginDependencyError(PluginError):
    """Raised when plugin dependencies are not met"""
    pass


class PluginConfigurationError(PluginError):
    """Raised when plugin configuration is invalid"""
    pass


class ProcessingError(MiddlewareError):
    """Base exception for document processing errors"""
    pass


class DocumentProcessingError(ProcessingError):
    """Raised when document processing fails"""
    pass


class OCRError(ProcessingError):
    """Raised when OCR processing fails"""
    pass


class DatabaseError(MiddlewareError):
    """Base exception for database-related errors"""
    pass


class ConnectionError(MiddlewareError):
    """Base exception for connection-related errors"""
    pass


class APIError(MiddlewareError):
    """Base exception for API-related errors"""
    pass


class ValidationError(MiddlewareError):
    """Raised when data validation fails"""
    pass


class ConfigurationError(MiddlewareError):
    """Raised when configuration is invalid or missing"""
    pass


class AuthenticationError(MiddlewareError):
    """Raised when authentication fails"""
    pass


class AuthorizationError(MiddlewareError):
    """Raised when authorization fails"""
    pass


class IntegrationError(MiddlewareError):
    """Base exception for third-party integration errors"""
    pass


class SyncError(IntegrationError):
    """Raised when data synchronization fails"""
    pass


class ExternalServiceError(IntegrationError):
    """Raised when external service communication fails"""
    pass
