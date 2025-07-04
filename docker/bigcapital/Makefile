# BigCapital Self-Hosted Setup (Pre-built Image)
# Makefile for managing BigCapital deployment using official Docker image

# Configuration
COMPOSE_FILE := docker-compose.yml
COMPOSE_PROJECT_NAME := bigcapital
NETWORK_NAME := paperless_network
BACKUP_DIR := ./backups
WEB_URL := http://simple.local:3000

# Database credentials
DB_USER := bigcapital
DB_PASSWORD := bigcapital_secure_password
DB_NAME := bigcapital
DB_ROOT_PASSWORD := bigcapital_root_password_change_me
REDIS_PASSWORD := bigcapital_redis_password

# Port mappings
WEB_PORT := 3000
MYSQL_PORT := 3307
MONGO_PORT := 27018
REDIS_PORT := 6380

.PHONY: help up down logs status clean init backup restore

# Default target
help: ## Show this help message
	@echo "BigCapital Self-Hosted Management (Pre-built Image)"
	@echo "=================================================="
	@echo ""
	@echo "🚀 Quick Start Commands:"
	@echo "  make quick-start    - Pull images and start everything"
	@echo "  make init          - Initialize with setup wizard"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo ""
	@echo "📋 Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔌 Port Mappings:"
	@echo "   BigCapital Web:  $(WEB_PORT) -> 3000"
	@echo "   MariaDB:         $(MYSQL_PORT) -> 3306"
	@echo "   MongoDB:         $(MONGO_PORT) -> 27017"
	@echo "   Redis:           $(REDIS_PORT) -> 6379"
	@echo ""
	@echo "🌐 Access URL: $(WEB_URL)"
	@echo "⚡ Using pre-built image: bigcapitalhq/server:latest"
	@echo "⚠️  Resource Requirements: 2GB+ RAM, 10GB+ storage, 2+ CPU cores"

# Core service management
up: ## Start BigCapital and all dependencies
	@echo "🚀 Starting BigCapital services..."
	@$(MAKE) -s _ensure_network
	@$(MAKE) -s _validate_compose
	@echo "⚡ Using pre-built image - startup should be fast!"
	@docker compose up -d
	@echo "✅ BigCapital is starting up"
	@echo "📱 Web UI will be available at: $(WEB_URL)"
	@echo "⏳ Services should be ready in 2-3 minutes..."

down: ## Stop BigCapital services
	@echo "🛑 Stopping BigCapital services..."
	@docker compose down
	@echo "✅ BigCapital services stopped"

restart: ## Restart BigCapital services
	@echo "🔄 Restarting BigCapital services..."
	@docker compose restart
	@echo "✅ BigCapital services restarted"

restart-app: ## Restart only BigCapital application
	@echo "🔄 Restarting BigCapital application..."
	@docker compose restart bigcapital
	@echo "✅ BigCapital application restarted"

status: ## Show status of all BigCapital services
	@echo "📊 BigCapital Services Status:"
	@docker compose ps

# Logging
logs: ## Show BigCapital application logs
	@docker compose logs -f bigcapital

logs-all: ## Show logs for all services
	@docker compose logs -f

logs-db: ## Show MariaDB logs
	@docker compose logs -f bigcapital-mariadb

logs-mongo: ## Show MongoDB logs
	@docker compose logs -f bigcapital-mongo

logs-redis: ## Show Redis logs
	@docker compose logs -f bigcapital-redis

# Development and debugging
dev: ## Start with live logs for development
	@echo "🔧 Starting BigCapital in development mode..."
	@docker compose up

shell: ## Open shell in BigCapital container
	@docker compose exec bigcapital /bin/bash

shell-root: ## Open root shell in BigCapital container
	@docker compose exec -u root bigcapital /bin/bash

db-shell: ## Open MySQL shell
	@docker compose exec bigcapital-mariadb mysql -u $(DB_USER) -p$(DB_PASSWORD) $(DB_NAME)

db-shell-root: ## Open MySQL root shell
	@docker compose exec bigcapital-mariadb mysql -u root -p$(DB_ROOT_PASSWORD)

mongo-shell: ## Open MongoDB shell
	@docker compose exec bigcapital-mongo mongosh mongodb://localhost:27017/$(DB_NAME)

redis-shell: ## Open Redis shell
	@docker compose exec bigcapital-redis redis-cli -a $(REDIS_PASSWORD)

