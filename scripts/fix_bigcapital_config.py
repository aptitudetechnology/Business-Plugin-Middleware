#!/usr/bin/env python3
"""
BigCapital Plugin Configuration Fix Script

This script diagnoses and fixes issues with BigCapital plugin configuration
on VM deployments.
"""

import os
import sys
import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")

def print_status(message: str, status: str = "INFO"):
    """Print a status message"""
    symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    print(f"{symbols.get(status, 'ℹ️')} {message}")

def load_config_ini(config_path: str) -> Optional[configparser.ConfigParser]:
    """Load configuration from config.ini"""
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        return config
    except Exception as e:
        print_status(f"Failed to load config.ini: {e}", "ERROR")
        return None

def load_plugins_json(plugins_path: str) -> Optional[Dict[str, Any]]:
    """Load configuration from plugins.json"""
    try:
        with open(plugins_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print_status(f"Failed to load plugins.json: {e}", "ERROR")
        return None

def check_plugin_module(plugin_path: str) -> bool:
    """Check if the plugin module exists and has the right structure"""
    try:
        # Just check if the file exists and contains the expected class name
        with open(plugin_path, 'r') as f:
            content = f.read()
        
        # Check if BigCapitalPlugin class exists in the file
        if 'class BigCapitalPlugin' in content:
            print_status("BigCapitalPlugin class found in plugin file", "SUCCESS")
            
            # Check for required imports and methods
            required_elements = [
                'from core.base_plugin import IntegrationPlugin',
                'def initialize(',
                'def cleanup(',
                'def test_connection(',
                'def sync_data('
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                print_status(f"Missing required elements: {', '.join(missing_elements)}", "WARNING")
                return False
            else:
                print_status("Plugin structure looks correct", "SUCCESS")
                return True
        else:
            print_status("BigCapitalPlugin class not found in plugin file", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Failed to read BigCapital plugin file: {e}", "ERROR")
        return False

def fix_plugin_routes(routes_path: str):
    """Check if plugin configuration routes can handle failed plugins"""
    try:
        with open(routes_path, 'r') as f:
            content = f.read()
        
        # Check if the route already handles temporary plugin instances
        if 'Create a temporary instance just for configuration' in content:
            print_status("Plugin configuration routes already handle failed plugins", "SUCCESS")
            return
        
        # Check if the get_plugin_config route exists
        if '/api/plugins/<plugin_name>/config' in content:
            print_status("Plugin configuration API endpoint exists", "SUCCESS")
            return
        
        print_status("Plugin configuration routes may need manual review", "WARNING")
        print_status("The web interface should already handle this via existing routes", "INFO")
        
    except Exception as e:
        print_status(f"Failed to check plugin routes: {e}", "ERROR")

def create_bigcapital_default_config(config_path: str, plugins_path: str):
    """Create default BigCapital configuration"""
    try:
        # Update config.ini
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if 'bigcapital' not in config:
            config.add_section('bigcapital')
        
        config.set('bigcapital', 'api_key', 'YOUR_BIGCAPITAL_API_KEY_HERE')
        config.set('bigcapital', 'base_url', 'http://bigcapital:3000')
        config.set('bigcapital', 'timeout', '30')
        config.set('bigcapital', 'enabled', 'False')
        
        with open(config_path, 'w') as f:
            config.write(f)
        
        print_status("Updated config.ini with BigCapital defaults", "SUCCESS")
        
        # Update plugins.json
        plugins_config = load_plugins_json(plugins_path)
        if plugins_config and 'plugins' in plugins_config:
            if 'bigcapital' not in plugins_config['plugins']:
                plugins_config['plugins']['bigcapital'] = {}
            
            plugins_config['plugins']['bigcapital'].update({
                'api_key': 'YOUR_BIGCAPITAL_API_KEY_HERE',
                'base_url': 'http://bigcapital:3000',
                'timeout': 30,
                'enabled': False
            })
            
            with open(plugins_path, 'w') as f:
                json.dump(plugins_config, f, indent=4)
            
            print_status("Updated plugins.json with BigCapital defaults", "SUCCESS")
        
    except Exception as e:
        print_status(f"Failed to create default config: {e}", "ERROR")

def restart_middleware():
    """Restart the middleware container"""
    try:
        os.system("docker compose restart middleware")
        print_status("Restarted middleware container", "SUCCESS")
    except Exception as e:
        print_status(f"Failed to restart middleware: {e}", "ERROR")

def main():
    """Main function"""
    print_header("BigCapital Plugin Configuration Fix")
    
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # File paths
    config_ini_path = project_root / "config" / "config.ini"
    plugins_json_path = project_root / "config" / "plugins.json"
    plugin_file_path = project_root / "plugins" / "bigcapital" / "plugin.py"
    routes_file_path = project_root / "web" / "routes.py"
    
    print_status(f"Project root: {project_root}")
    
    # Step 1: Check if files exist
    print_header("Checking File Existence")
    
    files_to_check = [
        ("config.ini", config_ini_path),
        ("plugins.json", plugins_json_path),
        ("BigCapital plugin", plugin_file_path),
        ("routes.py", routes_file_path)
    ]
    
    missing_files = []
    for name, path in files_to_check:
        if path.exists():
            print_status(f"{name}: Found", "SUCCESS")
        else:
            print_status(f"{name}: Missing", "ERROR")
            missing_files.append(name)
    
    if missing_files:
        print_status(f"Missing files: {', '.join(missing_files)}", "ERROR")
        return 1
    
    # Step 2: Check plugin module
    print_header("Checking BigCapital Plugin Module")
    plugin_valid = check_plugin_module(str(plugin_file_path))
    
    if not plugin_valid:
        print_status("BigCapital plugin file has structural issues", "WARNING")
        print_status("Continuing with configuration fix...", "INFO")
    else:
        print_status("BigCapital plugin file structure looks good", "SUCCESS")
    
    # Step 3: Check current configuration
    print_header("Checking Current Configuration")
    
    config_ini = load_config_ini(str(config_ini_path))
    plugins_json = load_plugins_json(str(plugins_json_path))
    
    if config_ini:
        if 'bigcapital' in config_ini:
            print_status("BigCapital section found in config.ini", "SUCCESS")
            for key, value in config_ini['bigcapital'].items():
                print_status(f"  {key}: {value}")
        else:
            print_status("BigCapital section missing from config.ini", "WARNING")
    
    if plugins_json:
        if 'plugins' in plugins_json and 'bigcapital' in plugins_json['plugins']:
            print_status("BigCapital config found in plugins.json", "SUCCESS")
            bigcapital_config = plugins_json['plugins']['bigcapital']
            for key, value in bigcapital_config.items():
                if 'key' in key.lower() or 'password' in key.lower():
                    print_status(f"  {key}: {'*' * len(str(value)) if value else 'Not set'}")
                else:
                    print_status(f"  {key}: {value}")
        else:
            print_status("BigCapital config missing from plugins.json", "WARNING")
    
    # Step 4: Fix configuration
    print_header("Fixing Configuration")
    
    create_bigcapital_default_config(str(config_ini_path), str(plugins_json_path))
    fix_plugin_routes(str(routes_file_path))
    
    # Step 5: Check Docker environment
    print_header("Environment Check")
    check_docker_environment()
    
    # Step 6: Provide configuration guidance
    provide_configuration_guidance()
    
    # Step 7: Optional restart
    print_header("Optional Restart")
    print_status("Configuration files have been updated with defaults", "SUCCESS")
    print()
    print("Would you like to restart the middleware container now? (y/n)")
    
    response = input().strip().lower()
    if response in ['y', 'yes']:
        restart_middleware()
        print()
        print_status("Setup complete! Try accessing the BigCapital configuration again.", "SUCCESS")
        print_status("Visit: http://simple.local:5000/plugins", "INFO")
    else:
        print_status("Remember to restart with: docker compose restart middleware", "INFO")
    
def check_docker_environment():
    """Check if we're in a Docker environment and provide guidance"""
    try:
        # Check if Docker is available
        docker_status = os.system("docker --version > /dev/null 2>&1")
        if docker_status == 0:
            print_status("Docker is available", "SUCCESS")
            
            # Check if containers are running
            container_status = os.system("docker compose ps middleware > /dev/null 2>&1")
            if container_status == 0:
                print_status("Middleware container appears to be running", "SUCCESS")
                print_status("Try accessing: http://simple.local:5000/plugins", "INFO")
            else:
                print_status("Middleware container may not be running", "WARNING")
                print_status("Try: docker compose up -d", "INFO")
        else:
            print_status("Docker not available - running in development mode", "INFO")
            
    except Exception as e:
        print_status(f"Failed to check Docker environment: {e}", "WARNING")

def provide_configuration_guidance():
    """Provide specific guidance for BigCapital configuration"""
    print_header("Configuration Guidance")
    
    print_status("Based on the analysis, here's how to configure BigCapital:", "INFO")
    print()
    print("📋 Method 1: Web Interface (Recommended)")
    print("   1. Start the middleware: docker compose up -d")
    print("   2. Visit: http://simple.local:5000/plugins")
    print("   3. Look for BigCapital plugin in the list")
    print("   4. Click 'Configure' or 'Settings' button")
    print("   5. Enter your API key from your self-hosted BigCapital instance")
    print()
    print("📋 Method 2: Direct Configuration File Edit")
    print("   1. Edit config/plugins.json")
    print("   2. Find the 'bigcapital' section")
    print("   3. Update the 'api_key' field with your actual key")
    print("   4. Update 'base_url' to point to your BigCapital instance")
    print("   5. Set 'enabled': true")
    print("   6. Restart: docker compose restart middleware")
    print()
    print("🔑 Get your BigCapital API Key:")
    print("   - Access your BigCapital instance (e.g., http://localhost:3000)")
    print("   - Go to Settings → API or User Settings")
    print("   - Generate or copy your API key")
    print()
    print("🐳 Local BigCapital Setup:")
    print("   - Use docker/bigcapital/ folder for local BigCapital instance")
    print("   - Default URL: http://bigcapital:3000 (container-to-container)")
    print("   - External URL: http://simple.local:3000 (browser access)")
    print()
    print("⚠️  If you see 'Plugin bigcapital not found' errors:")
    print("   - This usually means the plugin failed to load due to missing config")
    print("   - The configuration files have been updated with defaults")
    print("   - Restart the middleware and try again")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nScript cancelled by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)