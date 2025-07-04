# Business Plugin Middleware - Makefile
# Updated for modern Docker Compose and improved architecture

# Variables
IMAGE_NAME := business-plugin-middleware
CONTAINER_NAME := business-plugin-middleware
COMPOSE_FILE := docker-compose.yml
NETWORK_NAME := paperless_network

# Docker Compose command (modern syntax)
DOCKER_COMPOSE := docker compose -f $(COMPOSE_FILE)

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "$(CYAN)Business Plugin Middleware - Available Commands:$(NC)"
	@echo ""
	@echo "$(GREEN)🚀 Quick Start:$(NC)"
	@echo "  $(YELLOW)make up$(NC)          - Build and start all services (uses cache)"
	@echo "  $(YELLOW)make down$(NC)        - Stop all services"
	@echo "  $(YELLOW)make restart$(NC)     - Restart all services"
	@echo "  $(YELLOW)make rebuild$(NC)     - Force rebuild and start (no cache - use after code changes)"
	@echo ""
	@echo "$(GREEN)🔧 Development:$(NC)"
	@echo "  $(YELLOW)make build$(NC)       - Build the middleware image (uses cache)"
	@echo "  $(YELLOW)make rebuild$(NC)     - Force rebuild without cache (recommended after code changes)"
	@echo "  $(YELLOW)make fresh$(NC)       - Stop, rebuild everything from scratch, and start"
	@echo "  $(YELLOW)make logs$(NC)        - Follow logs from all services"
	@echo "  $(YELLOW)make logs-middleware$(NC) - Follow only middleware logs"
	@echo ""
	@echo "$(GREEN)🧹 Maintenance:$(NC)"
	@echo "  $(YELLOW)make clean$(NC)       - Stop and remove containers"
	@echo "  $(YELLOW)make clean-all$(NC)   - Clean everything including volumes and images"
	@echo "  $(YELLOW)make shell$(NC)       - Access middleware container shell"
	@echo "  $(YELLOW)make prune$(NC)       - Remove unused Docker resources"
	@echo ""
	@echo "$(GREEN)🔍 Debugging:$(NC)"
	@echo "  $(YELLOW)make status$(NC)      - Show service status"
	@echo "  $(YELLOW)make config$(NC)      - Show current configuration"
	@echo "  $(YELLOW)make test-plugins$(NC) - Test plugin connectivity"
	@echo "  $(YELLOW)make health$(NC)      - Check service health"
	@echo "  $(YELLOW)make debug-mongo$(NC) - Debug MongoDB connection issues"
	@echo ""
	@echo "$(GREEN)🚀 Setup:$(NC)"
	@echo "  $(YELLOW)make init$(NC)        - Initialize project (first time setup)"

# Network management
.PHONY: network-create network-remove
network-create:
	@echo "$(BLUE)🔧 Ensuring Docker network exists...$(NC)"
	@docker network create $(NETWORK_NAME) 2>/dev/null || echo "$(GREEN)✓ $(NETWORK_NAME) already exists$(NC)"

network-remove:
	@echo "$(BLUE)🗑️  Removing Docker network...$(NC)"
	@docker network rm $(NETWORK_NAME) 2>/dev/null || echo "$(YELLOW)⚠️  Network $(NETWORK_NAME) doesn't exist$(NC)"

# Main service management targets
.PHONY: up
up: network-create
	@echo "$(GREEN)🚀 Building and starting all services...$(NC)"
	$(DOCKER_COMPOSE) up --build -d
	@echo "$(GREEN)✅ Services started!$(NC)"
	@echo "$(CYAN)🌐 Middleware: http://localhost:5000$(NC)"
	@echo "$(CYAN)📄 Paperless-NGX: http://localhost:8000$(NC)"

.PHONY: down
down:
	@echo "$(YELLOW)🛑 Stopping all services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ All services stopped$(NC)"