# Initialization and setup
init: ## Initialize BigCapital with default configuration
	@echo "🔧 Initializing BigCapital..."
	@echo "⚡ Using pre-built image - this will be fast!"
	@$(MAKE) up
	@echo "⏳ Waiting for services to be ready..."
	@sleep 45
	@echo "🌐 BigCapital should now be available at: $(WEB_URL)"
	@echo ""
	@echo "📋 Setup Instructions:"
	@echo "   1. Open $(WEB_URL) in your browser"
	@echo "   2. Follow the initial setup wizard"
	@echo "   3. Create your admin account"
	@echo ""
	@echo "⚠️  IMPORTANT: Use strong passwords and keep them secure!"

quick-start: ## Quick start - pull images and start services
	@echo "🚀 BigCapital Quick Start"
	@echo "========================"
	@echo "📥 Pulling latest images..."
	@docker compose pull
	@echo "🔧 Starting services..."
	@$(MAKE) up
	@echo "⏳ Waiting for services to be ready..."
	@$(MAKE) wait-ready
	@echo ""
	@echo "🎉 BigCapital is ready!"
	@echo "🌐 Open: $(WEB_URL)"

# Updates
update: ## Update BigCapital to latest version
	@echo "🔄 Updating BigCapital..."
	@docker compose pull bigcapital
	@docker compose up -d bigcapital
	@echo "✅ BigCapital updated to latest version"

update-all: ## Update all images to latest versions
	@echo "🔄 Updating all BigCapital images..."
	@docker compose pull
	@docker compose up -d
	@echo "✅ All BigCapital services updated"

# Cleanup
clean: ## Remove containers and networks (keeps data)
	@echo "🧹 Cleaning up BigCapital containers..."
	@docker compose down --remove-orphans
	@docker compose rm -f
	@echo "✅ Cleanup complete (data volumes preserved)"

clean-all: ## Remove containers, networks, and ALL DATA (destructive!)
	@echo "⚠️  WARNING: This will delete ALL BigCapital data!"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	@docker compose down -v --remove-orphans
	@docker compose rm -f
	@echo "💥 All BigCapital data has been removed"

reset: ## Stop, clean, and restart BigCapital
	@echo "🔄 Resetting BigCapital..."
	@$(MAKE) down
	@$(MAKE) clean
	@$(MAKE) up
	@echo "✅ BigCapital reset complete"

prune: ## Remove unused Docker resources
	@echo "🧹 Cleaning up unused Docker resources..."
	@docker system prune -f
	@echo "✅ Docker cleanup complete"

# Backup and restore
backup: ## Create backup of BigCapital data
	@echo "💾 Creating BigCapital backup..."
	@mkdir -p $(BACKUP_DIR)
	@echo "📊 Backing up MariaDB..."
	@docker compose exec -T bigcapital-mariadb mysqldump -u $(DB_USER) -p$(DB_PASSWORD) $(DB_NAME) > $(BACKUP_DIR)/bigcapital-mysql-$$(date +%Y%m%d_%H%M%S).sql
	@echo "📊 Backing up MongoDB..."
	@docker compose exec -T bigcapital-mongo mongodump --uri="mongodb://localhost:27017/$(DB_NAME)" --archive > $(BACKUP_DIR)/bigcapital-mongo-$$(date +%Y%m%d_%H%M%S).archive
	@echo "✅ Backup created in $(BACKUP_DIR)/"

restore-mysql: ## Restore MySQL backup (usage: make restore-mysql BACKUP_FILE=backup.sql)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Usage: make restore-mysql BACKUP_FILE=backup.sql"; exit 1; fi
	@echo "📥 Restoring MySQL backup: $(BACKUP_FILE)"
	@docker compose exec -T bigcapital-mariadb mysql -u $(DB_USER) -p$(DB_PASSWORD) $(DB_NAME) < $(BACKUP_FILE)
	@echo "✅ MySQL backup restored"

restore-mongo: ## Restore MongoDB backup (usage: make restore-mongo BACKUP_FILE=backup.archive)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Usage: make restore-mongo BACKUP_FILE=backup.archive"; exit 1; fi
	@echo "📥 Restoring MongoDB backup: $(BACKUP_FILE)"
	@docker compose exec -T bigcapital-mongo mongorestore --uri="mongodb://localhost:27017/$(DB_NAME)" --archive < $(BACKUP_FILE)
	@echo "✅ MongoDB backup restored"

# Health checks and monitoring
health: ## Check health of all BigCapital services
	@echo "🔍 Checking BigCapital health..."
	@$(MAKE) -s _check_web_health
	@$(MAKE) -s _check_mysql_health
	@$(MAKE) -s _check_mongo_health
	@$(MAKE) -s _check_redis_health

wait-ready: ## Wait for all services to be ready
	@echo "⏳ Waiting for BigCapital services to be ready..."
	@$(MAKE) -s _wait_mysql
	@$(MAKE) -s _wait_mongo
	@$(MAKE) -s _wait_redis
	@$(MAKE) -s _wait_web
	@echo "✅ BigCapital is ready!"
	@echo "🌐 Access BigCapital at: $(WEB_URL)"

