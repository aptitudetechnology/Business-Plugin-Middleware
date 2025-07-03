# BigCapital Self-Hosted Setup
# Makefile for managing BigCapital deployment

.PHONY: help up down logs status clean init backup restore

# Default target
help: ## Show this help message
	@echo "BigCapital Self-Hosted Management"
	@echo "================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "⚠️  Resource Requirements:"
	@echo "   - RAM: 4GB+ recommended"
	@echo "   - Storage: 10GB+ for data"
	@echo "   - CPU: 2+ cores recommended"

up: ## Start BigCapital and all dependencies
	@echo "🚀 Starting BigCapital services..."
	@docker-compose up -d
	@echo "✅ BigCapital is starting up"
	@echo "📱 Web UI will be available at: http://simple.local:3000"
	@echo "⏳ Initial startup may take 2-3 minutes..."

down: ## Stop BigCapital services
	@echo "🛑 Stopping BigCapital services..."
	@docker-compose down
	@echo "✅ BigCapital services stopped"

logs: ## Show BigCapital application logs
	@docker-compose logs -f bigcapital

logs-all: ## Show logs for all BigCapital services
	@docker-compose logs -f

status: ## Show status of all BigCapital services
	@echo "📊 BigCapital Services Status:"
	@docker-compose ps

init: ## Initialize BigCapital with default configuration
	@echo "🔧 Initializing BigCapital..."
	@$(MAKE) up
	@echo "⏳ Waiting for services to be ready..."
	@sleep 30
	@echo "🌐 BigCapital should now be available at: http://simple.local:3000"
	@echo "📋 Default admin credentials:"
	@echo "   Email: admin@bigcapital.com"
	@echo "   Password: admin123"
	@echo ""
	@echo "⚠️  IMPORTANT: Change default credentials after first login!"

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
	@docker-compose exec bigcapital-mariadb mysqldump -u bigcapital -pbigcapital_secure_password bigcapital > ./backups/bigcapital-mysql-$$(date +%Y%m%d_%H%M%S).sql
	@docker-compose exec bigcapital-mongo mongodump --uri="mongodb://bigcapital:bigcapital_mongo_password@localhost:27017/bigcapital" --out=/tmp/backup
	@docker cp bigcapital-mongo:/tmp/backup ./backups/bigcapital-mongo-$$(date +%Y%m%d_%H%M%S)
	@echo "✅ Backup created in ./backups/"

restart: ## Restart BigCapital services
	@echo "🔄 Restarting BigCapital services..."
	@docker-compose restart
	@echo "✅ BigCapital services restarted"

update: ## Update BigCapital to latest version
	@echo "🔄 Updating BigCapital..."
	@docker-compose pull
	@docker-compose up -d
	@echo "✅ BigCapital updated"

shell: ## Open shell in BigCapital container
	@docker-compose exec bigcapital /bin/bash

db-shell: ## Open MySQL shell
	@docker-compose exec bigcapital-mariadb mysql -u bigcapital -pbigcapital_secure_password bigcapital

mongo-shell: ## Open MongoDB shell
	@docker-compose exec bigcapital-mongo mongosh mongodb://bigcapital:bigcapital_mongo_password@localhost:27017/bigcapital

config: ## Show current configuration
	@echo "📋 BigCapital Configuration:"
	@echo "  Web UI: http://simple.local:3000"
	@echo "  MySQL: simple.local:3306"
	@echo "  MongoDB: simple.local:27017"
	@echo "  Redis: simple.local:6379"
	@echo ""
	@echo "🔧 Container Status:"
	@$(MAKE) status

dev: ## Start in development mode with live logs
	@echo "🔧 Starting BigCapital in development mode..."
	@docker-compose up --build

# Integration with main middleware
integrate: ## Add BigCapital to main docker-compose.yml
	@echo "🔗 Integrating BigCapital with main middleware..."
	@echo "📝 Adding BigCapital services to ../docker-compose.yml"
	@echo ""
	@echo "💡 Manual step required:"
	@echo "   1. Copy the BigCapital services from docker-compose.yml to ../docker-compose.yml"
	@echo "   2. Uncomment the BigCapital sections"
	@echo "   3. Update middleware dependency: depends_on: [paperless-ngx, bigcapital]"
	@echo "   4. Run: cd .. && docker-compose up -d"

# Health checks
health: ## Check health of all BigCapital services
	@echo "🔍 Checking BigCapital health..."
	@echo "📊 BigCapital App:"
	@curl -s http://localhost:3000/health || echo "❌ BigCapital not responding"
	@echo ""
	@echo "📊 MySQL:"
	@docker-compose exec bigcapital-mariadb mysqladmin ping -u root -pbigcapital_root_password_change_me || echo "❌ MySQL not responding"
	@echo ""
	@echo "📊 MongoDB:"
	@docker-compose exec bigcapital-mongo mongosh --eval "db.runCommand('ping')" || echo "❌ MongoDB not responding"
	@echo ""
	@echo "📊 Redis:"
	@docker-compose exec bigcapital-redis redis-cli ping || echo "❌ Redis not responding"
