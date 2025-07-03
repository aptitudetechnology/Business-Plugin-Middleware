#!/bin/bash
# BigCapital Database Initialization Script

echo "Initializing BigCapital database..."

# Wait for MySQL to be ready
until mysqladmin ping -h "localhost" --silent; do
    echo "Waiting for MySQL to be ready..."
    sleep 2
done

echo "MySQL is ready. Setting up BigCapital database..."

# Create database if it doesn't exist
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "
CREATE DATABASE IF NOT EXISTS bigcapital CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON bigcapital.* TO 'bigcapital'@'%';
FLUSH PRIVILEGES;
"

echo "BigCapital database initialization complete."
