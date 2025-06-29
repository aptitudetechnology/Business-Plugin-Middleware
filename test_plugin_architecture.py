#!/usr/bin/env python3
"""
Test script for the plugin architecture
"""
import os
import sys
import tempfile
import shutil

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from config.settings import Config
from core.plugin_manager import PluginManager
from processing.document_processor import DocumentProcessor
from database.connection import DatabaseManager


def test_plugin_system():
    """Test the plugin system functionality"""
    print("Testing Business Plugin Middleware - Plugin Architecture")
    print("=" * 60)
    
    # Create temporary config
    config_content = """
[web_interface]
host = 127.0.0.1
port = 5000
debug = True

[database]
type = sqlite
path = :memory:

[processing]
upload_folder = /tmp/test_uploads
max_file_size = 10485760
allowed_extensions = pdf,png,jpg,jpeg,tiff,txt

[logging]
level = INFO
file = /tmp/test.log

[plugins]
enabled = True
auto_discover = True
plugin_directory = plugins
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        # Test configuration loading
        print("1. Testing configuration loading...")
        config = Config(config_path)
        print(f"   ✓ Configuration loaded from {config_path}")
        print(f"   ✓ Sections: {list(config.config.sections())}")
        
        # Test database manager
        print("\n2. Testing database manager...")
        db_manager = DatabaseManager(config)
        print("   ✓ Database manager created")
        
        # Test plugin manager
        print("\n3. Testing plugin manager...")
        plugins_dir = os.path.join(project_root, 'plugins')
        plugin_manager = PluginManager(plugins_dir, config)
        print(f"   ✓ Plugin manager created for directory: {plugins_dir}")
        
        # Discover plugins
        discovered = plugin_manager.discover_plugins()
        print(f"   ✓ Discovered plugins: {discovered}")
        
        # Load plugins
        load_results = plugin_manager.load_all_plugins()
        print(f"   ✓ Plugin load results: {load_results}")
        
        # Initialize plugins
        app_context = {
            'config': config,
            'db_manager': db_manager
        }
        init_results = plugin_manager.initialize_all_plugins(app_context)
        print(f"   ✓ Plugin initialization results: {init_results}")
        
        # Test document processor
        print("\n4. Testing document processor...")
        doc_processor = DocumentProcessor(config, db_manager, plugin_manager)
        print("   ✓ Document processor created")
        
        # Get processing stats
        stats = doc_processor.get_processing_stats()
        print(f"   ✓ Processing stats: {stats}")
        
        # Test plugin status
        print("\n5. Testing plugin status...")
        plugin_status = plugin_manager.get_plugin_status()
        print(f"   ✓ Plugin status: {plugin_status}")
        
        # Test plugin categorization
        print("\n6. Testing plugin categorization...")
        web_plugins = plugin_manager.get_web_plugins()
        api_plugins = plugin_manager.get_api_plugins()
        processing_plugins = plugin_manager.get_processing_plugins()
        integration_plugins = plugin_manager.get_integration_plugins()
        
        print(f"   ✓ Web plugins: {[p.name for p in web_plugins]}")
        print(f"   ✓ API plugins: {[p.name for p in api_plugins]}")
        print(f"   ✓ Processing plugins: {[p.name for p in processing_plugins]}")
        print(f"   ✓ Integration plugins: {[p.name for p in integration_plugins]}")
        
        print("\n" + "=" * 60)
        print("✅ Plugin architecture test completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            os.unlink(config_path)
        except:
            pass


if __name__ == '__main__':
    success = test_plugin_system()
    sys.exit(0 if success else 1)
