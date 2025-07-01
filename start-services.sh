#!/bin/bash

echo "🚀 Business Plugin Middleware - Updated Setup"
echo "============================================="
echo ""

echo "📋 Current Status:"
echo "✅ All plugins converted to use Loguru logging"
echo "✅ Plugin loading and discovery fixed"
echo "✅ Abstract method errors resolved in InvoicePlane and Invoice Ninja"
echo "✅ Docker Compose updated with Paperless-NGX service"
echo "✅ OCR Processor plugin fully functional"
echo ""

echo "⚙️  Services included in Docker Compose:"
echo "- Business Plugin Middleware (port 5000)"
echo "- Redis (port 6379) - for caching"
echo "- Paperless-NGX (port 8000) - document management"
echo "- PostgreSQL - database for Paperless-NGX"
echo ""

echo "🔧 Next Steps:"
echo "1. Start all services: docker-compose up -d"
echo "2. Wait for Paperless-NGX to initialize (may take 1-2 minutes)"
echo "3. Access Paperless-NGX at http://localhost:8000 and create admin user"
echo "4. Create API token in Paperless-NGX Settings > API Tokens"
echo "5. Update config/plugins.json with your real API token"
echo "6. Restart middleware: docker-compose restart middleware"
echo ""

echo "🌐 Web Interfaces:"
echo "- Middleware Dashboard: http://localhost:5000"
echo "- Paperless-NGX: http://localhost:8000"
echo ""

echo "🛠️  Configuration Files:"
echo "- config/config.ini - Main configuration"
echo "- config/plugins.json - Plugin-specific settings"
echo ""

echo "📖 For detailed setup instructions, see: setup-paperless.md"
echo ""

read -p "Start all services now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting services..."
    docker-compose up -d
    echo ""
    echo "⏳ Services starting... Check logs with: docker-compose logs -f"
    echo "🌐 Access the middleware at: http://localhost:5000"
    echo "📋 Setup Paperless-NGX at: http://localhost:8000"
fi
