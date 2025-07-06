# ⚠️ **CRITICAL WARNING - READ BEFORE PROCEEDING** ⚠️

> ## 🚨 PRE-ALPHA SOFTWARE - NOT FUNCTIONAL 🚨
> 
> **THIS PROJECT IS CURRENTLY IN PRE-ALPHA DEVELOPMENT AND IS NOT YET FUNCTIONAL.**
> 
> ### ❌ DO NOT USE FOR:
> - Production environments
> - Business-critical data
> - Live financial systems
> - Any mission-critical applications
> 
> ### ⚠️ IMPORTANT DISCLAIMERS:
> - **DATA LOSS RISK**: This software may corrupt, lose, or mishandle your data
> - **NO RELIABILITY GUARANTEE**: Features may not work as expected or at all
> - **BREAKING CHANGES**: API and functionality will change without notice
> - **NO SUPPORT**: Limited or no support available during pre-alpha phase
> 
> ### 🔬 INTENDED FOR:
> - Development and testing purposes only
> - Contributors and early adopters willing to accept risks
> - Non-critical experimentation environments
> 
> **By using this software, you acknowledge and accept full responsibility for any potential data loss, system issues, or other consequences.**

---


# Business Plugin Middleware

**A document processing middleware that bridges document management systems (like Paperless-NGX) with accounting platforms (like BigCapital) through a modular plugin architecture.**

 <img src="https://img.shields.io/badge/license-AGPL-blue.svg" alt="AGPL License"/>
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

