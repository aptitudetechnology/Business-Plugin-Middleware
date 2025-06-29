# Running Business Plugin Middleware in Replit

## Quick Start

1. **Install Dependencies**
   ```bash
   ./start.sh
   ```

2. **Run the Application**
   ```bash
   python web/app.py
   ```

## What to Expect

- The application should start successfully even with placeholder Paperless-NGX configuration
- You'll see plugin loading messages in the logs
- The Paperless-NGX plugin will initialize with placeholder config (connection not tested)
- The web interface will be available at the provided URL

## Plugin Status

### Working Plugins
- **Paperless-NGX Plugin**: ✅ Loaded and initialized (placeholder config)
- **BigCapital Plugin**: ❌ Missing API key (expected)
- **OCR Processor**: ❌ Missing pytesseract (expected in basic environment)

### Failed Plugins
- **Invoice Ninja**: ❌ Missing plugin class (expected)
- **Invoice Plane**: ❌ Missing plugin class (expected)

## Testing the Paperless-NGX Integration

To test with a real Paperless-NGX instance:

1. Update `config/plugins.json`:
   ```json
   {
     "paperless_ngx": {
       "enabled": true,
       "api_key": "your-real-api-key",
       "base_url": "https://your-paperless-instance.com",
       "timeout": 30,
       "auto_refresh": true,
       "page_size": 25
     }
   }
   ```

2. Restart the application

## Available Routes

- `/` - Dashboard
- `/paperless-ngx-documents` - Browse Paperless-NGX documents
- `/paperless-ngx-document/<id>/content` - View OCR content

## Troubleshooting

If you see errors about missing abstract methods, the recent fixes should resolve them. The plugin system is designed to handle:
- Placeholder configurations gracefully
- Missing dependencies without crashing
- Failed plugin initializations

## Development Notes

- Plugin system uses modular architecture
- Templates are in `web/templates/`
- Plugin-specific templates: `paperless_ngx_*.html`
- Configuration is loaded from `config/plugins.json`
