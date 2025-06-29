#!/bin/bash

echo "🧪 Business Plugin Middleware - Development Setup"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python installation
if command_exists python3; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check pip installation
if command_exists pip3; then
    echo "✅ pip3 found"
else
    echo "❌ pip3 not found. Please install pip."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs uploads config database data

# Copy configuration if it doesn't exist
if [ ! -f "config/config.ini" ]; then
    echo "⚙️  Creating configuration..."
    cp config/config.ini.example config/config.ini
fi

# Copy environment file if it doesn't exist  
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cp .env.example .env
fi

# Install system dependencies message
echo ""
echo "📋 System Dependencies Checklist:"
echo "  For OCR functionality, install Tesseract:"
echo "    Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-eng"
echo "    macOS: brew install tesseract"
echo "    Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
echo ""

# Check Tesseract
if command_exists tesseract; then
    echo "✅ Tesseract found: $(tesseract --version | head -n1)"
else
    echo "⚠️  Tesseract not found (optional for OCR functionality)"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "
try:
    from config.settings import Config
    from database.connection import DatabaseManager
    config = Config('config/config.ini')
    db_manager = DatabaseManager(config)
    print('✅ Database initialized')
except Exception as e:
    print(f'⚠️  Database init warning: {e}')
"

# Run tests
echo "🧪 Running tests..."
python3 test_plugin_architecture.py

echo ""
echo "🎉 Development setup complete!"
echo ""
echo "To start development:"
echo "  1. source venv/bin/activate"
echo "  2. python3 web/app.py"
echo ""
echo "Or use the startup script:"
echo "  ./start.sh"
echo ""
echo "Available URLs:"
echo "  🌐 Application: http://localhost:5000"
echo "  📊 Dashboard: http://localhost:5000/"
echo "  🔧 Plugins: http://localhost:5000/plugins"
echo "  📄 API Health: http://localhost:5000/api/health"
