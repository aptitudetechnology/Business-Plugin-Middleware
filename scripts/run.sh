#!/usr/bin/env bash
set -e

echo "🚀 Starting Paperless-BigCapital Middleware..."

# Get the directory of this script and set as project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

cd "$PROJECT_ROOT"

# Create necessary directories
mkdir -p logs uploads data

echo "📁 Created necessary directories"

# Initialize database if needed
if [ ! -f "data/middleware.db" ]; then
    echo "🗄️  Initializing database..."
    # TODO: Add database initialization commands here, e.g.:
    # python scripts/init_db.py
fi

# Initialize plugins (if any provide init.sh)
for plugin_init in plugins/*/init.sh; do
    if [ -f "$plugin_init" ]; then
        plugin_name=$(basename "$(dirname "$plugin_init")")
        echo "🔌 Initializing plugin: $plugin_name"
        bash "$plugin_init"
    fi
done

echo "🐍 Starting Python application..."

# Run the Flask application, logging output
python -m web.app | tee logs/app.log