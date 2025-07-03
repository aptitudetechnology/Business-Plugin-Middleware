# BigCapital Self-Hosted Setup

This directory contains the complete setup for running BigCapital locally alongside the Business Plugin Middleware.

## Quick Start

```bash
# Start BigCapital
make up

# Initialize with default settings
make init

# Check status
make status

# View logs
make logs
```

## Overview

BigCapital is a comprehensive open-source accounting and ERP software that provides:

- **Financial Management**: Invoicing, expenses, banking, reporting
- **Inventory Management**: Products, warehouses, stock tracking  
- **Customer/Vendor Management**: Contacts, relationships, transactions
- **Multi-currency Support**: Handle international business
- **API Integration**: Full REST API for middleware integration

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   BigCapital    │    │   Business      │    │  Paperless-NGX  │
│   (Port 3000)   │◄──►│   Middleware    │◄──►│  (Port 8000)    │
│                 │    │   (Port 5000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐                        ┌─────────────────┐
│   MariaDB       │                        │   PostgreSQL    │
│   MongoDB       │                        │   Redis         │
│   Redis         │                        │   Tika/Gotenberg│
└─────────────────┘                        └─────────────────┘
```

## Services

### BigCapital Application
- **Port**: 3000
- **URL**: http://simple.local:3000
- **Default Login**: admin@bigcapital.com / admin123

### MariaDB Database
- **Port**: 3306
- **Database**: bigcapital
- **User**: bigcapital

### MongoDB
- **Port**: 27017
- **Database**: bigcapital
- **Used for**: Document storage, reports, analytics

### Redis Cache
- **Port**: 6379
- **Used for**: Session storage, caching, job queues

## Configuration

### Environment Variables

Key configuration options in `docker-compose.yml`:

```yaml
# Security (CHANGE THESE!)
JWT_SECRET: "change-me-please-jwt-secret-make-it-long-and-random"
SESSION_SECRET: "another-long-random-secret-for-sessions"

# Database passwords (CHANGE THESE!)
DB_PASSWORD: "bigcapital_secure_password"
MYSQL_ROOT_PASSWORD: "bigcapital_root_password_change_me"
MONGO_INITDB_ROOT_PASSWORD: "bigcapital_mongo_password"
REDIS_PASSWORD: "bigcapital_redis_password"

# Application
APP_URL: "http://simple.local:3000"
NODE_ENV: "production"
```

### First Time Setup

1. **Start Services**:
   ```bash
   make init
   ```

2. **Access BigCapital**: 
   - URL: http://simple.local:3000
   - Email: admin@bigcapital.com
   - Password: admin123

3. **Change Default Credentials**:
   - Go to Settings → Users
   - Update admin password
   - Update email address

4. **Configure Company**:
   - Settings → Company Information
   - Add company details, logo, etc.

5. **Setup Chart of Accounts**:
   - Settings → Chart of Accounts
   - Configure account structure

## Integration with Middleware

### API Configuration

The middleware plugin connects to BigCapital using:

```json
{
  "api_key": "your-bigcapital-api-key",
  "base_url": "http://bigcapital:3000",
  "timeout": 30
}
```

### Getting API Key

1. Login to BigCapital
2. Go to Settings → API Keys
3. Generate new API key
4. Copy the key to middleware configuration

### Middleware Integration

The BigCapital plugin provides:

- **Document Processing**: Convert receipts/invoices to BigCapital entries
- **Expense Tracking**: Auto-create expenses from documents
- **Invoice Management**: Generate invoices from processed documents
- **Contact Sync**: Automatically create vendors/customers
- **Real-time Sync**: Immediate data synchronization

## Management Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make init` | Initialize with defaults |
| `make logs` | View application logs |
| `make logs-all` | View all service logs |
| `make status` | Show service status |
| `make restart` | Restart all services |
| `make clean` | Remove containers (keep data) |
| `make clean-all` | Remove everything including data |
| `make backup` | Create data backup |
| `make update` | Update to latest version |
| `make health` | Check service health |
| `make shell` | Open shell in BigCapital container |
| `make db-shell` | Open MySQL shell |
| `make mongo-shell` | Open MongoDB shell |

## Backup and Restore

### Create Backup
```bash
make backup
```

This creates:
- MySQL dump in `./backups/bigcapital-mysql-YYYYMMDD_HHMMSS.sql`
- MongoDB dump in `./backups/bigcapital-mongo-YYYYMMDD_HHMMSS/`

### Manual Backup
```bash
# MySQL backup
docker compose exec bigcapital-mariadb mysqldump -u bigcapital -p bigcapital > backup.sql

# MongoDB backup
docker compose exec bigcapital-mongo mongodump --uri="mongodb://bigcapital:password@localhost:27017/bigcapital"
```

## Resource Requirements

### Minimum Requirements
- **RAM**: 2GB
- **Storage**: 5GB
- **CPU**: 1 core

### Recommended for Production
- **RAM**: 4GB+
- **Storage**: 20GB+ (SSD recommended)
- **CPU**: 2+ cores

## Troubleshooting

### Common Issues

1. **Services won't start**:
   ```bash
   # Check logs
   make logs-all
   
   # Restart services
   make restart
   ```

2. **Database connection errors**:
   ```bash
   # Check database health
   make health
   
   # Restart database
   docker compose restart bigcapital-mariadb
   ```

3. **Out of memory**:
   ```bash
   # Check container resources
   docker stats
   
   # Reduce memory limits in docker-compose.yml
   ```

4. **Port conflicts**:
   - Change port mappings in `docker-compose.yml`
   - Update `APP_URL` environment variable

### Log Locations

- **Application Logs**: `docker compose logs bigcapital`
- **Database Logs**: `docker compose logs bigcapital-mariadb`
- **MongoDB Logs**: `docker compose logs bigcapital-mongo`
- **Redis Logs**: `docker compose logs bigcapital-redis`

## Security Considerations

### Production Deployment

1. **Change Default Passwords**:
   - Update all password environment variables
   - Change default admin credentials

2. **Network Security**:
   - Remove port mappings for internal services
   - Use Docker networks for service communication

3. **SSL/TLS**:
   - Add reverse proxy (nginx/traefik)
   - Configure SSL certificates

4. **Backup Strategy**:
   - Automated daily backups
   - Offsite backup storage
   - Regular restore testing

### Environment Variables to Change

```bash
# Required changes for production
JWT_SECRET="your-unique-jwt-secret-min-32-chars"
SESSION_SECRET="your-unique-session-secret-min-32-chars"
DB_PASSWORD="your-secure-db-password"
MYSQL_ROOT_PASSWORD="your-secure-root-password"
MONGO_INITDB_ROOT_PASSWORD="your-secure-mongo-password"
REDIS_PASSWORD="your-secure-redis-password"
```

## Development

### Custom Configuration

1. Copy `docker-compose.yml` to `docker-compose.override.yml`
2. Modify settings for development
3. Use `make dev` for development mode

### API Development

BigCapital provides a comprehensive REST API:

- **Documentation**: http://simple.local:3000/api/docs
- **Authentication**: API Key based
- **Rate Limiting**: Configurable
- **Webhooks**: Event-based notifications

## Support

- **BigCapital Documentation**: https://docs.bigcapital.ly
- **BigCapital GitHub**: https://github.com/bigcapitalhq/bigcapital
- **API Reference**: https://developer.bigcapital.ly

## License

BigCapital is open-source software licensed under the GNU General Public License v3.0.
