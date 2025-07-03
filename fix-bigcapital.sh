#!/bin/bash

# BigCapital Plugin Configuration Fix Script
# Simple wrapper for the Python diagnostic script

set -e

echo "🔧 BigCapital Plugin Configuration Fix"
echo "======================================"
echo

# Check if we're in the right directory
if [ ! -f "scripts/fix_bigcapital_config.py" ]; then
    echo "❌ Error: This script must be run from the Business-Plugin-Middleware root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: scripts/fix_bigcapital_config.py"
    exit 1
fi

# Make the Python script executable
chmod +x scripts/fix_bigcapital_config.py

# Run the Python script
echo "🚀 Running BigCapital configuration fix..."
echo
python3 scripts/fix_bigcapital_config.py

echo
echo "✅ Script completed!"
echo
echo "📋 Manual steps if needed:"
echo "   1. Visit: http://simple.local:5000/plugins"
echo "   2. Click 'Configure' for BigCapital plugin"
echo "   3. Enter your API key from: https://app.bigcapital.ly/settings/api"
echo "   4. Save configuration"
echo
