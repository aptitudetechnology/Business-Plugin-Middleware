#!/bin/bash
# BigCapital Health Check Script

set -e

echo "🔍 BigCapital Health Check"
echo "=========================="

# Function to check if a service is healthy
check_service() {
    local service_name=$1
    local check_command=$2

    echo -n "Checking $service_name... "

    if eval "$check_command" &>/dev/null; then
        echo "✅ Healthy"
        return 0
    else
        echo "❌ Unhealthy"
        return 1
    fi
}

# Function to validate MongoDB URI format
validate_mongo_uri() {
    local uri=$1

    echo -n "Validating MongoDB URI... "
    
    if [[ $uri =~ ^mongodb(\+srv)?:\/\/[^:]+:[^@]+@[^\/]+\/[^?]+(\?.*)?$ ]]; then
        echo "✅ Format looks valid"
    else
        echo "❌ Invalid format"
        echo "   Example format: mongodb://user:pass@host:27017/dbname?options"
        return 1
    fi
}

# Load environment file if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check BigCapital App
check_service "BigCapital App" "curl -s http://localhost:3000/health"

# Check MariaDB
check_service "MariaDB" "mysqladmin ping -h bigcapital-mariadb -u bigcapital -pbigcapital_secure_password"

# Validate Mongo URI (if provided)
if [ -n "$MONGO_URI" ]; then
    validate_mongo_uri "$MONGO_URI"
else
    echo "⚠️  Skipping Mongo URI validation: MONGO_URI not set"
fi

# Check MongoDB using Docker exec
check_service "MongoDB" "docker compose exec -T bigcapital-mongo mongosh --eval 'db.runCommand({ ping: 1 })' --quiet"

# Check Redis
check_service "Redis" "docker compose exec -T bigcapital-redis redis-cli ping | grep -q PONG"

echo ""
echo "📊 Container Status:"
docker compose ps

echo ""
echo "💾 Volume Usage:"
docker system df

echo ""
echo "🌐 BigCapital should be available at: http://simple.local:3000"
