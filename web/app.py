# web/app.py

"""
Main Flask Application with Modular Plugin Architecture
"""

import os
import sys
from datetime import datetime
import secrets

from flask import Flask, render_template, request, jsonify
from loguru import logger

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.settings import Config
from database.connection import DatabaseManager
from processing.document_processor import DocumentProcessor
from core.plugin_manager import PluginManager
from core.exceptions import MiddlewareError

# Configuration flag to choose routing approach
USE_MODULAR_ROUTES = True  # Set to True to use new modular structure
USE_PLUGIN_SYSTEM = True   # Set to True to enable plugin system

if USE_MODULAR_ROUTES:
    # New modular structure imports with plugin support
    from web.routes import create_api_blueprint, create_web_blueprint
else:
    # Legacy monolithic structure imports
    from web.legacy_routes import api, web, init_routes

def create_app(config_path: str = None) -> Flask:
    """Create and configure Flask application with plugin support"""
    app = Flask(__name__)
    
    # Load configuration
    config = Config(config_path)
    
    # Configure Flask app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', config.get('web_interface', 'secret_key', fallback=secrets.token_hex(32)))
    app.config['MAX_CONTENT_LENGTH'] = int(config.get('processing', 'max_file_size', '10485760'))
    app.config['UPLOAD_FOLDER'] = config.get('processing', 'upload_folder', 'uploads')
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    db_manager = DatabaseManager(config)
    
    # Initialize plugin manager if enabled
    plugin_manager = None
    if USE_PLUGIN_SYSTEM:
        try:
            plugins_directory = os.path.join(project_root, 'plugins')
            plugin_manager = PluginManager(plugins_directory, config)
            
            # Discover and load plugins
            logger.info("Discovering plugins...")
            load_results = plugin_manager.load_all_plugins()
            logger.info(f"Plugin load results: {load_results}")
            
            # Initialize plugins with application context
            app_context = {
                'config': config,
                'db_manager': db_manager,
                'flask_app': app
            }
            
            init_results = plugin_manager.initialize_all_plugins(app_context)
            logger.info(f"Plugin initialization results: {init_results}")
            
        except Exception as e:
            logger.error(f"Plugin system initialization failed: {e}")
            plugin_manager = None
    
    # Initialize document processor with plugin support
    doc_processor = DocumentProcessor(config, db_manager, plugin_manager)
    
    # Initialize and register routes based on configuration
    if USE_MODULAR_ROUTES:
        # New modular approach - create blueprints with factory functions
        api_blueprint = create_api_blueprint(config, db_manager, doc_processor, plugin_manager)
        web_blueprint = create_web_blueprint(config, db_manager, doc_processor, plugin_manager)
        
        # Register the created blueprints
        app.register_blueprint(api_blueprint, url_prefix='/api')
        app.register_blueprint(web_blueprint)
        
        # Register plugin blueprints if plugin manager is available
        if plugin_manager and hasattr(plugin_manager, 'register_blueprints'):
            try:
                plugin_manager.register_blueprints(app)
                logger.info("Plugin blueprints registered successfully")
            except Exception as e:
                logger.error(f"Failed to register plugin blueprints: {e}")
        else:
            logger.warning("Plugin manager not available or missing register_blueprints method")
        
        logger.info("Using modular route structure with plugin support")
    else:
        # Legacy approach - global variable injection
        init_routes(config, db_manager, doc_processor)
        
        # Register the pre-created blueprints
        app.register_blueprint(api, url_prefix='/api')
        app.register_blueprint(web)
        
        logger.info("Using legacy monolithic route structure")
    
    # Configure logging
    setup_logging(app, config)
    
    # Store references for cleanup
    app.plugin_manager = plugin_manager
    app.doc_processor = doc_processor
    app.db_manager = db_manager

    # Add template filters
    # ... (rest of your template filters and error handlers) ...

    # Add template filters
    @app.template_filter('datetime')
    def datetime_filter(value, format='%Y-%m-%d %H:%M:%S'):
        """Format datetime for templates"""
        if value is None:
            return 'N/A'
        if isinstance(value, str):
            try:
                # Handle ISO format strings from APIs
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try parsing other common formats
                    value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    try:
                        value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        # If all parsing fails, return the original string
                        return value
        
        # If it's a datetime object, format it
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        
        return str(value)
    
    # ... (rest of the create_app function, including the template filters, context processor, and error handlers) ...

    @app.template_filter('currency')
    def currency_filter(value):
        """Format currency for templates"""
        if value is None:
            return 'N/A'
        try:
            return f"${float(value):,.2f}"
        except:
            return str(value)
    
    @app.template_filter('filesize')
    def filesize_filter(value):
        """Format file size for templates"""
        if value is None:
            return 'N/A'
        try:
            size = int(value)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return str(value)
    
    # Add template globals
    @app.context_processor
    def inject_globals():
        """Inject global variables into templates"""
        return {
            'app_name': 'Business Plugin Middleware',
            'current_year': datetime.now().year
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'File too large'}), 413
        return render_template('errors/413.html'), 413
    
    # Plugin-specific error handler
    @app.errorhandler(MiddlewareError)
    def handle_middleware_error(error):
        logger.error(f"Middleware error: {error}")
        if request.path.startswith('/api/'):
            return jsonify({'error': str(error)}), 500
        return render_template('errors/500.html', error=str(error)), 500
    
    # Cleanup handler
    @app.teardown_appcontext
    def cleanup_plugins(error):
        """Cleanup plugins on app context teardown"""
        if error:
            logger.error(f"Application context error: {error}")
    
    # Shutdown handler
    def shutdown_handler():
        """Cleanup resources on shutdown"""
        if plugin_manager:
            try:
                plugin_manager.shutdown_all_plugins()
                logger.info("Plugins shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down plugins: {e}")
    
    # Register shutdown handler
    import atexit
    atexit.register(shutdown_handler)
    
    return app