monitor: ## Show real-time resource usage
	@echo "📊 BigCapital Resource Monitor"
	@echo "============================="
	@docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" bigcapital bigcapital-mariadb bigcapital-mongo bigcapital-redis

# Configuration and validation
config: ## Show current configuration
	@echo "📋 BigCapital Configuration:"
	@echo "  Web UI: $(WEB_URL)"
	@echo "  MySQL: simple.local:$(MYSQL_PORT)"
	@echo "  MongoDB: simple.local:$(MONGO_PORT)"
	@echo "  Redis: simple.local:$(REDIS_PORT)"
	@echo ""
	@echo "🔧 Container Status:"
	@$(MAKE) status

validate-env: ## Validate environment and prerequisites
	@echo "🔍 Validating BigCapital environment..."
	@echo "📊 Docker version:"
	@docker --version
	@echo "📊 Docker Compose version:"
	@docker compose version
	@echo "📊 Available disk space:"
	@df -h . | tail -n 1
	@echo "📊 Available memory:"
	@free -h 2>/dev/null | grep Mem || echo "Memory info not available"
	@echo "📊 Port availability:"
	@netstat -tuln 2>/dev/null | grep -E ":$(WEB_PORT)|:$(MYSQL_PORT)|:$(MONGO_PORT)|:$(REDIS_PORT)" || echo "✅ Required ports appear to be available"
	@echo "✅ Environment validation complete"

validate-compose: ## Validate docker-compose.yml configuration
	@echo "🔍 Validating docker-compose.yml..."
	@docker compose config -q || echo "❌ docker-compose.yml has configuration errors"
	@echo "🔍 Checking volume declarations..."
	@docker compose config --volumes 2>/dev/null || echo "❌ Volume configuration issues found"

# Troubleshooting
troubleshoot: ## Run comprehensive troubleshooting checks
	@echo "🔍 BigCapital Troubleshooting"
	@echo "============================"
	@echo ""
	@echo "📊 Service Status:"
	@$(MAKE) status
	@echo ""
	@echo "🔍 Health Check:"
	@$(MAKE) health
	@echo ""
	@echo "📋 MongoDB Connection Check:"
	@$(MAKE) test-mongo
	@echo ""
	@echo "📋 Common Issues & Solutions:"
	@echo "  - MongoDB connection errors: make fix-mongo"
	@echo "  - Port conflicts: Check ports $(WEB_PORT), $(MYSQL_PORT), $(MONGO_PORT), $(REDIS_PORT)"
	@echo "  - Network issues: make _ensure_network"
	@echo "  - Resource limits: make validate-env"
	@echo ""
	@echo "🔧 Quick fixes:"
	@echo "  - Restart services: make restart"
	@echo "  - Clean restart: make reset"
	@echo "  - Check logs: make logs"
	@echo "  - Debug MongoDB: make debug-mongo"

test-mongo: ## Test MongoDB connection comprehensively
	@echo "🔍 Testing MongoDB connection..."
	@echo "📊 MongoDB container status:"
	@docker compose ps bigcapital-mongo
	@echo ""
	@echo "📊 Testing MongoDB internal connection:"
	@docker compose exec bigcapital-mongo mongosh --eval "db.runCommand('ping')" --quiet 2>/dev/null && echo "✅ MongoDB internal connection OK" || echo "❌ MongoDB internal connection failed"
	@echo ""
	@echo "📊 Testing network connectivity:"
	@docker compose exec bigcapital nc -zv bigcapital-mongo 27017 2>/dev/null && echo "✅ Network connectivity OK" || echo "❌ Network connectivity failed"
	@echo ""
	@echo "📊 MongoDB environment variables:"
	@docker compose exec bigcapital printenv | grep -i mongo || echo "❌ No MongoDB environment variables found"

fix-mongo: ## Fix MongoDB connection issues
	@echo "🔧 MongoDB Connection Fix Guide"
	@echo "=============================="
	@echo ""
	@echo "💡 Recommended MongoDB URI configurations:"
	@echo ""
	@echo "1. Simple connection (recommended):"
	@echo "   MONGODB_URI=mongodb://bigcapital-mongo:27017/$(DB_NAME)"
	@echo ""
	@echo "2. With authentication:"
	@echo "   MONGODB_URI=mongodb://admin:password@bigcapital-mongo:27017/$(DB_NAME)?authSource=admin"
	@echo ""
	@echo "🔧 Add these to your BigCapital service environment in docker-compose.yml"
	@echo "🔄 Then run: make restart"

