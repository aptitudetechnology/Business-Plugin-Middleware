#!/bin/bash
# BigCapital Health Check Script

set -e

echo "🔍 BigCapital Health Check"
echo "=========================="

# Load .env file if exists
if [[ -f .env ]]; then
    echo "📄 Loading environment variables from .env"
    set -o allexport
    source .env
    set +o allexport
fi

# Helper to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Helper function for service checks
check_service() {
    local name="$1"
    local cmd="$2"
    local help="$3"

    echo -n "🔎 $name... "
    output=$(eval "$cmd" 2>&1)
    if [[ $? -eq 0 ]]; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy"
        if [[ -n "$help" ]]; then
            echo "   ↳ $help"
        fi
        echo "   ↳ Output:"
        echo "   ---------------------------------"
        echo "$output" | sed 's/^/   /'
        echo "   ---------------------------------"
    fi
}

echo
echo "🌐 Web Service Checks"
echo "----------------------"

check_service "BigCapital App" \
    "curl -sf http://localhost:3000/health" \
    "Visit http://localhost:3000/health in your browser or use: curl -v http://localhost:3000/health"

echo
echo "🗄️  Database Checks"
echo "----------------------"

if command_exists docker-compose; then
    check_service "MariaDB" \
        "docker-compose exec bigcapital-mariadb mysqladmin ping -ubigcapital -pbigcapital_secure_password" \
        "Could not ping MariaDB. Ensure credentials and host are correct."

    if [[ -z "$MONGO_URI" ]]; then
        echo "⚠️  Skipping Mongo URI validation: MONGO_URI not set"
    fi

    check_service "MongoDB" \
        "docker-compose exec bigcapital-mongo mongosh --eval 'db.runCommand(\"ping\")' --quiet" \
        "Failed to ping MongoDB. Is the container running and accepting connections?"
else
    echo "❌ docker-compose is not installed or not in PATH."
fi

echo
echo "🧠 Cache Service Checks"
echo "------------------------"

if command_exists docker-compose; then
    check_service "Redis" \
        "docker-compose exec bigcapital-redis redis-cli ping | grep -q PONG" \
        "Redis did not respond with PONG. Ensure it's running and accessible."
fi

echo
echo "📦 Container Status:"
echo "----------------------"
if command_exists docker-compose; then
    docker-compose ps
else
    echo "docker-compose not available."
fi

echo
echo "💾 Volume Usage:"
echo "----------------------"
if command_exists docker; then
    docker system df
else
    echo "docker command not available."
fi

echo
echo "🌐 BigCapital should be available at: http://simple.local:3000"