def setup_logging(app: Flask, config: Config):
    """Setup application logging with Loguru"""
    log_level = config.get('logging', 'level', 'INFO')
    log_file = config.get('logging', 'file', 'logs/middleware.log')
    
    # Create logs directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure Loguru
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        level=log_level.upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler with rotation
    logger.add(
        log_file,
        level=log_level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="1 week",
        compression="zip"
    )
    
    logger.info(f"Logging configured with level: {log_level}, file: {log_file}")

def main():
    """Main entry point"""
    # Determine the path to the config.json file
    # Even though it should be config.ini!
    # Get the directory of the current file (app.py)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to the project root directory (from web/ to project_root/)
    project_root = os.path.dirname(current_file_dir)
    
    # Construct the path to config/config.json
    #config_file_path = os.path.join(project_root, 'config', 'config.json')

    # Construct the path to config/config.ini
    config_file_path = os.path.join(project_root, 'config', 'config.ini')
    
    print(f"Attempting to load configuration from: {config_file_path}") # Debugging line

    # Load configuration by passing the determined path
    config = Config(config_file_path)
    
    # Create Flask app, passing the config object or the path again
    # It's generally better to pass the config object if it's already loaded,
    # or ensure create_app also gets the correct path.
    # Given create_app expects config_path, let's pass the path.
    app = create_app(config_file_path) # Pass the config_file_path to create_app

    # Get web interface configuration (you can now use the 'config' object created above)
    host = config.get('web_interface', 'host', '0.0.0.0')
    port = int(config.get('web_interface', 'port', '5000'))
    debug = config.getboolean('web_interface', 'debug', False)
    
    # Log startup information
    logger.info(f"Starting Business Plugin Middleware on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Max file size: {app.config['MAX_CONTENT_LENGTH']} bytes")
    
    # Run the application
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == '__main__':
    main()