.PHONY: restart
restart:
	@echo "$(BLUE)🔄 Restarting all services...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✅ All services restarted$(NC)"

.PHONY: restart-middleware
restart-middleware:
	@echo "$(BLUE)🔄 Restarting middleware only...$(NC)"
	$(DOCKER_COMPOSE) restart middleware
	@echo "$(GREEN)✅ Middleware restarted$(NC)"

# Build targets
.PHONY: build
build:
	@echo "$(BLUE)🔨 Building middleware image (using cache)...$(NC)"
	$(DOCKER_COMPOSE) build middleware

.PHONY: rebuild
rebuild:
	@echo "$(BLUE)🔨 Force rebuilding all images (no cache)...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache
	$(DOCKER_COMPOSE) up -d

.PHONY: fresh
fresh: down network-create
	@echo "$(PURPLE)🧹 Rebuilding from scratch...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache --pull
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Fresh build complete!$(NC)"
	@echo "$(CYAN)🌐 Middleware: http://localhost:5000$(NC)"

# Logging targets
.PHONY: logs
logs:
	@echo "$(CYAN)📋 Following logs from all services (Ctrl+C to exit)...$(NC)"
	$(DOCKER_COMPOSE) logs -f

.PHONY: logs-middleware
logs-middleware:
	@echo "$(CYAN)📋 Following middleware logs (Ctrl+C to exit)...$(NC)"
	$(DOCKER_COMPOSE) logs -f middleware

.PHONY: logs-paperless
logs-paperless:
	@echo "$(CYAN)📋 Following Paperless-NGX logs (Ctrl+C to exit)...$(NC)"
	$(DOCKER_COMPOSE) logs -f paperless-ngx

.PHONY: logs-mongodb
logs-mongodb:
	@echo "$(CYAN)📋 Following MongoDB logs (Ctrl+C to exit)...$(NC)"
	$(DOCKER_COMPOSE) logs -f mongodb

# Maintenance targets
.PHONY: clean
clean:
	@echo "$(YELLOW)🧹 Cleaning up containers...$(NC)"
	$(DOCKER_COMPOSE) down --remove-orphans
	@echo "$(GREEN)✅ Containers cleaned$(NC)"

.PHONY: clean-all
clean-all:
	@echo "$(RED)🧹 Cleaning everything (containers, volumes, images)...$(NC)"
	$(DOCKER_COMPOSE) down --remove-orphans --volumes
	@docker image prune -f
	@echo "$(GREEN)✅ Everything cleaned$(NC)"

.PHONY: prune
prune:
	@echo "$(YELLOW)🗑️  Removing unused Docker resources...$(NC)"
	@docker system prune -f
	@docker volume prune -f
	@echo "$(GREEN)✅ Docker resources pruned$(NC)"

# Development and debugging targets
.PHONY: shell
shell:
	@echo "$(CYAN)🐚 Accessing middleware container shell...$(NC)"
	$(DOCKER_COMPOSE) exec middleware bash

.PHONY: shell-root
shell-root:
	@echo "$(CYAN)🐚 Accessing middleware container shell as root...$(NC)"
	$(DOCKER_COMPOSE) exec --user root middleware bash

.PHONY: status
status:
	@echo "$(CYAN)📊 Service status:$(NC)"
	$(DOCKER_COMPOSE) ps

.PHONY: health
health:
	@echo "$(CYAN)🏥 Checking service health...$(NC)"
	@$(DOCKER_COMPOSE) ps --format table
	@echo ""
	@echo "$(CYAN)🔍 Container resource usage:$(NC)"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

.PHONY: config
config:
	@echo "$(CYAN)⚙️ Current configuration:$(NC)"
	@echo "$(YELLOW)--- config.ini ---$(NC)"
	@cat config/config.ini 2>/dev/null || echo "$(RED)❌ config.ini not found$(NC)"
	@echo ""
	@echo "$(YELLOW)--- plugins.json ---$(NC)"
	@cat config/plugins.json 2>/dev/null || echo "$(RED)❌ plugins.json not found$(NC)"

