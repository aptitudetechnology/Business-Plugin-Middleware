#!/usr/bin/env python3

"""
Main entry point for the Business Plugin Middleware application.
This script can be run directly or imported as a module.
"""

import os
import sys
import logging
from pathlib import Path

def setup_environment():
    """Set up the Python environment for the application."""
    # Get the project root directory
    current_file = Path(__file__).resolve()
    project_root = current_file.parent
    
    # Add project root to Python path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return project_root

def main():
    """Main entry point for the application."""
    try:
        # Set up environment
        project_root = setup_environment()
        
        # Import after path setup
        from web.app import create_app
        
        # Create the Flask app
        app = create_app()
        
        # Get configuration
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        print(f"Starting Business Plugin Middleware...")
        print(f"Project root: {project_root}")
        print(f"Server: http://{host}:{port}")
        print(f"Debug mode: {debug}")
        
        # Run the application
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