Based on the original [Simplified Paperless BigCapital Middleware](https://github.com/aptitudetechnology/simplified-paperless-bigcapital-middleware), this version provides a comprehensive plugin-based architecture for connecting document management systems with accounting platforms, automating the flow from document ingestion to accounting entry creation.

## 🌟 Key Features

- **� Document-to-Accounting Bridge** - Seamlessly connects document management with accounting systems
- **�🔌 Plugin-Based Architecture** - Easily extensible with new integrations (BigCapital, Invoice Ninja, etc.)
- **📄 Smart Document Processing** - OCR extraction and automated data mapping for invoices and receipts
- **🌐 Modern Web Interface** - Intuitive dashboard for managing documents, plugins, and integrations
- **📊 System Diagnostics** - Built-in connectivity tests and container monitoring
- **🐳 Docker Ready** - Complete containerized deployment with Docker Compose
- **📝 Advanced Logging** - Comprehensive logging with Loguru for better debugging
- **🔄 Real-time Processing** - View and process OCR content directly from the web interface
- **⚙️ Dynamic Configuration** - Configure plugins through web UI or configuration files
- **🔒 Network Flexibility** - Supports various deployment scenarios (Docker, VM, host)

## ⚡ Quick Start

### Prerequisites
- **Docker** (version 20.10+ recommended) 
- **Docker Compose** (version 2.0+ **REQUIRED**)
  - ⚠️ **Important**: This project uses Docker Compose v2 syntax
  - Check version: `docker-compose --version` (should show v2.x.x)
  - [Upgrade instructions](docker/bigcapital/README.md#upgrading-docker-compose) if needed
- **Git** for cloning the repository
- **At least 4GB RAM** for basic setup (8GB+ recommended with BigCapital)
- **20GB+ free storage** for document processing and databases

### Method 1: Standard Installation (Paperless-NGX + Middleware)

This is the base installation that provides document processing with Paperless-NGX and the middleware bridge. **Note:** To fully utilize the middleware, you'll need to add accounting system integrations (like BigCapital) - see Method 2 for complete integration.

```bash
# 1. Clone the repository
git clone <repository-url>
cd Business-Plugin-Middleware

# 2. Start the standard setup
make up

# 3. Wait for services to initialize (2-3 minutes)
# Monitor startup progress
make logs

# 4. Access the applications
# - Middleware: http://simple.local:5000
# - Paperless-NGX: http://simple.local:8000
```

### Method 2: Full Installation (+ BigCapital Self-Hosted) **[RECOMMENDED]**

This is the complete installation that includes self-hosted BigCapital accounting system, providing the full document-to-accounting workflow that the middleware is designed for.

#### Step 1: Install Standard Setup
```bash
# Clone and start the base system first
git clone <repository-url>
cd Business-Plugin-Middleware
make up
```

#### Step 2: Add BigCapital Integration
```bash
# Navigate to BigCapital setup
cd docker/bigcapital

# Initialize BigCapital (will start MariaDB, MongoDB, Redis, BigCapital)
make init

# Check BigCapital status
make status

# Access BigCapital at http://simple.local:3000
# Default login: admin@bigcapital.com / admin123
```

#### Step 3: Integration with Main Middleware
```bash
# Option A: Use integrated docker-compose (recommended)
cd ../..  # Back to project root

# Copy BigCapital services to main compose file
# (Manual step - see Integration Guide below)

# Restart with integrated services
docker compose down
docker compose up -d

# Option B: Run BigCapital standalone
# Keep BigCapital running separately and configure middleware to connect
```

### Method 3: Selective Installation

Install only the components you need:

```bash
# Clone repository
git clone <repository-url>
cd Business-Plugin-Middleware

# Option 1: Middleware only (no Paperless-NGX)
docker compose up middleware -d

# Option 2: BigCapital only
cd docker/bigcapital
make up

# Option 3: Custom configuration
# Edit docker-compose.yml to comment out unwanted services
nano docker-compose.yml
docker compose up -d
```

## 🔗 BigCapital Integration Guide

### Automatic Integration (Recommended)

1. **Copy BigCapital services to main compose file**:
   ```bash
   # Use the provided integration template
   cat docker/bigcapital/integration.yml >> docker-compose.yml
   
   # Edit the file to uncomment BigCapital services
   nano docker-compose.yml
   ```

2. **Add BigCapital to middleware dependencies**:
   ```yaml
   # In docker-compose.yml, update middleware service:
   middleware:
     depends_on:
       - paperless-ngx
       - bigcapital  # Add this line
       - gotenberg
       - tika
   ```

3. **Add required volumes**:
   ```yaml
   # Add to the volumes section:
   volumes:
     # ...existing volumes...
     bigcapital_mariadb:
     bigcapital_mongo:
     bigcapital_mongo_config:
     bigcapital_redis:
     bigcapital_uploads:
     bigcapital_storage:
     bigcapital_logs:
   ```

4. **Start integrated environment**:
   ```bash
   # Stop current services
   docker compose down
   
   # Start with BigCapital integration
   docker compose up -d
   
   # Check all services are running
   docker compose ps
   ```

### Manual Integration (Advanced Users)

1. **Run BigCapital separately**:
   ```bash
   cd docker/bigcapital
   make up
   ```

2. **Configure middleware to connect**:
   ```bash
   # Edit plugin configuration
   nano config/plugins.json
   
   # Update BigCapital section:
   {
     "plugins": {
       "bigcapital": {
         "enabled": true,
         "api_key": "your-api-key-here",
         "base_url": "http://bigcapital:3000",
         "timeout": 30
       }
     }
   }
   ```

3. **Restart middleware**:
   ```bash
   docker compose restart middleware
   ```

## 🚀 Post-Installation Setup

### 1. Configure Paperless-NGX

```bash
# Access Paperless-NGX
open http://simple.local:8000

# Create admin user (if not exists)
docker compose exec paperless-ngx python manage.py createsuperuser

# Generate API token
# 1. Login to Paperless-NGX
# 2. Go to Settings → API Tokens
# 3. Create new token
# 4. Copy token for middleware configuration
```

### 2. Configure BigCapital (if installed)

```bash
# Access BigCapital
open http://simple.local:3000

# Default credentials:
# Email: admin@bigcapital.com
# Password: admin123

# IMPORTANT: Change default credentials immediately!
# 1. Login with defaults
# 2. Go to Settings → Users
# 3. Update admin password and email
# 4. Configure company information
```

### 3. Configure Middleware Plugins

#### Via Web Interface (Recommended):
```bash
# Access middleware
open http://simple.local:5000/plugins

# Configure each plugin:
# 1. Click "Configure" next to any plugin
# 2. Enter API keys and settings
# 3. Test connection
# 4. Save configuration
```

#### Via Configuration Files:
```bash
# Edit plugin settings
nano config/plugins.json

# Example configuration:
{
  "plugins": {
    "paperless_ngx": {
      "enabled": true,
      "api_key": "your-paperless-api-token",
      "base_url": "http://paperless-ngx:8000",
      "hostname_url": "http://simple.local:8000"
    },
    "bigcapital": {
      "enabled": true,
      "api_key": "your-bigcapital-api-key",
      "base_url": "http://bigcapital:3000"
    }
  }
}

# Restart middleware to apply changes
docker compose restart middleware
```

### 4. System Verification

```bash
# Check all services are running
docker compose ps

# Test system connectivity
open http://simple.local:5000/system

# View application logs
make logs

# Check BigCapital health (if installed)
cd docker/bigcapital
make health
```

## 📊 Service Overview

## 🐳 Docker Management

### Standard Docker Commands

```bash
# Using the Makefile (Recommended)
make up             # Build and start all services
make start          # Start services without rebuilding  
make stop           # Stop all services
make restart        # Restart middleware only
make logs           # View logs
make fresh          # Fresh rebuild (clears cache)
make clean          # Clean up everything
make help           # Show all available commands

# Manual Docker Compose Commands
docker compose up --build -d              # Start all services (build if needed)
docker compose down                       # Stop all services
docker compose restart middleware         # Restart just the middleware
docker compose logs -f middleware         # View middleware logs
docker compose logs -f paperless-ngx      # View Paperless-NGX logs
docker compose build --no-cache middleware # Rebuild after code changes
docker compose up -d middleware           # Start updated middleware
```

### BigCapital Docker Management

```bash
# Navigate to BigCapital directory
cd docker/bigcapital

# Essential BigCapital commands
make help           # Show all available commands
make up             # Start BigCapital services
make down           # Stop BigCapital services  
make init           # Initialize with default settings
make status         # Show service status
make logs           # View application logs
make logs-all       # View all service logs
make health         # Check service health
make restart        # Restart services
make update         # Update to latest version

# Data management
make backup         # Create data backup
make clean          # Remove containers (keep data)
make clean-all      # Remove everything including data (DESTRUCTIVE!)

# Database access
make db-shell       # Open MySQL shell
make mongo-shell    # Open MongoDB shell
make shell          # Open BigCapital container shell

# Development
make dev            # Start in development mode with live logs
```

### Integration Management

```bash
# Full stack management (when BigCapital is integrated)
cd ../..  # Back to project root

# Start everything
docker compose up -d

# Stop everything  
docker compose down

# Restart specific services
docker compose restart middleware bigcapital

# View logs for integrated setup
docker compose logs -f middleware
docker compose logs -f bigcapital
docker compose logs -f bigcapital-mariadb

# Check all service status
docker compose ps
```

## 🔧 Advanced Configuration

### Production Security Checklist

Before deploying to production, ensure you:

#### 1. Change Default Passwords
```bash
# BigCapital passwords (in docker-compose.yml or .env)
JWT_SECRET="your-unique-jwt-secret-min-32-chars"
SESSION_SECRET="your-unique-session-secret-min-32-chars"  
DB_PASSWORD="your-secure-db-password"
MYSQL_ROOT_PASSWORD="your-secure-root-password"
MONGO_INITDB_ROOT_PASSWORD="your-secure-mongo-password"
REDIS_PASSWORD="your-secure-redis-password"

# Paperless-NGX secrets
PAPERLESS_SECRET_KEY="your-unique-paperless-secret"
```

#### 2. Network Security
```bash
# Remove port mappings for internal services
# Comment out these lines in docker-compose.yml for production:
# ports:
#   - "3306:3306"  # MariaDB
#   - "27017:27017"  # MongoDB  
#   - "6379:6379"  # Redis
```

#### 3. SSL/TLS Configuration
```bash
# Add reverse proxy (nginx/traefik)
# Configure SSL certificates
# Update APP_URL to use https://
```

### Backup Strategy

#### Automated Backups
```bash
# Set up automated BigCapital backups
cd docker/bigcapital
make backup

# Schedule daily backups (add to crontab)
0 2 * * * cd /path/to/Business-Plugin-Middleware/docker/bigcapital && make backup

# Backup middleware data
docker run --rm \
  -v middleware_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/middleware-data-$(date +%Y%m%d).tar.gz -C /data .
```

#### Backup Verification
```bash
# Test backup integrity
cd docker/bigcapital/backups
file bigcapital-mysql-*.sql
tar -tzf bigcapital-volumes-*.tar.gz | head

# Test restore process in development environment
```

### Performance Optimization

#### Resource Monitoring
```bash
# Monitor resource usage
docker stats

# Check specific service resources
docker stats middleware paperless-ngx bigcapital

# Monitor disk usage
docker system df
df -h  # Host filesystem
```

#### Database Optimization
```bash
# Optimize BigCapital MariaDB
cd docker/bigcapital
make db-shell

# Run optimization queries:
# OPTIMIZE TABLE invoices;
# OPTIMIZE TABLE expenses;
# OPTIMIZE TABLE contacts;
# ANALYZE TABLE invoices;

# MongoDB maintenance
make mongo-shell
# Run: db.runCommand({compact: "collection_name"})
```

### Custom Configuration

#### Environment Variables
```bash
# Create custom environment file
cp docker/bigcapital/.env.example docker/bigcapital/.env

# Edit with your settings
nano docker/bigcapital/.env

# Restart to apply changes
cd docker/bigcapital
make restart
```

#### Custom Docker Compose Override
```bash
# Create override file for customizations
cp docker-compose.yml docker-compose.override.yml

# Edit override file with your changes
nano docker-compose.override.yml

# Restart with overrides
docker compose up -d
```

## 📊 Monitoring and Maintenance

### Health Monitoring

#### Built-in Health Checks
```bash
# Middleware health check
curl http://simple.local:5000/api/health

# BigCapital health check  
curl http://simple.local:3000/health

# System diagnostics page
open http://simple.local:5000/system
```

#### Container Health Status
```bash
# Check container health
docker compose ps

# View health check logs
docker inspect --format='{{.State.Health.Status}}' middleware
docker inspect --format='{{.State.Health.Log}}' bigcapital
```

### Log Management

#### Log Locations
```bash
# Application logs
./logs/middleware.log
./logs/app.log

# Container logs  
docker compose logs middleware
docker compose logs bigcapital
docker compose logs paperless-ngx

# BigCapital specific logs
cd docker/bigcapital
make logs-all
```

#### Log Rotation
```bash
# Configure log rotation in docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "200k"
    max-file: "10"
```

### Maintenance Tasks

#### Regular Maintenance
```bash
# Weekly maintenance script
#!/bin/bash

# Clean up Docker resources
docker system prune -f

# Backup data
cd docker/bigcapital
make backup

# Update services
make update

# Check health
make health

# Restart if needed
make restart
```

#### Database Maintenance
```bash
# Monthly database optimization
cd docker/bigcapital

# MariaDB maintenance
make db-shell
# Run database optimization queries

# MongoDB maintenance  
make mongo-shell
# Run collection compaction

# Check database sizes
docker exec bigcapital-mariadb du -sh /var/lib/mysql
docker exec bigcapital-mongo du -sh /data/db
```

## 🔗 Integration Examples

### Custom Plugin Development

Example of integrating a new accounting system:

```python
# plugins/your_accounting_system/plugin.py
from core.base_plugin import IntegrationPlugin

class YourAccountingPlugin(IntegrationPlugin):
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.client = None
        
    def initialize(self, app_context):
        # Initialize your API client
        api_key = self.config.get('api_key')
        base_url = self.config.get('base_url')
        self.client = YourAccountingClient(api_key, base_url)
        return self.test_connection()
        
    def test_connection(self):
        try:
            return self.client.ping()
        except Exception:
            return False
            
    def sync_data(self, data):
        # Implement your sync logic
        document = data.get('document')
        # Process document and create accounting entry
        return {'success': True, 'entry_id': 'created_id'}
```

### Webhook Integration

```python
# Add webhook support for real-time document processing
@app.route('/webhook/document-processed', methods=['POST'])
def document_processed_webhook():
    document_data = request.json
    
    # Process with all enabled plugins
    for plugin in plugin_manager.get_integration_plugins():
        if plugin.enabled:
            result = plugin.sync_data({
                'type': 'document',
                'document': document_data
            })
            logger.info(f"Plugin {plugin.name} result: {result}")
    
    return jsonify({'status': 'processed'})
```

## 🆘 Support and Community

### Getting Help

1. **Documentation**: Check the `/docs` directory for detailed guides
2. **System Diagnostics**: Use http://simple.local:5000/system for automated diagnostics  
3. **Issues**: Report bugs and feature requests via GitHub Issues
4. **Community**: Join our discussions for help and collaboration

### Useful Resources

- **BigCapital Documentation**: https://docs.bigcapital.ly
- **Paperless-NGX Documentation**: https://paperless-ngx.readthedocs.io
- **Docker Documentation**: https://docs.docker.com
- **Plugin Development Guide**: See `/docs/plugin-development.md`

### Contributing

1. Fork the repository
2. Create a feature branch  
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## 🔮 Roadmap

### Current Focus (Q1 2025)
- ✅ **BigCapital Self-Hosted Integration** - Complete Docker setup
- ✅ **Enhanced Plugin Architecture** - Fault-tolerant plugin loading
- ✅ **System Diagnostics** - Built-in connectivity and health monitoring
- 🔄 **Production Hardening** - Security enhancements and performance optimization

### Short Term (Q2 2025)
- [ ] **Advanced OCR with AI/ML** - Improved document classification and data extraction
- [ ] **Webhook Support** - Real-time integrations and event-driven processing
- [ ] **Enhanced Security** - OAuth integration, JWT tokens, role-based access
- [ ] **Mobile Interface** - Responsive design improvements for mobile devices

### Medium Term (Q3-Q4 2025)
- [ ] **Multi-tenant Support** - Support for multiple organizations
- [ ] **Advanced Reporting** - Cross-system analytics and dashboards  
- [ ] **API Rate Limiting** - Enhanced API management and caching
- [ ] **Plugin Marketplace** - Community plugin sharing and distribution

### Long Term (2026+)
- [ ] **Cloud Integration** - AWS, Azure, GCP deployment options
- [ ] **Machine Learning** - Automated document classification and routing
- [ ] **Enterprise Features** - SSO, audit logging, compliance reporting
- [ ] **Microservices Architecture** - Scalable, distributed processing

---

**⚠️ Development Status**: This software is actively maintained and suitable for production use with proper configuration. The BigCapital integration is in active development - always backup your data before deploying in production environments.
