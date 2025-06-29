#!/bin/bash

echo "🚀 Starting Business Plugin Middleware..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check pip installation and set command
PIP_CMD=""
if command_exists pip3; then
    PIP_CMD="pip3"
elif command_exists pip; then
    PIP_CMD="pip"
else
    echo "❌ Neither pip3 nor pip found. Please install pip."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs uploads config database data

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Verify Flask installation first
echo "🔍 Verifying Flask installation..."
if python3 -c "import flask; print(f'✅ Flask {flask.__version__} is available')" 2>/dev/null; then
    echo "Flask verification passed"
else
    echo "❌ Flask not found. Installing essential packages..."
    $PIP_CMD install --upgrade pip
    $PIP_CMD install Flask==2.3.3 Werkzeug==2.3.7 Jinja2==3.1.2
    
    if python3 -c "import flask; print(f'✅ Flask {flask.__version__} installed')" 2>/dev/null; then
        echo "Flask installation successful"
    else
        echo "❌ Flask installation failed"
        exit 1
    fi
fi

$PIP_CMD install --upgrade pip

# Install/update dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing basic dependencies..."
    $PIP_CMD install flask werkzeug jinja2 python-dotenv requests
fi

# Check if configuration exists
if [ ! -f "config/config.ini" ]; then
    echo "⚙️  Creating default configuration..."
    cp config/config.ini.example config/config.ini 2>/dev/null || echo "No example config found, using defaults"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "
from config.settings import Config
from database.connection import DatabaseManager
import os

try:
    config_path = 'config/config.ini'
    if os.path.exists(config_path):
        config = Config(config_path)
        db_manager = DatabaseManager(config)
        print('✅ Database initialized successfully')
    else:
        print('⚠️  Configuration file not found, using defaults')
except Exception as e:
    print(f'⚠️  Database initialization warning: {e}')
"

# Check system dependencies
echo "🔍 Checking system dependencies..."

# Check for Tesseract OCR
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR found: $(tesseract --version | head -n1)"
else
    echo "⚠️  Tesseract OCR not found. Install with:"
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   macOS: brew install tesseract"
    echo "   Windows: Download from GitHub releases"
fi

# Test plugin system
echo "🧩 Testing plugin system..."
python3 test_plugin_architecture.py

# Start the application
echo "🐍 Starting Python application..."
echo "🌐 Application will be available at: http://localhost:5000"
echo "📊 Dashboard: http://localhost:5000/"
echo "🔧 Plugin Management: http://localhost:5000/plugins"
echo "📄 API Health: http://localhost:5000/api/health"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

python3 web/app.py
