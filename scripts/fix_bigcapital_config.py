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
import importlib.util
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
    """Check if the plugin module can be imported"""
    try:
        spec = importlib.util.spec_from_file_location("bigcapital_plugin", plugin_path)
        if spec is None:
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if BigCapitalPlugin class exists
        if hasattr(module, 'BigCapitalPlugin'):
            plugin_class = getattr(module, 'BigCapitalPlugin')
            print_status(f"BigCapitalPlugin class found: {plugin_class}", "SUCCESS")
            return True
        else:
            print_status("BigCapitalPlugin class not found in module", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Failed to import BigCapital plugin: {e}", "ERROR")
        return False

def fix_plugin_routes(routes_path: str):
    """Add fallback configuration route for failed plugins"""
    try:
        with open(routes_path, 'r') as f:
            content = f.read()
        
        # Check if fallback route already exists
        if '@web.route(\'/plugins/<plugin_name>/config\')' in content:
            print_status("Fallback plugin config route already exists", "INFO")
            return
        
        # Add fallback route before the last return statement
        fallback_route = '''
    @web.route('/plugins/<plugin_name>/config')
    def plugin_config_fallback(plugin_name):
        """Fallback configuration page for failed plugins"""
        try:
            if not plugin_manager:
                return render_template('errors/plugin_error.html', 
                                     plugin_name=plugin_name.title(),
                                     error='Plugin manager not available')
            
            # Check if plugin class exists (even if not initialized)
            if plugin_name in plugin_manager._plugin_classes:
                plugin_class = plugin_manager._plugin_classes[plugin_name]
                
                # Generate basic configuration form
                config_data = {}
                if hasattr(plugin_class, '_default_config'):
                    config_data = plugin_class._default_config
                elif plugin_name == 'bigcapital':
                    config_data = {
                        'api_key': '',
                        'base_url': 'https://api.bigcapital.ly',
                        'timeout': 30,
                        'enabled': True
                    }
                
                form_html = f'<form id="pluginConfigForm" method="post" action="/api/plugins/{plugin_name}/config">'
                
                for key, value in config_data.items():
                    if key in ['api_key', 'password', 'secret']:
                        form_html += f'<div class="mb-3">' + \\
                            f'<label for="{key}" class="form-label">{key.replace("_", " ").title()}</label>' + \\
                            f'<input type="password" class="form-control" id="{key}" name="{key}" ' + \\
                            f'placeholder="Enter {key.replace("_", " ")}" required>' + \\
                            '</div>'
                    elif key == 'enabled':
                        checked = 'checked' if value else ''
                        form_html += f'<div class="mb-3 form-check">' + \\
                            f'<input type="checkbox" class="form-check-input" id="{key}" name="{key}" {checked}>' + \\
                            f'<label class="form-check-label" for="{key}">Enable Plugin</label>' + \\
                            '</div>'
                    else:
                        form_html += f'<div class="mb-3">' + \\
                            f'<label for="{key}" class="form-label">{key.replace("_", " ").title()}</label>' + \\
                            f'<input type="text" class="form-control" id="{key}" name="{key}" ' + \\
                            f'value="{value}" placeholder="{key.replace("_", " ").title()}">' + \\
                            '</div>'
                
                form_html += '<button type="submit" class="btn btn-primary">Save Configuration</button></form>'
                
                return f'<div class="container mt-4">' + \\
                    f'<h2>{plugin_name.title()} Plugin Configuration</h2>' + \\
                    '<div class="alert alert-warning">' + \\
                    '<strong>Plugin Status:</strong> Not initialized (likely due to missing configuration)' + \\
                    '</div>' + \\
                    form_html + \\
                    '</div>'
            else:
                return render_template('errors/plugin_error.html', 
                                     plugin_name=plugin_name.title(),
                                     error='Plugin class not found')
                                     
        except Exception as e:
            logger.error(f"Plugin config fallback error for {plugin_name}: {e}")
            return render_template('errors/plugin_error.html', 
                                 plugin_name=plugin_name.title(),
                                 error=f'Configuration error: {str(e)}')

'''
        
        # Insert before the final return web statement
        content = content.replace('    return web', fallback_route + '    return web')
        
        with open(routes_path, 'w') as f:
            f.write(content)
        
        print_status("Added fallback plugin configuration route", "SUCCESS")
        
    except Exception as e:
        print_status(f"Failed to fix plugin routes: {e}", "ERROR")

def create_bigcapital_default_config(config_path: str, plugins_path: str):
    """Create default BigCapital configuration"""
    try:
        # Update config.ini
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if 'bigcapital' not in config:
            config.add_section('bigcapital')
        
        config.set('bigcapital', 'api_key', 'YOUR_BIGCAPITAL_API_KEY_HERE')
        config.set('bigcapital', 'base_url', 'https://api.bigcapital.ly')
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
                'base_url': 'https://api.bigcapital.ly',
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
        print_status("BigCapital plugin module has issues", "ERROR")
        return 1
    
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
    
    # Step 5: Instructions for user
    print_header("Next Steps")
    
    print_status("Configuration fix completed!", "SUCCESS")
    print()
    print("To complete the setup:")
    print("1. Get your BigCapital API key from: https://app.bigcapital.ly/settings/api")
    print("2. Access the web interface: http://simple.local:5000")
    print("3. Go to Plugins page: http://simple.local:5000/plugins")
    print("4. Click 'Configure' next to BigCapital plugin")
    print("5. Enter your API key and save")
    print()
    print("Would you like to restart the middleware container now? (y/n)")
    
    response = input().strip().lower()
    if response in ['y', 'yes']:
        restart_middleware()
        print()
        print_status("Setup complete! Try accessing the BigCapital configuration again.", "SUCCESS")
    else:
        print_status("Remember to restart with: docker compose restart middleware", "INFO")
    
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