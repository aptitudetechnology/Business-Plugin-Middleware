# BigCapital Self-Hosted Setup (Pre-built Image)
# Makefile for managing BigCapital deployment using official Docker image

.PHONY: help up down logs status clean init backup restore

# Default target
help: ## Show this help message
	@echo "BigCapital Self-Hosted Management (Pre-built Image)"
	@echo "=================================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔌 Port mappings (to avoid conflicts with main middleware):"
	@echo "   BigCapital Web:  3000 -> 3000"
	@echo "   MariaDB:         3307 -> 3306 (external -> internal)"
	@echo "   MongoDB:         27018 -> 27017 (external -> internal)"
	@echo "   Redis:           6380 -> 6379 (external -> internal)"
	@echo ""
	@echo "⚡ Using pre-built image: bigcapitalhq/server:latest"
	@echo "⚠️  Resource Requirements:"
	@echo "   - RAM: 2GB+ recommended"
	@echo "   - Storage: 10GB+ for data"
	@echo "   - CPU: 2+ cores recommended"

up: ## Start BigCapital and all dependencies
	@echo "🚀 Starting BigCapital services..."
	@echo "🔧 Ensuring paperless_network exists..."
	@docker network create paperless_network 2>/dev/null || echo "✓ paperless_network already exists"
	@echo "🔍 Validating docker-compose.yml..."
	@docker-compose config -q || (echo "❌ docker-compose.yml has errors - run 'make validate-compose' for details" && exit 1)
	@echo "⚡ Using pre-built image - startup should be fast!"
	@docker-compose up -d
	@echo "✅ BigCapital is starting up"
	@echo "📱 Web UI will be available at: http://simple.local:3000"
	@echo "⏳ Services should be ready in 2-3 minutes..."

down: ## Stop BigCapital services
	@echo "🛑 Stopping BigCapital services..."
	@docker-compose down
	@echo "✅ BigCapital services stopped"

logs: ## Show BigCapital application logs
	@docker-compose logs -f bigcapital

logs-all: ## Show logs for all BigCapital services
	@docker-compose logs -f

logs-db: ## Show database logs
	@docker-compose logs -f bigcapital-mariadb

logs-mongo: ## Show MongoDB logs
	@docker-compose logs -f bigcapital-mongo

logs-redis: ## Show Redis logs
	@docker-compose logs -f bigcapital-redis

status: ## Show status of all BigCapital services
	@echo "📊 BigCapital Services Status:"
	@docker-compose ps

init: ## Initialize BigCapital with default configuration
	@echo "🔧 Initializing BigCapital..."
	@echo "⚡ Using pre-built image - this will be fast!"
	@$(MAKE) up
	@echo "⏳ Waiting for services to be ready..."
	@sleep 45
	@echo "🌐 BigCapital should now be available at: http://simple.local:3000"
	@echo ""
	@echo "📋 Setup Instructions:"
	@echo "   1. Open http://simple.local:3000 in your browser"
	@echo "   2. Follow the initial setup wizard"
	@echo "   3. Create your admin account"
	@echo ""
	@echo "⚠️  IMPORTANT: Use strong passwords and keep them secure!"

clean: ## Remove all BigCapital containers and networks (keeps data)
	@echo "🧹 Cleaning up BigCapital containers..."
	@docker-compose down --remove-orphans
	@docker-compose rm -f
	@echo "✅ Cleanup complete (data volumes preserved)"

clean-all: ## Remove containers, networks, and ALL DATA (destructive!)
	@echo "⚠️  WARNING: This will delete ALL BigCapital data!"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	@docker-compose down -v --remove-orphans
	@docker-compose rm -f
	@echo "💥 All BigCapital data has been removed"

backup: ## Create backup of BigCapital data
	@echo "💾 Creating BigCapital backup..."
	@mkdir -p ./backups
	@echo "📊 Backing up MariaDB..."
	@docker-compose exec -T bigcapital-mariadb mysqldump -u bigcapital -pbigcapital_secure_password bigcapital > ./backups/bigcapital-mysql-$$(date +%Y%m%d_%H%M%S).sql
	@echo "📊 Backing up MongoDB..."
	@docker-compose exec -T bigcapital-mongo mongodump --uri="mongodb://localhost:27017/bigcapital" --archive > ./backups/bigcapital-mongo-$$(date +%Y%m%d_%H%M%S).archive
	@echo "✅ Backup created in ./backups/"

