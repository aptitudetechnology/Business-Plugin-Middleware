#!/bin/bash
# BigCapital Health Check Script

set -e

echo "🔍 BigCapital Health Check"
echo "========================="

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

# Check BigCapital application
check_service "BigCapital App" "curl -s http://localhost:3000/health"

# Check MariaDB
check_service "MariaDB" "mysqladmin ping -h bigcapital-mariadb -u bigcapital -pbigcapital_secure_password"

# Check MongoDB
check_service "MongoDB" "docker compose exec -T bigcapital-mongo mongosh --eval 'db.runCommand(\"ping\")' --quiet"

# Check Redis
check_service "Redis" "docker compose exec -T bigcapital-redis redis-cli ping"

echo ""
echo "📊 Container Status:"
docker compose ps

echo ""
echo "💾 Volume Usage:"
docker system df

echo ""
echo "🌐 BigCapital should be available at: http://simple.local:3000"
