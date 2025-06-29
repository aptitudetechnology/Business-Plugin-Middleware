"""
Paperless-NGX Plugin Package
Integration with Paperless-NGX document management system
"""

from .plugin import PaperlessNGXPlugin, PaperlessNGXProcessingPlugin, create_plugin, create_processing_plugin
from .client import PaperlessNGXClient, PaperlessNGXDocument, PaperlessNGXPagination

__version__ = "1.0.0"
__author__ = "Business Plugin Middleware Team"
__description__ = "Paperless-NGX integration plugin for document management"

__all__ = [
    'PaperlessNGXPlugin',
    'PaperlessNGXProcessingPlugin', 
    'PaperlessNGXClient',
    'PaperlessNGXDocument',
    'PaperlessNGXPagination',
    'create_plugin',
    'create_processing_plugin'
]
