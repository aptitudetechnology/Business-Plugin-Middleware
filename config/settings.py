"""
Configuration Management with Plugin Support
"""
import os
import configparser
import json
from loguru import logger
from typing import Dict, Any, Optional


class Config:
    """Configuration manager with plugin support"""
    
    def __init__(self, config_path: str = None):
        self.config = configparser.ConfigParser()
        self.config_path = config_path or 'config/config.ini'
        self._plugin_configs = {}
        
        if os.path.exists(self.config_path):
            self.load_config(self.config_path)
        else:
            logger.warning(f"Configuration file not found: {self.config_path}")
            self._create_default_config()
    
    def load_config(self, config_path: str):
        """Load configuration from file"""
        try:
            self.config.read(config_path)
            self.config_path = config_path
            logger.info(f"Configuration loaded from: {config_path}")
            
            # Load plugin configurations
            self._load_plugin_configs()
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """
        Creates a default config.ini file with predefined settings.
        This method is called if config.ini does not exist on startup.
        """
        # Database configuration
        self.config['database'] = {
            'type': 'sqlite',
            'path': 'data/middleware.db'
        }
        
        # Web interface configuration
        self.config['web_interface'] = {
            'host': '0.0.0.0',
            'port': '5000',
            'debug': 'False',
            'secret_key': 'dev-secret-key-change-in-production'
        }
        
        # Extended mode section
        self.config['extended'] = {
            'enabled': 'false'
        }
        
        # OCR configuration
        self.config['ocr'] = {
            'language': 'eng',
            'confidence_threshold': '60',
            'dpi': '300'
        }
        
        # Document processing configuration
        self.config['processing'] = {
            'upload_folder': 'uploads',
            'max_file_size': '10485760',
            'allowed_extensions': 'pdf,png,jpg,jpeg,tiff,txt',
            'check_interval_seconds': '10',
            'log_level': 'INFO',
            'processed_tag': 'ProcessedByMiddleware',
            'error_tag': 'ErrorProcessing'
        }
        
        # Logging configuration
        self.config['logging'] = {
            'level': 'INFO',
            'file': 'logs/middleware.log'
        }
        
        # Currency configuration
        self.config['currency'] = {
            'default': 'USD',
            'supported': 'USD,EUR,GBP,AUD,CAD'
        }
        
        # Plugins configuration
        self.config['plugins'] = {
            'enabled': 'True',
            'auto_discover': 'True',
            'plugin_directory': 'plugins'
        }
        
        # Paperless-NGX configuration
        self.config['paperless'] = {
            'api_url': 'http://paperless-ngx:8000/api/',
            'api_token': 'YOUR_GENERATED_API_TOKEN',
            'invoice_tags': 'Invoice,ProcessedByMiddleware',
            'receipt_tags': 'Receipt,ProcessedByMiddleware'
        }
        
        # BigCapital configuration
        self.config['bigcapital'] = {
            'api_url': 'http://bigcapital:3000/api/',
            'api_token': 'YOUR_BIGCAPITAL_API_TOKEN',
            'default_due_days': '7',
            'auto_create_customers': 'false'
        }
        
        # Ensure the directory for config_file exists before writing
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        # Write the configuration to file
        with open(self.config_path, 'w') as f:
            self.config.write(f)
        
        logger.info(f"Default configuration created at: {self.config_path}")
        
        # Load plugin configurations after creating the file
        self._load_plugin_configs()
    
    def _load_plugin_configs(self):
        """Load plugin-specific configurations"""
        try:
            # Look for plugin configuration files
            config_dir = os.path.dirname(self.config_path) if self.config_path else 'config'
            plugins_config_path = os.path.join(config_dir, 'plugins.json')
            
            if os.path.exists(plugins_config_path):
                with open(plugins_config_path, 'r') as f:
                    self._plugin_configs = json.load(f)
                logger.info(f"Plugin configurations loaded from: {plugins_config_path}")
            
            # Also check for individual plugin config files
            plugins_config_dir = os.path.join(config_dir, 'plugins')
            if os.path.exists(plugins_config_dir):
                for config_file in os.listdir(plugins_config_dir):
                    if config_file.endswith('.json'):
                        plugin_name = config_file[:-5]  # Remove .json extension
                        config_file_path = os.path.join(plugins_config_dir, config_file)
                        
                        try:
                            with open(config_file_path, 'r') as f:
                                self._plugin_configs[plugin_name] = json.load(f)
                            logger.info(f"Plugin config loaded for {plugin_name}")
                        except Exception as e:
                            logger.error(f"Failed to load plugin config for {plugin_name}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to load plugin configurations: {e}")
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """Get configuration value"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value"""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value"""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value"""
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def set(self, section: str, key: str, value: Any):
        """Set a configuration value"""
        # Ensure section exists
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        # Set the value
        self.config.set(section, key, str(value))
    
    def save(self):
        """Save configuration changes to file (alias for save_config)"""
        return self.save_config()
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get configuration for a specific plugin"""
        return self._plugin_configs.get(plugin_name, {})
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """Set configuration for a specific plugin"""
        self._plugin_configs[plugin_name] = config
    
    def save_plugin_configs(self):
        """Save plugin configurations to file"""
        try:
            if not self.config_path:
                logger.error("No config path set, cannot save plugin configurations")
                return False
            
            config_dir = os.path.dirname(self.config_path)
            plugins_config_path = os.path.join(config_dir, 'plugins.json')
            
            # Ensure config directory exists
            os.makedirs(config_dir, exist_ok=True)
            
            with open(plugins_config_path, 'w') as f:
                json.dump(self._plugin_configs, f, indent=2)
            
            logger.info(f"Plugin configurations saved to: {plugins_config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save plugin configurations: {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, str]:
        """Get entire configuration section as dictionary"""
        try:
            return dict(self.config[section])
        except KeyError:
            return {}
    
    def has_section(self, section: str) -> bool:
        """Check if configuration section exists"""
        return self.config.has_section(section)
    
    def has_option(self, section: str, option: str) -> bool:
        """Check if configuration option exists"""
        return self.config.has_option(section, option)
    
    def get_all_plugin_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all plugin configurations"""
        return self._plugin_configs.copy()
    
    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """Check if a plugin is enabled in configuration"""
        plugin_config = self.get_plugin_config(plugin_name)
        return plugin_config.get('enabled', True)  # Default to enabled
    
    def enable_plugin(self, plugin_name: str):
        """Enable a plugin in configuration"""
        if plugin_name not in self._plugin_configs:
            self._plugin_configs[plugin_name] = {}
        self._plugin_configs[plugin_name]['enabled'] = True
    
    def disable_plugin(self, plugin_name: str):
        """Disable a plugin in configuration"""
        if plugin_name not in self._plugin_configs:
            self._plugin_configs[plugin_name] = {}
        self._plugin_configs[plugin_name]['enabled'] = False
    
    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration"""
        return self.get_section('database')
    
    def get_web_config(self) -> Dict[str, str]:
        """Get web interface configuration"""
        return self.get_section('web_interface')
    
    def get_processing_config(self) -> Dict[str, str]:
        """Get document processing configuration"""
        return self.get_section('processing')
    
    def get_logging_config(self) -> Dict[str, str]:
        """Get logging configuration"""
        return self.get_section('logging')
    
    def get_plugins_config(self) -> Dict[str, str]:
        """Get plugins configuration"""
        return self.get_section('plugins')
    
    def get_ocr_config(self) -> Dict[str, str]:
        """Get OCR configuration"""
        return self.get_section('ocr')
    
    def get_currency_config(self) -> Dict[str, str]:
        """Get currency configuration"""
        return self.get_section('currency')
    
    def get_extended_config(self) -> Dict[str, str]:
        """Get extended mode configuration"""
        return self.get_section('extended')
    
    def get_paperless_config(self) -> Dict[str, str]:
        """Get Paperless-NGX configuration"""
        return self.get_section('paperless')
    
    def get_bigcapital_config(self) -> Dict[str, str]:
        """Get BigCapital configuration"""
        return self.get_section('bigcapital')
    
    def is_extended_mode_enabled(self) -> bool:
        """Check if extended mode is enabled"""
        return self.getboolean('extended', 'enabled', fallback=False)
    
    def get_paperless_api_url(self) -> str:
        """Get the Paperless-ngx API URL"""
        return self.get('paperless', 'api_url', fallback='')
    
    def get_paperless_api_token(self) -> str:
        """Get the Paperless-ngx API token"""
        return self.get('paperless', 'api_token', fallback='')
    
    def get_invoice_tags(self) -> str:
        """Get the invoice tags for Paperless-ngx"""
        return self.get('paperless', 'invoice_tags', fallback='Invoice,ProcessedByMiddleware')
    
    def get_receipt_tags(self) -> str:
        """Get the receipt tags for Paperless-ngx"""
        return self.get('paperless', 'receipt_tags', fallback='Receipt,ProcessedByMiddleware')
    
    def get_bigcapital_api_url(self) -> str:
        """Get the BigCapital API URL"""
        return self.get('bigcapital', 'api_url', fallback='')
    
    def get_bigcapital_api_token(self) -> str:
        """Get the BigCapital API token"""
        return self.get('bigcapital', 'api_token', fallback='')
    
    def get_default_due_days(self) -> int:
        """Get the default due days for invoices"""
        return self.getint('bigcapital', 'default_due_days', fallback=7)
    
    def should_auto_create_customers(self) -> bool:
        """Check if customers should be auto-created"""
        return self.getboolean('bigcapital', 'auto_create_customers', fallback=False)
    
    def get_default_currency(self) -> str:
        """Get the default currency"""
        return self.get('currency', 'default', fallback='USD')
    
    def get_supported_currencies(self) -> list:
        """Get list of supported currencies"""
        currencies_str = self.get('currency', 'supported', fallback='USD,EUR,GBP,AUD,CAD')
        return [c.strip() for c in currencies_str.split(',')]
    
    def get_ocr_language(self) -> str:
        """Get OCR language setting"""
        return self.get('ocr', 'language', fallback='eng')
    
    def get_ocr_confidence_threshold(self) -> int:
        """Get OCR confidence threshold"""
        return self.getint('ocr', 'confidence_threshold', fallback=60)
    
    def get_ocr_dpi(self) -> int:
        """Get OCR DPI setting"""
        return self.getint('ocr', 'dpi', fallback=300)
    
    def save_config(self, config_path: str = None):
        """Save configuration to file"""
        try:
            save_path = config_path or self.config_path
            if not save_path:
                logger.error("No config path specified")
                return False
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w') as f:
                self.config.write(f)
            
            logger.info(f"Configuration saved to: {save_path}")
            
            # Also save plugin configurations
            self.save_plugin_configs()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def __repr__(self):
        return f"<Config(path='{self.config_path}', sections={list(self.config.sections())})>"
