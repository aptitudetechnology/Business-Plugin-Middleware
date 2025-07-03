#!/bin/bash
# BigCapital Health Check Script

set -e

echo "🔍 BigCapital Health Check"
echo "=========================="

# Load environment variables from .env safely
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env"
    while IFS='=' read -r key value; do
        if [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
            export "$key"="${value%\"}"
        fi
    done < <(grep -v '^#' .env | grep '=')
else
    echo "⚠️  .env file not found — skipping environment load"
fi

echo ""

# Function to check a service and print verbose output on failure
check_service() {
    local service_name=$1
    local check_command=$2
    local error_message=${3:-"Check failed."}

    echo -n "🔎 Checking $service_name... "

    if output=$(eval "$check_command" 2>&1); then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy"
        echo "   ↳ $error_message"
        echo "   ↳ Output:"
        echo "   ---------------------------------"
        echo "$output" | sed 's/^/   /'
        echo "   ---------------------------------"
    fi
}

# HTTP app check with response status
echo "🌐 Web Service Checks"
echo "----------------------"
echo -n "🔎 BigCapital App... "
app_response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:3000/health || echo "000")

if [ "$app_response" == "200" ]; then
    echo "✅ Healthy (HTTP 200)"
else
    echo "❌ Unhealthy (HTTP $app_response)"
    echo "   ↳ Visit http://localhost:3000/health in your browser or use: curl -v http://localhost:3000/health"
fi


echo ""

# Check database services
echo "🗄️  Database Checks"
echo "----------------------"
check_service "MariaDB" "mysqladmin ping -h bigcapital-mariadb -u bigcapital -pbigcapital_secure_password" \
    "Could not ping MariaDB. Ensure credentials and host are correct."

# Validate MONGO_URI
if [ -n "$MONGO_URI" ]; then
    echo -n "🔎 Validating MongoDB URI... "
    if [[ $MONGO_URI =~ ^mongodb(\+srv)?:\/\/[^:]+:[^@]+@[^\/]+\/[^?]+(\?.*)?$ ]]; then
        echo "✅ Format OK"
    else
        echo "❌ Invalid format"
        echo "   ↳ Example: mongodb://user:pass@host:27017/dbname?retryWrites=true"
    fi
else
    echo "⚠️  Skipping Mongo URI validation: MONGO_URI not set"
fi

check_service "MongoDB" \
    "docker compose exec -T bigcapital-mongo mongosh --eval 'db.runCommand({ ping: 1 })' --quiet" \
    "Failed to ping MongoDB. Is the container running and accepting connections?"

echo ""

# Check Redis
echo "🧠 Cache Service Checks"
echo "------------------------"
check_service "Redis" \
    "docker compose exec -T bigcapital-redis redis-cli ping | grep -q PONG" \
    "Redis did not respond with PONG. Ensure it's running and accessible."

echo ""
echo "📦 Container Status:"
echo "----------------------"
docker compose ps

echo ""
echo "💽 Volume Usage:"
echo "----------------------"
docker system df

echo ""
echo "🌍 BigCapital should be available at: http://simple.local:3000"