restore-mysql: ## Restore MySQL backup (usage: make restore-mysql BACKUP_FILE=backup.sql)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Usage: make restore-mysql BACKUP_FILE=backup.sql"; exit 1; fi
	@echo "📥 Restoring MySQL backup: $(BACKUP_FILE)"
	@docker-compose exec -T bigcapital-mariadb mysql -u bigcapital -pbigcapital_secure_password bigcapital < $(BACKUP_FILE)
	@echo "✅ MySQL backup restored"

restore-mongo: ## Restore MongoDB backup (usage: make restore-mongo BACKUP_FILE=backup.archive)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Usage: make restore-mongo BACKUP_FILE=backup.archive"; exit 1; fi
	@echo "📥 Restoring MongoDB backup: $(BACKUP_FILE)"
	@docker-compose exec -T bigcapital-mongo mongorestore --uri="mongodb://localhost:27017/bigcapital" --archive < $(BACKUP_FILE)
	@echo "✅ MongoDB backup restored"

restart: ## Restart BigCapital services
	@echo "🔄 Restarting BigCapital services..."
	@docker-compose restart
	@echo "✅ BigCapital services restarted"

restart-app: ## Restart only BigCapital application
	@echo "🔄 Restarting BigCapital application..."
	@docker-compose restart bigcapital
	@echo "✅ BigCapital application restarted"

update: ## Update BigCapital to latest version
	@echo "🔄 Updating BigCapital..."
	@docker-compose pull bigcapital
	@docker-compose up -d bigcapital
	@echo "✅ BigCapital updated to latest version"

update-all: ## Update all images to latest versions
	@echo "🔄 Updating all BigCapital images..."
	@docker-compose pull
	@docker-compose up -d
	@echo "✅ All BigCapital services updated"

shell: ## Open shell in BigCapital container
	@docker-compose exec bigcapital /bin/bash

shell-root: ## Open root shell in BigCapital container
	@docker-compose exec -u root bigcapital /bin/bash

db-shell: ## Open MySQL shell
	@docker-compose exec bigcapital-mariadb mysql -u bigcapital -pbigcapital_secure_password bigcapital

db-shell-root: ## Open MySQL root shell
	@docker-compose exec bigcapital-mariadb mysql -u root -pbigcapital_root_password_change_me

mongo-shell: ## Open MongoDB shell
	@docker-compose exec bigcapital-mongo mongosh mongodb://localhost:27017/bigcapital

redis-shell: ## Open Redis shell
	@docker-compose exec bigcapital-redis redis-cli -a bigcapital_redis_password

config: ## Show current configuration
	@echo "📋 BigCapital Configuration:"
	@echo "  Web UI: http://simple.local:3000"
	@echo "  MySQL: simple.local:3307"
	@echo "  MongoDB: simple.local:27018"
	@echo "  Redis: simple.local:6380"
	@echo ""
	@echo "🔧 Container Status:"
	@$(MAKE) status

dev: ## Start with live logs for development
	@echo "🔧 Starting BigCapital in development mode..."
	@docker-compose up

# Health checks
health: ## Check health of all BigCapital services
	@echo "🔍 Checking BigCapital health..."
	@echo "📊 BigCapital App:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|301\|302" && echo "✅ BigCapital responding" || echo "❌ BigCapital not responding"
	@echo ""
	@echo "📊 MySQL:"
	@docker-compose exec bigcapital-mariadb mysqladmin ping -u bigcapital -pbigcapital_secure_password >/dev/null 2>&1 && echo "✅ MySQL healthy" || echo "❌ MySQL not responding"
	@echo ""
	@echo "📊 MongoDB:"
	@docker-compose exec bigcapital-mongo mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1 && echo "✅ MongoDB healthy" || echo "❌ MongoDB not responding"
	@echo ""
	@echo "📊 Redis:"
	@docker-compose exec bigcapital-redis redis-cli -a bigcapital_redis_password ping >/dev/null 2>&1 && echo "✅ Redis healthy" || echo "❌ Redis not responding"

