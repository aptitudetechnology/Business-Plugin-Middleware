# Business Plugin Middleware

**A modular document processing middleware with plugin architecture for business document management systems.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

Based on the original [Simplified Paperless BigCapital Middleware](https://github.com/aptitudetechnology/simplified-paperless-bigcapital-middleware), this version provides a comprehensive plugin-based architecture for integrating various document management and accounting systems.

## 🌟 Key Features

- **🔌 Plugin-Based Architecture** - Easily extensible with new integrations
- **🌐 Modern Web Interface** - Intuitive dashboard for managing documents and plugins
- **📊 System Diagnostics** - Built-in connectivity tests and container monitoring
- **🐳 Docker Ready** - Complete containerized deployment with Docker Compose
- **📝 Advanced Logging** - Comprehensive logging with Loguru for better debugging
- **🔄 Real-time OCR** - View and download OCR content directly from the web interface
- **⚙️ Dynamic Configuration** - Configure plugins through web UI or configuration files
- **🔒 Network Flexibility** - Supports various deployment scenarios (Docker, VM, host)

## ⚡ Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- At least 4GB RAM (for Paperless-NGX and PostgreSQL)

### 1. Clone and Start Services

```bash
# Clone the repository
git clone <repository-url>
cd Business-Plugin-Middleware

# Build and start all services
make build

# Or manually with docker-compose
docker compose up --build -d

# Check that services are running
docker compose ps
```

### 2. Access Web Interface

```bash
# Access the main web interface
open http://localhost:5000

# Access Paperless-NGX (if included)
open http://localhost:8000
```

### 3. Configure Plugins

1. **Via Web Interface** (Recommended):
   - Navigate to http://localhost:5000/plugins
   - Click "Configure" next to any plugin
   - Enter your API keys and settings
   - Save configuration

2. **Via Configuration Files**:
   ```bash
   # Edit plugin settings
   nano config/plugins.json
   
   # Edit general configuration
   nano config/config.ini
   ```

### 4. System Diagnostics

Visit http://localhost:5000/system to:
- Test plugin connectivity
- View container status
- Check Docker network configuration
- Diagnose network issues

## 🐳 Docker Commands

### Using the Makefile (Recommended)

```bash
# Build and start all services
make build

# Start services without rebuilding
make start

# Stop all services
make stop

# Restart middleware only
make restart

# View logs
make logs

# Fresh rebuild (clears cache)
make fresh

# Clean up everything
make clean

# Show all available commands
make help
```

### Manual Docker Compose Commands

```bash
# Start all services (build if needed)
docker compose up --build -d

# Stop all services
docker compose down

# Restart just the middleware
docker compose restart middleware

# View logs
docker compose logs -f middleware
docker compose logs -f paperless-ngx

# Rebuild after code changes
docker compose build --no-cache middleware
docker compose up -d middleware
```

## 🏗️ Architecture

### Services Overview

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| **Middleware** | 5000 | Main application and web interface | ✅ Ready |
| **Paperless-NGX** | 8000 | Document management system | ✅ Ready |
| **PostgreSQL** | 5432 | Database for Paperless-NGX | ✅ Ready |
| **Redis** | 6379 | Caching and background tasks | ✅ Ready |

### Plugin Status

| Plugin | Status | Description | Configuration Required |
|--------|--------|-------------|----------------------|
| **Paperless-NGX** | ✅ Working | Document management integration | API Token |
| **OCR Processor** | ✅ Working | Document text extraction | None |
| **BigCapital** | ⚠️ Needs Config | Accounting system integration | API Key |
| **InvoicePlane** | ⚠️ Needs Config | Invoice management | API Settings |
| **Invoice Ninja** | ⚠️ Needs Config | Invoice management | API Settings |

## 📱 Web Interface Features

### Dashboard
- **Document Statistics** - View processing stats and recent documents
- **Quick Actions** - Upload documents, refresh data, bulk operations
- **Plugin Status** - Monitor plugin health and connectivity

### Documents Page
- **Document Browser** - View all documents from Paperless-NGX
- **OCR Content Viewer** - View extracted text with copy/download options
- **Document Actions** - Preview, download, and view details
- **Advanced Filtering** - Filter by type, status, and other criteria

### Plugin Management
- **Plugin Configuration** - Configure each plugin through web forms
- **Status Monitoring** - Real-time plugin status and error reporting
- **Batch Operations** - Retry failed plugins, reload configurations

### System Diagnostics
- **Connectivity Tests** - Test connections to external services
- **Container Information** - View Docker container status
- **Network Diagnostics** - Identify networking issues
- **Configuration Validation** - Verify settings are correct

## 🛠️ Configuration

### Network Configuration

#### Docker Environment (Linux)
```ini
[paperless]
# For Linux Docker, use the host LAN IP
api_url = http://192.168.1.115:8000
hostname_url = http://192.168.1.115:8000
api_token = YOUR_REAL_API_TOKEN_HERE
```

#### Docker Environment (Windows/Mac)
```ini
[paperless]
# For Windows/Mac Docker Desktop
api_url = http://host.docker.internal:8000
hostname_url = http://localhost:8000
api_token = YOUR_REAL_API_TOKEN_HERE
```

#### Docker Compose Network
```ini
[paperless]
# When using the included docker-compose.yml
api_url = http://paperless-ngx:8000
hostname_url = http://localhost:8000
api_token = YOUR_REAL_API_TOKEN_HERE
```

### Getting API Tokens

#### Paperless-NGX API Token
1. Access Paperless-NGX at http://localhost:8000
2. Log in with admin credentials
3. Go to Settings → API Tokens
4. Create a new token
5. Copy the token to your configuration

#### BigCapital API Key
1. Log in to your BigCapital account
2. Navigate to Settings → API
3. Create a new API key
4. Copy the key to your plugin configuration

## 🔧 Development

### Project Structure
```
├── api/                 # REST API endpoints
├── config/             # Configuration files
├── core/              # Core plugin system
├── plugins/           # Individual plugin implementations
├── services/          # Business logic services
├── web/              # Web interface (Flask)
├── tests/            # Test suite
├── docker-compose.yml # Service orchestration
├── Dockerfile        # Container definition
└── Makefile          # Build automation
```

### Adding New Plugins

1. Create plugin directory: `plugins/your_plugin/`
2. Implement plugin class extending `BasePlugin`
3. Add configuration to `config/plugins.json`
4. Register plugin in plugin manager

Example plugin structure:
```python
from core.base_plugin import BasePlugin

class YourPlugin(BasePlugin):
    def __init__(self, config: dict):
        super().__init__(config)
        
    def initialize(self, app_context: dict) -> bool:
        # Plugin initialization logic
        return True
        
    def process_document(self, document: dict) -> dict:
        # Document processing logic
        return document
```

### Logging

The project uses Loguru for advanced logging:
- All logs are centralized and structured
- Different log levels for debugging and production
- Automatic log rotation and formatting
- Plugin-specific log contexts

## 🚀 Deployment

### Development Environment
```bash
# Start in development mode
make build
make logs  # Follow logs for debugging
```

### Production Environment
1. Update security settings in `config/config.ini`
2. Use proper SSL certificates
3. Set strong passwords and secret keys
4. Configure backup strategies
5. Use production-grade database settings

### Environment Variables
```bash
# Optional environment overrides
export MIDDLEWARE_HOST=0.0.0.0
export MIDDLEWARE_PORT=5000
export PAPERLESS_URL=http://your-paperless-host:8000
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Plugin Connection Failures
- **Symptom**: Plugins show as "Failed to connect"
- **Solution**: 
  - Check network configuration using System Diagnostics page
  - Verify API tokens are correct and active
  - For Linux Docker: Use host LAN IP instead of `host.docker.internal`

#### 2. Paperless-NGX Not Accessible
- **Symptom**: Documents page shows "No documents found"
- **Solution**:
  ```bash
  # Check if Paperless-NGX is running
  docker compose ps paperless-ngx
  
  # Check connectivity from middleware container
  docker compose exec middleware curl -I http://paperless-ngx:8000
  ```

#### 3. Permission Issues
- **Symptom**: Log files or data directories not writable
- **Solution**:
  ```bash
  # Fix ownership of data directories
  sudo chown -R $USER:$USER ./data ./logs ./uploads
  chmod -R 755 ./data ./logs ./uploads
  ```

#### 4. Container Startup Failures
- **Symptom**: Services fail to start or keep restarting
- **Solution**:
  ```bash
  # Check container logs
  docker compose logs <service-name>
  
  # Check system resources
  docker system df
  docker system prune  # Clean up if needed
  ```

### Debug Mode

Enable debug mode for detailed logging:
```ini
[web_interface]
debug = True

[logging]
level = DEBUG
```

### Network Diagnostics

Use the built-in system diagnostics page at `/system` to:
- Test external service connectivity
- Verify Docker network configuration
- Check container health status
- Validate plugin configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` directory for detailed guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Community**: Join our discussions for help and collaboration

## 🔮 Roadmap

- [ ] Additional accounting system plugins (QuickBooks, Xero)
- [ ] Advanced OCR with AI/ML integration
- [ ] Webhook support for real-time integrations
- [ ] Enhanced security features (OAuth, JWT)
- [ ] Mobile-responsive interface improvements
- [ ] API rate limiting and caching
- [ ] Plugin marketplace and packaging system

---

**⚠️ Development Status**: This software is actively maintained and suitable for production use with proper configuration. Always backup your data before deploying in production environments.
