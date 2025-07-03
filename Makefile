# Business Plugin Middleware - Makefile
# Updated for new plugin-based architecture

# Variables
IMAGE_NAME = business-plugin-middleware
CONTAINER_NAME = business-plugin-middleware
COMPOSE_FILE = docker-compose.yml

# Default target
.PHONY: help
help:
	@echo "Business Plugin Middleware - Available Commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make up          - Build and start all services (uses cache)"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make rebuild     - Force rebuild and start (no cache - use after code changes)"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make build       - Build the middleware image (uses cache)"
	@echo "  make rebuild     - Force rebuild without cache (recommended after code changes)"
	@echo "  make fresh       - Stop, rebuild everything from scratch, and start"
	@echo "  make logs        - Follow logs from all services"
	@echo "  make logs-middleware - Follow only middleware logs"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean       - Stop and remove containers"
	@echo "  make clean-all   - Clean everything including volumes"
	@echo "  make shell       - Access middleware container shell"
	@echo ""
	@echo "🔍 Debugging:"
	@echo "  make status      - Show service status"
	@echo "  make config      - Show current configuration"
	@echo "  make test-plugins - Test plugin connectivity"

# Main targets
.PHONY: up
up:
	@echo "🚀 Building and starting all services..."
	@echo "🔧 Ensuring Docker network exists..."
	@docker network create paperless_network 2>/dev/null || echo "✓ paperless_network already exists"
	docker-compose -f $(COMPOSE_FILE) up --build -d
	@echo "✅ Services started!"
	@echo "🌐 Middleware: http://localhost:5000"
	@echo "📄 Paperless-NGX: http://localhost:8000"

.PHONY: down
down:
	@echo "🛑 Stopping all services..."
	docker-compose -f $(COMPOSE_FILE) down
	@echo "✅ All services stopped"

.PHONY: restart
restart:
	@echo "🔄 Restarting all services..."
	docker-compose -f $(COMPOSE_FILE) restart
	@echo "✅ All services restarted"

.PHONY: restart-middleware
restart-middleware:
	@echo "🔄 Restarting middleware only..."
	docker-compose -f $(COMPOSE_FILE) restart middleware
	@echo "✅ Middleware restarted"

# Build targets
.PHONY: build
build:
	@echo "🔨 Building middleware image (using cache)..."
	docker-compose -f $(COMPOSE_FILE) build middleware

.PHONY: rebuild
rebuild:
	@echo "🔨 Force rebuilding all images (no cache)..."
	docker-compose -f $(COMPOSE_FILE) build --no-cache
	docker-compose -f $(COMPOSE_FILE) up -d

.PHONY: fresh
fresh:
	@echo "🧹 Stopping containers and rebuilding from scratch..."
	docker-compose -f $(COMPOSE_FILE) down
	@echo "🔧 Ensuring Docker network exists..."
	@docker network create paperless_network 2>/dev/null || echo "✓ paperless_network already exists"
	docker-compose -f $(COMPOSE_FILE) build --no-cache --pull
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "✅ Fresh build complete!"
	@echo "🌐 Middleware: http://localhost:5000"

# Logging targets
.PHONY: logs
logs:
	@echo "📋 Following logs from all services (Ctrl+C to exit)..."
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: logs-middleware
logs-middleware:
	@echo "📋 Following middleware logs (Ctrl+C to exit)..."
	docker-compose -f $(COMPOSE_FILE) logs -f middleware

.PHONY: logs-paperless
logs-paperless:
	@echo "📋 Following Paperless-NGX logs (Ctrl+C to exit)..."
	docker-compose -f $(COMPOSE_FILE) logs -f paperless-ngx

# Maintenance targets
.PHONY: clean
clean:
	@echo "🧹 Cleaning up containers..."
	docker-compose -f $(COMPOSE_FILE) down --remove-orphans
	@echo "✅ Containers cleaned"

.PHONY: clean-all
clean-all:
	@echo "🧹 Cleaning everything (containers, volumes, images)..."
	docker-compose -f $(COMPOSE_FILE) down --remove-orphans --volumes
	docker image prune -f
	@echo "✅ Everything cleaned"

# Development and debugging targets
.PHONY: shell
shell:
	@echo "🐚 Accessing middleware container shell..."
	docker-compose -f $(COMPOSE_FILE) exec middleware bash

.PHONY: status
status:
	@echo "📊 Service status:"
	docker-compose -f $(COMPOSE_FILE) ps

.PHONY: config
config:
	@echo "⚙️ Current configuration:"
	@echo "--- config.ini ---"
	@cat config/config.ini 2>/dev/null || echo "config.ini not found"
	@echo ""
	@echo "--- plugins.json ---"
	@cat config/plugins.json 2>/dev/null || echo "plugins.json not found"

.PHONY: test-plugins
test-plugins:
	@echo "🔌 Testing plugin connectivity..."
	@docker-compose -f $(COMPOSE_FILE) exec middleware python -c "\
import sys; sys.path.append('/app'); \
from core.plugin_manager import PluginManager; \
from config.settings import load_config; \
config = load_config(); \
pm = PluginManager(config); \
print('Discovered plugins:', pm.discover_plugins())" || echo "❌ Failed to test plugins"

# Setup and initialization
.PHONY: init
init:
	@echo "🚀 Initializing Business Plugin Middleware..."
	@echo "📁 Creating necessary directories..."
	@mkdir -p data logs uploads config
	@echo "🔧 Setting up configuration files..."
	@test -f config/config.ini || cp config/config.ini.example config/config.ini 2>/dev/null || echo "No example config found"
	@echo "🐳 Building and starting services..."
	@make up
	@echo ""
	@echo "✅ Initialization complete!"
	@echo "🌐 Access the web interface at: http://localhost:5000"
	@echo "📖 Check README.md for configuration instructions"

# Shortcuts for common operations
.PHONY: start stop restart-mid
start: up
stop: down
restart-mid: restart-middleware
