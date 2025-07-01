# Business Plugin Middleware

**A modular document processing middleware with plugin architecture for business document management systems.**

Based on the original [Simplified Paperless BigCapital Middleware](https://github.com/aptitudetechnology/simplified-paperless-bigcapital-middleware), this version provides a plugin-based architecture for integrating various document management and accounting systems.

## ⚡ Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Clone and Start Services

```bash
# Clone the repository
git clone <repository-url>
cd Business-Plugin-Middleware

# Build and start all services
docker-compose up --build -d

# Check that services are running
docker-compose ps
```

### 2. Initial Setup

```bash
# Follow logs to ensure everything starts properly
docker-compose logs -f

# Access the web interface
open http://localhost:5000

# Access Paperless-NGX (if using)
open http://localhost:8000
```

### 3. Configure Plugins

1. **Via Web Interface** (Recommended):
   - Go to http://localhost:5000/plugins
   - Click "Configure" next to any plugin
   - Enter your API keys and settings
   - Save configuration

2. **Via Configuration Files**:
   - Edit `config/plugins.json` for plugin-specific settings
   - Edit `config/config.ini` for general configuration

### 4. Test Plugin Connections

- Use the web interface to reload/retry failed plugins
- Check plugin status at http://localhost:5000/plugins

## 🐳 Docker Commands

### Essential Commands

```bash
# Start all services (build if needed)
docker-compose up --build -d

# Stop all services
docker-compose down

# Restart just the middleware
docker-compose restart middleware

# View logs
docker-compose logs -f middleware
docker-compose logs -f paperless-ngx

# Rebuild middleware after code changes
docker-compose build --no-cache middleware
docker-compose up -d middleware

# Complete rebuild (use when major changes occur)
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Troubleshooting Commands

```bash
# Check running containers
docker-compose ps

# Check container logs
docker-compose logs <service-name>

# Execute commands inside middleware container
docker-compose exec middleware bash

# Check configuration inside container
docker-compose exec middleware cat /app/config/config.ini

# Network connectivity test
docker-compose exec middleware ping paperless-ngx
```

## 🔧 Services Included

| Service | Port | Description |
|---------|------|-------------|
| **Middleware** | 5000 | Main application and web interface |
| **Paperless-NGX** | 8000 | Document management system |
| **PostgreSQL** | - | Database for Paperless-NGX |
| **Redis** | 6379 | Caching and background tasks |

## 📋 Plugin Status

### ✅ Working Plugins
- **OCR Processor** - Document text extraction using Tesseract

### ⚠️ Plugins Requiring Configuration
- **Paperless-NGX** - Requires API token setup
- **BigCapital** - Requires API key and internet access
- **InvoicePlane** - Requires API configuration
- **Invoice Ninja** - Requires API configuration

## 🛠️ Configuration

### Main Configuration (`config/config.ini`)
```ini
[web_interface]
host = 0.0.0.0
port = 5000
debug = False

[paperless]
api_url = http://paperless-ngx:8000
api_token = YOUR_API_TOKEN_HERE
```

### Plugin Configuration (`config/plugins.json`)
```json
{
  "paperless_ngx": {
    "enabled": true,
    "api_key": "your-api-token-here",
    "base_url": "http://paperless-ngx:8000"
  }
}
```

## � Important Notes

### For Production Use
- Change default passwords and secret keys
- Use proper SSL certificates
- Configure proper backup strategies
- Review security settings

### Development
- Volume mounts allow real-time code changes
- Logs are available in `./logs/` directory
- Use `docker-compose logs -f` for debugging

## 📖 Additional Documentation

- `setup-paperless.md` - Detailed Paperless-NGX setup guide
- `start-services.sh` - Interactive setup script
- Plugin documentation in respective plugin directories

## 🆘 Troubleshooting

### Common Issues

1. **Plugin initialization failures**:
   ```bash
   # Restart failed plugins via web interface
   # OR restart entire middleware
   docker-compose restart middleware
   ```

2. **Configuration not updating**:
   ```bash
   # Rebuild to ensure config changes are applied
   docker-compose down
   docker-compose up --build -d
   ```

3. **Service connectivity issues**:
   ```bash
   # Check if all services are on same network
   docker-compose exec middleware ping paperless-ngx
   ```

4. **Permission issues**:
   ```bash
   # Fix ownership of data directories
   sudo chown -R $USER:$USER ./data ./logs ./uploads
   ```

---

## ⚠️ Development Status

This software is in active development. While the core plugin system is functional, individual plugins may require additional configuration or development.

**Always backup your data before testing with production documents.**