wait-ready: ## Wait for all services to be ready
	@echo "⏳ Waiting for BigCapital services to be ready..."
	@echo "📊 Checking MariaDB..."
	@until docker-compose exec bigcapital-mariadb mysqladmin ping -u bigcapital -pbigcapital_secure_password >/dev/null 2>&1; do sleep 2; done
	@echo "✅ MariaDB is ready"
	@echo "📊 Checking MongoDB..."
	@until docker-compose exec bigcapital-mongo mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; do sleep 2; done
	@echo "✅ MongoDB is ready"
	@echo "📊 Checking Redis..."
	@until docker-compose exec bigcapital-redis redis-cli -a bigcapital_redis_password ping >/dev/null 2>&1; do sleep 2; done
	@echo "✅ Redis is ready"
	@echo "📊 Checking BigCapital app..."
	@until curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|301\|302"; do sleep 5; done
	@echo "✅ BigCapital is ready!"
	@echo "🌐 Access BigCapital at: http://simple.local:3000"

# Quick setup for first-time users
quick-start: ## Quick start - pull images and start services
	@echo "🚀 BigCapital Quick Start"
	@echo "========================"
	@echo "📥 Pulling latest images..."
	@docker-compose pull
	@echo "🔧 Starting services..."
	@$(MAKE) up
	@echo "⏳ Waiting for services to be ready..."
	@$(MAKE) wait-ready
	@echo ""
	@echo "🎉 BigCapital is ready!"
	@echo "🌐 Open: http://simple.local:3000"

# Maintenance commands
prune: ## Remove unused Docker resources
	@echo "🧹 Cleaning up unused Docker resources..."
	@docker system prune -f
	@echo "✅ Docker cleanup complete"

reset: ## Stop, clean, and restart BigCapital
	@echo "🔄 Resetting BigCapital..."
	@$(MAKE) down
	@$(MAKE) clean
	@$(MAKE) up
	@echo "✅ BigCapital reset complete"

# Monitoring
monitor: ## Show real-time resource usage
	@echo "📊 BigCapital Resource Monitor"
	@echo "============================="
	@docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" bigcapital bigcapital-mariadb bigcapital-mongo bigcapital-redis

# Integration with main middleware
integrate: ## Instructions for integrating with main docker-compose.yml
	@echo "🔗 Integrating BigCapital with main middleware..."
	@echo "📝 Manual integration steps:"
	@echo ""
	@echo "1. Copy BigCapital services to your main docker-compose.yml"
	@echo "2. Ensure 'paperless_network' is available"
	@echo "3. Update middleware dependencies if needed"
	@echo "4. Run: docker-compose up -d"
	@echo ""
	@echo "💡 BigCapital will be available at: http://simple.local:3000"

# Troubleshooting
troubleshoot: ## Run troubleshooting checks
	@echo "🔍 BigCapital Troubleshooting"
	@echo "============================"
	@echo ""
	@echo "📊 Service Status:"
	@$(MAKE) status
	@echo ""
	@echo "🔍 Health Check:"
	@$(MAKE) health
	@echo ""
	@echo "📋 Common Issues:"
	@echo "  - Port conflicts: Check if ports 3000, 3307, 27018, 6380 are available"
	@echo "  - Network issues: Ensure 'paperless_network' exists"
	@echo "  - Resource limits: Check available RAM and disk space"
	@echo ""
	@echo "🔧 Quick fixes:"
	@echo "  - Restart services: make restart"
	@echo "  - Clean restart: make reset"
	@echo "  - Check logs: make logs"

# Environment validation
validate-env: ## Validate environment and prerequisites
	@echo "🔍 Validating BigCapital environment..."
	@echo "📊 Docker version:"
	@docker --version
	@echo "📊 Docker Compose version:"
	@docker-compose --version
	@echo "📊 Available disk space:"
	@df -h . | tail -n 1
	@echo "📊 Available memory:"
	@free -h | grep Mem
	@echo "📊 Port availability:"
	@netstat -tuln | grep -E ":3000|:3307|:27018|:6380" || echo "✅ Required ports appear to be available"
	@echo "✅ Environment validation complete"

validate-compose: ## Validate docker-compose.yml configuration
	@echo "🔍 Validating docker-compose.yml..."
	@docker-compose config || echo "❌ docker-compose.yml has configuration errors"
	@echo "🔍 Checking volume declarations..."
	@docker-compose config --volumes || echo "❌ Volume configuration issues found"

fix-compose: ## Fix common docker-compose.yml issues
	@echo "🔧 Checking for missing volume declarations..."
	@echo "📋 Your docker-compose.yml should include these volumes:"
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
	@echo "💡 Add the missing 'bigcapital_redis:' volume declaration to your docker-compose.yml"