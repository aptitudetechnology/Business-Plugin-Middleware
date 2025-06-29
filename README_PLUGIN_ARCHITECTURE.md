# Business Plugin Middleware - Modular Architecture

A modular plugin-based middleware system for document processing and business system integration.

## Architecture Overview

The system has been refactored to support a modular plugin architecture with the following key components:

### Core Components

- **Plugin Manager** (`core/plugin_manager.py`): Manages plugin discovery, loading, and lifecycle
- **Base Plugin Classes** (`core/base_plugin.py`): Abstract base classes for different plugin types
- **Document Processor** (`processing/document_processor.py`): Coordinates document processing with plugins
- **Configuration System** (`config/settings.py`): Enhanced configuration with plugin support

### Plugin Types

1. **ProcessingPlugin**: Document processing and OCR
2. **IntegrationPlugin**: Third-party system integration
3. **WebPlugin**: Web interface extensions
4. **APIPlugin**: API endpoint extensions

### Example Plugins

- **OCR Processor** (`plugins/ocr_processor/`): Document text extraction using Tesseract
- **BigCapital Integration** (`plugins/bigcapital/`): Accounting system integration

## Installation & Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt

# For OCR functionality
pip install pytesseract pillow pymupdf

# Install Tesseract OCR engine
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Windows: Download from GitHub releases
```

2. **Configuration**:
```bash
# Copy and modify configuration
cp config/config.ini.example config/config.ini
# Edit config/config.ini with your settings

# Configure plugins
# Edit config/plugins.json with plugin-specific settings
```

3. **Run the Application**:
```bash
python web/app.py
```

## Plugin Development

### Creating a New Plugin

1. **Create Plugin Directory**:
```
plugins/my_plugin/
├── __init__.py
├── plugin.py      # Main plugin class
└── client.py      # Optional: API client
```

2. **Implement Plugin Class**:
```python
from core.base_plugin import ProcessingPlugin

class MyPlugin(ProcessingPlugin):
    def initialize(self, app_context):
        # Initialize plugin
        return True
    
    def cleanup(self):
        # Cleanup resources
        return True
    
    def process_document(self, document_path, metadata):
        # Process document
        return {'success': True, 'result': 'processed'}
    
    def supported_formats(self):
        return ['pdf', 'txt']
```

3. **Configure Plugin**:
```json
{
  "my_plugin": {
    "enabled": true,
    "setting1": "value1",
    "setting2": "value2"
  }
}
```

### Plugin Configuration

Plugins can be configured in two ways:

1. **Main Configuration File** (`config/config.ini`):
```ini
[my_plugin]
enabled = True
api_key = your-api-key
```

2. **Plugin Configuration File** (`config/plugins.json`):
```json
{
  "my_plugin": {
    "enabled": true,
    "api_key": "your-api-key",
    "additional_settings": {}
  }
}
```

## API Endpoints

### Core API

- `GET /api/health` - System health check
- `GET /api/plugins` - List all plugins and their status
- `POST /api/plugins/{name}/reload` - Reload a specific plugin
- `POST /api/documents/upload` - Upload and process documents
- `POST /api/documents/batch` - Batch upload documents

### Plugin API

Plugins can register their own API endpoints by extending `APIPlugin`:

```python
from core.base_plugin import APIPlugin
from flask import Blueprint

class MyAPIPlugin(APIPlugin):
    def get_api_blueprint(self):
        bp = Blueprint('my_api', __name__)
        
        @bp.route('/status')
        def status():
            return {'status': 'ok'}
        
        return bp
```

## Web Interface

### Main Pages

- **Dashboard** (`/`): System overview and plugin status
- **Documents** (`/documents`): Document management
- **Upload** (`/upload`): Document upload interface
- **Plugins** (`/plugins`): Plugin management and configuration

### Plugin Web Interface

Plugins can provide web interfaces by extending `WebPlugin`:

```python
from core.base_plugin import WebPlugin
from flask import Blueprint, render_template_string

class MyWebPlugin(WebPlugin):
    def get_blueprint(self):
        bp = Blueprint('my_web', __name__)
        
        @bp.route('/')
        def dashboard():
            return render_template_string('<h1>My Plugin Dashboard</h1>')
        
        return bp
    
    def get_menu_items(self):
        return [{
            'name': 'My Plugin',
            'url': '/plugins/my_plugin/',
            'icon': 'fa-cog'
        }]
```

## Database Models

The system includes models for:

- **Document**: Document metadata and processing results
- **PluginStatus**: Plugin status tracking
- **ProcessingJob**: Asynchronous processing jobs
- **SyncRecord**: Data synchronization tracking
- **AuditLog**: System activity logging

## Configuration Management

### Environment Variables

- `SECRET_KEY`: Flask secret key
- `CONFIG_PATH`: Path to configuration file
- `DEBUG`: Enable debug mode

### Configuration Sections

- `[web_interface]`: Web server settings
- `[database]`: Database configuration
- `[processing]`: Document processing settings
- `[logging]`: Logging configuration
- `[plugins]`: Plugin system settings

## Logging

The system uses structured logging with plugin-specific loggers:

```python
# In plugin code
self.logger.info("Plugin initialized successfully")
self.logger.error(f"Plugin error: {error}")
```

Log files are stored in `logs/middleware.log` by default.

## Error Handling

Custom exception hierarchy:

- `MiddlewareError`: Base exception
- `PluginError`: Plugin-related errors
- `ProcessingError`: Document processing errors
- `IntegrationError`: Third-party integration errors

## Development

### Running in Development Mode

```bash
# Enable debug mode in config.ini
debug = True

# Or set environment variable
export DEBUG=1
python web/app.py
```

### Testing Plugins

```bash
# Test individual plugin
python -c "from plugins.my_plugin.plugin import MyPlugin; p = MyPlugin('test'); print(p.test_connection())"

# Check plugin status via API
curl http://localhost:5000/api/plugins
```

## Production Deployment

### Using Docker

```bash
# Build image
docker build -t business-middleware .

# Run container
docker run -p 5000:5000 -v ./config:/app/config -v ./uploads:/app/uploads business-middleware
```

### Using Docker Compose

```bash
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Plugin Not Loading**:
   - Check plugin configuration in `config/plugins.json`
   - Verify plugin dependencies are installed
   - Check logs for error messages

2. **OCR Not Working**:
   - Install Tesseract: `sudo apt-get install tesseract-ocr`
   - Install Python packages: `pip install pytesseract pillow`
   - Configure tesseract path in plugin config

3. **Database Errors**:
   - Ensure database directory exists and is writable
   - Check database configuration in `config/config.ini`

### Debug Mode

Enable debug logging to troubleshoot issues:

```ini
[logging]
level = DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your plugin or enhancement
4. Add tests and documentation
5. Submit a pull request

## License

See LICENSE file for details.
