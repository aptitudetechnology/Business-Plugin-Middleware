#!/usr/bin/env python3
"""
Quick Flask test and startup script for Replit
"""
import os
import sys
import subprocess

def install_flask():
    """Install Flask if not available"""
    print("🔧 Installing Flask...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask==2.3.3"])
        print("✅ Flask installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Flask: {e}")
        return False

def test_imports():
    """Test if required modules can be imported"""
    modules = {
        'flask': 'Flask',
        'sqlite3': 'SQLite3 (built-in)',
        'os': 'OS (built-in)',
        'sys': 'Sys (built-in)',
        'configparser': 'ConfigParser (built-in)'
    }
    
    print("🧪 Testing Python imports...")
    success = True
    
    for module, name in modules.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name}: {e}")
            if module == 'flask':
                success = False
    
    return success

def create_minimal_config():
    """Create minimal configuration"""
    os.makedirs('config', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    config_content = """[web_interface]
host = 0.0.0.0
port = 5000
debug = True
secret_key = dev-secret-key

[database]
type = sqlite
path = data/middleware.db

[processing]
upload_folder = uploads
max_file_size = 10485760
allowed_extensions = pdf,png,jpg,jpeg,tiff,txt

[logging]
level = INFO
file = logs/middleware.log

[plugins]
enabled = True
auto_discover = True
plugin_directory = plugins
"""
    
    if not os.path.exists('config/config.ini'):
        with open('config/config.ini', 'w') as f:
            f.write(config_content)
        print("✅ Configuration created")

def main():
    print("🚀 Business Plugin Middleware - Quick Start for Replit")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Test imports first
    if not test_imports():
        print("🔧 Installing missing dependencies...")
        if not install_flask():
            print("❌ Failed to install Flask. Exiting.")
            sys.exit(1)
        
        # Test again after installation
        if not test_imports():
            print("❌ Still missing dependencies. Exiting.")
            sys.exit(1)
    
    # Create minimal config
    create_minimal_config()
    
    print("\n🎯 Starting Flask application...")
    print("📍 Open in browser: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop\n")
    
    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    try:
        # Import and run the app
        from web.app import main
        main()
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print("🔧 Trying alternative startup...")
        
        # Try to run the file directly
        try:
            subprocess.run([sys.executable, "web/app.py"])
        except Exception as e2:
            print(f"❌ Alternative startup failed: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()
