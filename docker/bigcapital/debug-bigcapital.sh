#!/bin/bash

# BigCapital MongoDB Connection Debug Script
# This script helps identify and fix MongoDB connection issues

echo "🔍 BigCapital MongoDB Connection Troubleshooter"
echo "================================================"

# Function to check if container exists and is running
check_container() {
    local container_name=$1
    if docker ps | grep -q "$container_name"; then
        echo "✅ $container_name is running"
        return 0
    else
        echo "❌ $container_name is not running"
        return 1
    fi
}

# Function to test MongoDB connection from host
test_mongo_connection() {
    local mongo_uri=$1
    echo "🧪 Testing MongoDB connection: $mongo_uri"
    
    if docker exec bigcapital-mongo mongosh "$mongo_uri" --eval "db.runCommand('ping')" &>/dev/null; then
        echo "✅ MongoDB connection successful"
        return 0
    else
        echo "❌ MongoDB connection failed"
        return 1
    fi
}

echo ""
echo "📋 Step 1: Check container status"
echo "--------------------------------"
check_container "bigcapital"
check_container "bigcapital-mongo"
check_container "bigcapital-mariadb"
check_container "bigcapital-redis"

echo ""
echo "📋 Step 2: Check MongoDB connectivity"
echo "-----------------------------------"
if check_container "bigcapital-mongo"; then
    # Test different connection strings
    test_mongo_connection "mongodb://localhost:27017/bigcapital"
    test_mongo_connection "mongodb://bigcapital-mongo:27017/bigcapital"
    
    echo ""
    echo "📋 MongoDB container logs (last 10 lines):"
    docker logs --tail 10 bigcapital-mongo
fi

echo ""
echo "📋 Step 3: Check BigCapital environment variables"
echo "-----------------------------------------------"
if check_container "bigcapital"; then
    echo "Environment variables containing 'mongo' or 'database':"
    docker exec bigcapital env | grep -i -E "(mongo|database|db_)" | sort
fi

echo ""
echo "📋 Step 4: Check BigCapital application logs"
echo "------------------------------------------"
if check_container "bigcapital"; then
    echo "BigCapital container logs (last 5 lines):"
    docker logs --tail 5 bigcapital
fi

echo ""
echo "📋 Step 5: Suggested fixes"
echo "-------------------------"
echo "Based on the analysis above, try these solutions:"
echo ""
echo "🔧 Solution 1: Use pre-built BigCapital image"
echo "   Edit docker-compose.yml and replace the build section with:"
echo "   image: bigcapital/bigcapital:latest"
echo ""
echo "🔧 Solution 2: Create MongoDB without authentication"
echo "   Already implemented - MongoDB should not require auth"
echo ""
echo "🔧 Solution 3: Use environment file"
echo "   Create a .env file with MONGODB_URI=mongodb://bigcapital-mongo:27017/bigcapital"
echo ""
echo "🔧 Solution 4: Check BigCapital documentation"
echo "   Visit: https://docs.bigcapital.app for official configuration"
echo ""
echo "📧 If issues persist, this suggests BigCapital may need specific configuration"
echo "   or the build process needs to be customized for self-hosting."

# Quick fix attempt
echo ""
echo "🚀 Attempting automatic fix..."
echo "-----------------------------"

# Try to restart just the BigCapital container
if check_container "bigcapital"; then
    echo "Restarting BigCapital container..."
    docker restart bigcapital
    sleep 10
    
    echo "Checking if fix worked..."
    if docker logs --tail 5 bigcapital 2>&1 | grep -q "MongoParseError"; then
        echo "❌ MongoDB error still present"
    else
        echo "✅ No immediate MongoDB errors detected"
    fi
fi

echo ""
echo "🏁 Debug completed. Review the output above for next steps."
