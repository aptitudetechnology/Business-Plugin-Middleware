# Setting up Paperless-NGX Integration

## Quick Start

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Check logs to ensure everything is starting:**
   ```bash
   docker-compose logs -f
   ```

3. **Access Paperless-NGX:**
   - Open http://localhost:8000 in your browser
   - Follow the setup wizard to create an admin user

4. **Get your API token:**
   - Log into Paperless-NGX
   - Go to Settings > API Tokens
   - Create a new token and copy it

5. **Update the configuration:**
   - Edit `config/plugins.json` and replace `YOUR_REAL_API_TOKEN_HERE` with your actual token
   - OR use the web interface at http://localhost:5000/plugins to configure plugins

6. **Restart the middleware:**
   ```bash
   docker-compose restart middleware
   ```

## Manual Configuration

### Option 1: Via Web Interface
1. Visit http://localhost:5000/plugins
2. Click "Configure" next to Paperless-NGX
3. Enter your API token
4. Save the configuration

### Option 2: Edit Configuration Files
Edit `config/plugins.json`:
```json
{
  "paperless_ngx": {
    "enabled": true,
    "api_key": "your-actual-api-token-here",
    "base_url": "http://paperless-ngx:8000",
    "timeout": 30,
    "auto_refresh": true,
    "page_size": 25
  }
}
```

## Troubleshooting

### Plugin Initialization Errors
If you see abstract method errors for InvoicePlane or Invoice Ninja:
- These plugins are still in development
- You can disable them in `config/plugins.json` by setting `"enabled": false`

### Connection Issues
- Ensure all containers are on the same network
- Check container names match the configuration
- Verify API tokens are correct and have proper permissions

### Checking Services
```bash
# Check if all containers are running
docker-compose ps

# Check specific service logs
docker-compose logs paperless-ngx
docker-compose logs middleware

# Check network connectivity between containers
docker-compose exec middleware ping paperless-ngx
```

## Current Status

After the recent fixes:
- ✅ Loguru logging implemented across all plugins
- ✅ Plugin loading and discovery working
- ✅ OCR Processor plugin fully functional
- ✅ Docker Compose includes Paperless-NGX service
- ✅ Fixed abstract method errors in InvoicePlane and Invoice Ninja plugins
- ⚠️  Paperless-NGX needs real API token configuration
- ⚠️  BigCapital requires external internet access for DNS resolution

The middleware should now start properly with only the OCR processor working until you configure the API tokens for the other services.
