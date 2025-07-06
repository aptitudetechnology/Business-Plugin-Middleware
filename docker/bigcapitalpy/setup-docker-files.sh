#!/bin/bash

# BigCapitalPy Docker Setup Script
# This script creates all necessary files and directories for the Docker setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

print_status "Setting up BigCapitalPy Docker environment..."
print_status "Project root: $PROJECT_ROOT"

# Create directory structure
print_status "Creating directory structure..."

# Docker directories
mkdir -p "$PROJECT_ROOT/docker/nginx"
mkdir -p "$PROJECT_ROOT/docker/postgres"

print_success "Created directory structure"

# Clean up any existing directories that should be files
print_status "Cleaning up existing nginx config directories..."

if [ -d "$PROJECT_ROOT/docker/nginx/nginx.conf" ]; then
    print_warning "Removing nginx.conf directory..."
    sudo rm -rf "$PROJECT_ROOT/docker/nginx/nginx.conf"
fi

if [ -d "$PROJECT_ROOT/docker/nginx/bigcapitalpy.conf" ]; then
    print_warning "Removing bigcapitalpy.conf directory..."
    sudo rm -rf "$PROJECT_ROOT/docker/nginx/bigcapitalpy.conf"
fi

# Create nginx.conf
print_status "Creating nginx.conf..."
cat > "$PROJECT_ROOT/docker/nginx/nginx.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Include server configurations
    include /etc/nginx/conf.d/*.conf;
}
EOF

# Create bigcapitalpy.conf
print_status "Creating bigcapitalpy.conf..."
cat > "$PROJECT_ROOT/docker/nginx/bigcapitalpy.conf" << 'EOF'
upstream bigcapitalpy_app {
    server bigcapitalpy:5000;
    keepalive 32;
}

server {
    listen 80;
    server_name localhost;

    # Client max body size for file uploads
    client_max_body_size 100M;
    client_body_timeout 300s;
    client_header_timeout 300s;

    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
        
        # Optional: serve pre-compressed files
        gzip_static on;
    }

    # Favicon
    location = /favicon.ico {
        alias /var/www/static/favicon.ico;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Robots.txt
    location = /robots.txt {
        alias /var/www/static/robots.txt;
        access_log off;
    }

    # Main application
    location / {
        proxy_pass http://bigcapitalpy_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        
        # Cache control
        proxy_cache_bypass $http_upgrade;
    }

    # API endpoints (if you have specific API routes)
    location /api/ {
        proxy_pass http://bigcapitalpy_app;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # API-specific settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://bigcapitalpy_app/health;
        proxy_set_header Host $host;
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
        proxy_read_timeout 5s;
    }

    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /404.html {
        root /usr/share/nginx/html;
        internal;
    }
    
    location = /50x.html {
        root /usr/share/nginx/html;
        internal;
    }
}
EOF

# Create PostgreSQL init script
print_status "Creating PostgreSQL initialization script..."
cat > "$PROJECT_ROOT/docker/postgres/init.sql" << 'EOF'
-- BigCapitalPy Database Initialization
-- This script runs when the PostgreSQL container starts for the first time

-- Create additional databases if needed
-- CREATE DATABASE bigcapitalpy_test;

-- Create extensions that might be useful for accounting software
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create additional users if needed
-- CREATE USER bigcapital_readonly WITH PASSWORD 'readonly123';
-- GRANT CONNECT ON DATABASE bigcapitalpy TO bigcapital_readonly;
-- GRANT USAGE ON SCHEMA public TO bigcapital_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO bigcapital_readonly;

-- Set timezone (adjust as needed)
SET timezone = 'UTC';

-- Create initial schema or tables here if needed
-- Example:
-- CREATE TABLE IF NOT EXISTS app_info (
--     id SERIAL PRIMARY KEY,
--     version VARCHAR(50),
--     initialized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- Insert initial data
-- INSERT INTO app_info (version) VALUES ('1.0.0') ON CONFLICT DO NOTHING;

COMMIT;
EOF

# Create environment file template
print_status "Creating .env template..."
cat > "$PROJECT_ROOT/.env.example" << 'EOF'
# BigCapitalPy Environment Variables
# Copy this file to .env and update the values

# Database
DB_PASSWORD=bigcapital123

# Redis
REDIS_PASSWORD=redis123

# Application
SECRET_KEY=change-this-in-production-use-a-long-random-string
FLASK_ENV=development

# pgAdmin
PGADMIN_EMAIL=admin@bigcapitalpy.com
PGADMIN_PASSWORD=admin123

# Optional: Additional settings
# FLASK_DEBUG=True
# LOG_LEVEL=INFO
EOF

# Create .env file if it doesn't exist
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    print_status "Creating .env file from template..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    print_warning "Please review and update the .env file with your preferred settings"
fi

# Create .gitignore if it doesn't exist
if [ ! -f "$PROJECT_ROOT/.gitignore" ]; then
    print_status "Creating .gitignore file..."
    cat > "$PROJECT_ROOT/.gitignore" << 'EOF'
# Environment files
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
ENV/
env/
.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Uploads
uploads/
static/uploads/

# Docker
.dockerignore

# Backup files
*.bak
*.backup
EOF
fi

# Create basic Dockerfile if it doesn't exist
if [ ! -f "$PROJECT_ROOT/Dockerfile" ]; then
    print_status "Creating basic Dockerfile..."
    cat > "$PROJECT_ROOT/Dockerfile" << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "app.py"]
EOF
fi

# Create basic requirements.txt if it doesn't exist
if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    print_status "Creating basic requirements.txt..."
    cat > "$PROJECT_ROOT/requirements.txt" << 'EOF'
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Flask-WTF==1.1.1
WTForms==3.0.1
psycopg2-binary==2.9.7
redis==4.6.0
python-dotenv==1.0.0
Werkzeug==2.3.7
Jinja2==3.1.2
gunicorn==21.2.0
EOF
fi

# Set proper permissions
print_status "Setting file permissions..."
chmod 644 "$PROJECT_ROOT/docker/nginx/nginx.conf"
chmod 644 "$PROJECT_ROOT/docker/nginx/bigcapitalpy.conf"
chmod 644 "$PROJECT_ROOT/docker/postgres/init.sql"
chmod 644 "$PROJECT_ROOT/.env.example"

if [ -f "$PROJECT_ROOT/.env" ]; then
    chmod 600 "$PROJECT_ROOT/.env"  # More restrictive for actual env file
fi

# Make script executable
chmod +x "$0"

print_success "Docker setup completed successfully!"
print_status "Files created:"
echo "  - docker/nginx/nginx.conf"
echo "  - docker/nginx/bigcapitalpy.conf"
echo "  - docker/postgres/init.sql"
echo "  - .env.example"
echo "  - .gitignore (if not existing)"
echo "  - Dockerfile (if not existing)"
echo "  - requirements.txt (if not existing)"

if [ -f "$PROJECT_ROOT/.env" ]; then
    print_warning "Please review the .env file and update passwords and secrets"
fi

print_status "Next steps:"
echo "1. Review and update the .env file with your preferred settings"
echo "2. Update the docker-compose.yml file"
echo "3. Run: docker-compose up -d"
echo "4. Access your application at: http://localhost"
echo "5. Access pgAdmin at: http://localhost:8080 (with --profile admin)"

print_success "Setup complete! 🚀