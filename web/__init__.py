"""
Web routes initialization with dependency injection and logging support
"""

import logging
from flask import Blueprint
from config.settings import Config
from database.connection import DatabaseManager
from processing.document_processor import DocumentProcessor
from core.plugin_manager import PluginManager

# Import route modules
from .routes import create_web_blueprint, create_api_blueprint

# Set up logger for this module
logger = logging.getLogger(__name__)

# Global variables (will be injected by app.py)
config: Config = None
db_manager: DatabaseManager = None
doc_processor: DocumentProcessor = None
plugin_manager: PluginManager = None

def init_routes(app_config: Config, app_db_manager: DatabaseManager, 
               app_doc_processor: DocumentProcessor, app_plugin_manager: PluginManager = None):
    """Initialize routes with dependency injection"""
    global config, db_manager, doc_processor, plugin_manager
    
    config = app_config
    db_manager = app_db_manager
    doc_processor = app_doc_processor
    plugin_manager = app_plugin_manager
    
    logger.info("Routes initialized with dependencies")
    if plugin_manager:
        logger.info("Plugin manager available for routes")
    else:
        logger.info("No plugin manager provided to routes")

def get_blueprints():
    """Return all blueprints for registration with Flask app"""
    if not config or not db_manager or not doc_processor:
        raise RuntimeError("Routes must be initialized before getting blueprints")
    
    logger.info("Creating blueprints...")
    
    blueprints = [
        create_web_blueprint(config, db_manager, doc_processor, plugin_manager),
        create_api_blueprint(config, db_manager, doc_processor, plugin_manager)
    ]
    
    logger.info(f"Created {len(blueprints)} blueprints")
    return blueprints