debug-mongo: ## Debug MongoDB connection in detail
	@echo "🔍 MongoDB Debug Information"
	@echo "==========================="
	@echo ""
	@echo "📊 Environment Variables:"
	@docker compose exec bigcapital printenv | grep -E "MONGO|DATABASE" || echo "❌ No MongoDB environment variables"
	@echo ""
	@echo "📊 MongoDB Container Logs (last 20 lines):"
	@docker compose logs --tail 20 bigcapital-mongo
	@echo ""
	@echo "📊 BigCapital MongoDB-related Logs:"
	@docker compose logs bigcapital | grep -i mongo | tail -10 || echo "❌ No MongoDB logs found"
	@echo ""
	@echo "📊 Network Connectivity:"
	@docker compose exec bigcapital ping -c 3 bigcapital-mongo 2>/dev/null || echo "❌ Cannot ping MongoDB container"

# Integration helpers
integrate: ## Show integration instructions
	@echo "🔗 BigCapital Integration Guide"
	@echo "==============================="
	@echo ""
	@echo "To integrate with existing docker-compose setup:"
	@echo "1. Ensure network '$(NETWORK_NAME)' exists"
	@echo "2. Copy BigCapital services to main docker-compose.yml"
	@echo "3. Update port mappings if needed"
	@echo "4. Run: docker compose up -d"
	@echo ""
	@echo "💡 BigCapital will be available at: $(WEB_URL)"

# Internal helper functions (prefixed with _)
_ensure_network:
	@echo "🔧 Ensuring $(NETWORK_NAME) exists..."
	@docker network create $(NETWORK_NAME) 2>/dev/null || echo "✓ $(NETWORK_NAME) already exists"

_validate_compose:
	@echo "🔍 Validating docker-compose.yml..."
	@docker compose config -q || (echo "❌ docker-compose.yml has errors - run 'make validate-compose' for details" && exit 1)

_check_web_health:
	@echo "📊 BigCapital App:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:$(WEB_PORT) 2>/dev/null | grep -q "200\|301\|302" && echo "✅ BigCapital responding" || echo "❌ BigCapital not responding"

_check_mysql_health:
	@echo "📊 MySQL:"
	@docker compose exec bigcapital-mariadb mysqladmin ping -u $(DB_USER) -p$(DB_PASSWORD) >/dev/null 2>&1 && echo "✅ MySQL healthy" || echo "❌ MySQL not responding"

_check_mongo_health:
	@echo "📊 MongoDB:"
	@docker compose exec bigcapital-mongo mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1 && echo "✅ MongoDB healthy" || echo "❌ MongoDB not responding"

_check_redis_health:
	@echo "📊 Redis:"
	@docker compose exec bigcapital-redis redis-cli -a $(REDIS_PASSWORD) ping >/dev/null 2>&1 && echo "✅ Redis healthy" || echo "❌ Redis not responding"

_wait_mysql:
	@echo "📊 Waiting for MariaDB..."
	@until docker compose exec bigcapital-mariadb mysqladmin ping -u $(DB_USER) -p$(DB_PASSWORD) >/dev/null 2>&1; do sleep 2; done
	@echo "✅ MariaDB is ready"

_wait_mongo:
	@echo "📊 Waiting for MongoDB..."
	@until docker compose exec bigcapital-mongo mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; do sleep 2; done
	@echo "✅ MongoDB is ready"

_wait_redis:
	@echo "📊 Waiting for Redis..."
	@until docker compose exec bigcapital-redis redis-cli -a $(REDIS_PASSWORD) ping >/dev/null 2>&1; do sleep 2; done
	@echo "✅ Redis is ready"

_wait_web:
	@echo "📊 Waiting for BigCapital app..."
	@until curl -s -o /dev/null -w "%{http_code}" http://localhost:$(WEB_PORT) 2>/dev/null | grep -q "200\|301\|302"; do sleep 5; done
	@echo "✅ BigCapital is ready!"

# Legacy commands (for backward compatibility)
fix-compose: ## Show volume configuration help
	@echo "🔧 Common docker-compose.yml Volume Configuration"
	@echo "================================================"
	@echo ""
	@echo "Ensure your docker-compose.yml includes these volumes:"
	@echo "volumes:"
	@echo "  bigcapital_mariadb:"
	@echo "    driver: local"
	@echo "  bigcapital_mongo:"
	@echo "    driver: local"
	@echo "  bigcapital_redis:"
	@echo "    driver: local"
	@echo "  bigcapital_uploads:"
	@echo "    driver: local"
	@echo "  bigcapital_storage:"
	@echo "    driver: local"
	@echo "  bigcapital_logs:"
	@echo "    driver: local"
	@echo ""
	@echo "💡 All volumes should be declared at the bottom of your docker-compose.yml"