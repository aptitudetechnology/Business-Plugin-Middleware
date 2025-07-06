#!/bin/bash
# filepath: scripts/fix_journal_entries_schema.sh

set -e  # Exit on any error

echo "🔧 Fixing journal_entries schema..."

# Ensure we're in the project root
if [[ ! -f "app.py" ]]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Check if Flask is available
if ! command -v flask &> /dev/null; then
    echo "❌ Error: Flask CLI not found. Activating virtual environment..."
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    elif [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    else
        echo "❌ No virtual environment found. Please activate manually."
        exit 1
    fi
fi

# Set Flask app environment variable
export FLASK_APP=app.py

echo "📋 Current schema status:"
python scripts/check_schema.py --critical --silent || echo "⚠️ Schema mismatches found (expected)"

echo ""
echo "📝 Creating migration..."
flask db migrate -m "Add posted_by, status, and posted_at columns to journal_entries"

echo ""
echo "🚀 Applying migration..."
flask db upgrade

echo ""
echo "🔍 Verifying schema fix..."
python scripts/check_schema.py --critical

if [[ $? -eq 0 ]]; then
    echo ""
    echo "✅ Journal entries schema successfully fixed!"
    echo "🎉 All columns are now in sync between model and database"
else
    echo ""
    echo "⚠️ Schema verification completed with warnings (check output above)"
fi

echo ""
echo "📊 Final schema status:"
python scripts/check_schema.py --list-models