.PHONY: test-plugins
test-plugins:
	@echo "$(CYAN)🔌 Testing plugin connectivity...$(NC)"
	@$(DOCKER_COMPOSE) exec middleware python -c "\
import sys; sys.path.append('/app'); \
from core.plugin_manager import PluginManager; \
from config.settings import load_config; \
config = load_config(); \
pm = PluginManager(config); \
print('Discovered plugins:', pm.discover_plugins())" || echo "$(RED)❌ Failed to test plugins$(NC)"

# Setup and initialization
.PHONY: init
init:
	@echo "$(GREEN)🚀 Initializing Business Plugin Middleware...$(NC)"
	@echo "$(BLUE)📁 Creating necessary directories...$(NC)"
	@mkdir -p data logs uploads config
	@echo "$(BLUE)🔧 Setting up configuration files...$(NC)"
	@test -f config/config.ini || cp config/config.ini.example config/config.ini 2>/dev/null || echo "$(YELLOW)⚠️  No example config found$(NC)"
	@echo "$(BLUE)🐳 Building and starting services...$(NC)"
	@$(MAKE) up
	@echo ""
	@echo "$(GREEN)✅ Initialization complete!$(NC)"
	@echo "$(CYAN)🌐 Access the web interface at: http://localhost:5000$(NC)"
	@echo "$(CYAN)📖 Check README.md for configuration instructions$(NC)"

# Backup and restore
.PHONY: backup restore
backup:
	@echo "$(BLUE)💾 Creating backup...$(NC)"
	@mkdir -p backups
	@tar -czf backups/backup-$(shell date +%Y%m%d_%H%M%S).tar.gz data config
	@echo "$(GREEN)✅ Backup created in backups/$(NC)"

restore:
	@echo "$(YELLOW)📥 Available backups:$(NC)"
	@ls -la backups/ 2>/dev/null || echo "$(RED)❌ No backups directory found$(NC)"
	@echo "$(YELLOW)To restore: tar -xzf backups/backup-YYYYMMDD_HHMMSS.tar.gz$(NC)"

# Environment and dependency checks
.PHONY: check-deps
check-deps:
	@echo "$(CYAN)🔍 Checking dependencies...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)❌ Docker not installed$(NC)"; exit 1; }
	@command -v docker compose >/dev/null 2>&1 || { echo "$(RED)❌ Docker Compose not installed$(NC)"; exit 1; }
	@echo "$(GREEN)✅ Docker: $(shell docker --version)$(NC)"
	@echo "$(GREEN)✅ Docker Compose: $(shell docker compose version)$(NC)"

# Shortcuts for common operations
.PHONY: start stop restart-mid dev prod
start: up
stop: down
restart-mid: restart-middleware
dev: fresh logs
prod: check-deps up

# File watchers and development helpers
.PHONY: watch-logs
watch-logs:
	@echo "$(CYAN)👀 Watching logs with auto-refresh...$(NC)"
	@while true; do \
		clear; \
		echo "$(CYAN)=== Logs ($(shell date)) ===$(NC)"; \
		$(DOCKER_COMPOSE) logs --tail=50; \
		sleep 5; \
	done

# Validation targets
.PHONY: validate-compose
validate-compose:
	@echo "$(CYAN)🔍 Validating Docker Compose configuration...$(NC)"
	$(DOCKER_COMPOSE) config --quiet && echo "$(GREEN)✅ Compose file is valid$(NC)" || echo "$(RED)❌ Compose file has errors$(NC)"

# Quick development cycle
.PHONY: quick-restart
quick-restart:
	@echo "$(BLUE)⚡ Quick restart for development...$(NC)"
	$(DOCKER_COMPOSE) restart middleware
	@sleep 2
	@echo "$(GREEN)✅ Ready for testing$(NC)"