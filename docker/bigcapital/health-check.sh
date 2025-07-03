#!/bin/bash

echo "🔍 BigCapital Health Check"
echo "=========================="

# -----------------------------------------------------------------------------
# Load .env Safely
# -----------------------------------------------------------------------------
echo "📄 Loading environment variables from .env"

if [[ ! -f .env ]]; then
    echo "❌ .env file not found. Please create one."
    exit 1
fi

# Validate .env lines
bad_lines=$(grep -vE '^\s*#|^\s*$|^[A-Za-z_][A-Za-z0-9_]*=' .env)
if [[ -n "$bad_lines" ]]; then
    echo "⚠️ Found invalid lines in .env:"
    echo "$bad_lines"
    echo ""
    echo "Please fix or comment out these lines before continuing."
    exit 1
fi

# Load valid environment variables
export $(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | xargs)

# -----------------------------------------------------------------------------
# Web Service Check
# -----------------------------------------------------------------------------
echo ""
echo "🌐 Web Service Checks"
echo "----------------------"

HEALTH_URL="${APP_URL}/health"
if command -v curl > /dev/null; then
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")
    if [[ "$http_code" == "200" ]]; then
        echo "🔎 BigCapital App... ✅ Healthy (HTTP 200)"
    else
        echo "🔎 BigCapital App... ❌ Unhealthy (HTTP $http_code)"
        echo "   ↳ Visit $HEALTH_URL or run: curl -v $HEALTH_URL"
    fi
else
    echo "❌ curl not found. Cannot check web health."
fi

# -----------------------------------------------------------------------------
# Database Checks
# -----------------------------------------------------------------------------
echo ""
echo "🗄️  Database Checks"
echo "----------------------"

# MariaDB
if command -v mysqladmin > /dev/null; then
    mariadb_status=$(mysqladmin ping -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" --password="$DB_PASSWORD" 2>&1)
    if [[ "$mariadb_status" == *"mysqld is alive"* ]]; then
        echo "🔎 MariaDB... ✅ Healthy"
    else
        echo "🔎 MariaDB... ❌ Unhealthy"
        echo "   ↳ Could not ping MariaDB. Check DB_HOST, DB_USER, and credentials."
        echo "   ↳ Output:"
        echo "   ---------------------------------"
        echo "$mariadb_status"
        echo "   ---------------------------------"
    fi
else
    echo "❌ mysqladmin not found. Cannot check MariaDB."
fi

# MongoDB
echo ""
if [[ -z "$MONGODB_URI" ]]; then
    echo "⚠️  Skipping MongoDB check: MONGODB_URI not set"
else
    if command -v docker > /dev/null; then
        mongo_output=$(docker run --rm mongo:6.0 mongosh "$MONGODB_URI" --eval "db.runCommand({ ping: 1 })" 2>&1)
        if [[ "$mongo_output" ==_]()]()
