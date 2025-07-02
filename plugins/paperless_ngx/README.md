# Paperless-NGX Plugin

**A robust integration plugin for [Paperless-NGX](https://github.com/paperless-ngx/paperless-ngx) document management system.**

![Status](https://img.shields.io/badge/status-stable-green.svg)
![Features](https://img.shields.io/badge/features-complete-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## ✅ **Production Ready**

This plugin has been thoroughly tested and is ready for production use with proper configuration and API token setup.

### 🌟 **Key Features**

### 🌟 **Key Features**

- **📄 Document Browsing**: Browse and search your Paperless-NGX documents with pagination
- **🔍 Advanced OCR Viewing**: View both processed text and raw HTML/SVG content
- **📊 Document Metadata**: Access document types, correspondents, tags, and creation dates
- **🔗 Smart URL Handling**: Separate internal API and external browser URLs for Docker deployments
- **💾 Download Support**: Download documents directly through the middleware
- **🔎 Search Functionality**: Search documents by title, content, or metadata
- **📱 Modern Web Interface**: Responsive design with tabbed OCR viewer
- **📋 Copy/Export**: Copy OCR text to clipboard or download as files
- **⚙️ Dynamic Configuration**: Configure via web UI or configuration files
- **🔧 Real-time Debugging**: Built-in diagnostics and error handling

## 🚀 **Recent Enhancements**

- **Dual Content Viewer**: Separate tabs for processed text and raw HTML/SVG content
- **Network Flexibility**: Support for Docker service names and external hostnames
- **Enhanced Error Messages**: Specific guidance for API token and connectivity issues
- **Plugin Reload**: Hot-reload configuration without container restarts
- **Loguru Integration**: Advanced logging with structured output

## ⚙️ **Configuration**

### Docker Compose Setup (Recommended)

For containerized deployments using Docker Compose, add to your `config/config.ini`:

```ini
[paperless]
# Internal API URL (container-to-container communication)
api_url = http://paperless-ngx:8000
# External hostname URL (for browser links)
hostname_url = http://simple.local:8000
api_token = YOUR_REAL_API_TOKEN_HERE
enabled = true
```

### Host Network Setup

For direct host network access, use:

```ini
[paperless]
# Use your host IP for internal API calls
api_url = http://192.168.1.115:8000
# Use your preferred hostname for browser links
hostname_url = http://simple.local:8000
api_token = YOUR_REAL_API_TOKEN_HERE
enabled = true
```

### Plugin Configuration

The plugin also supports configuration via `config/plugins.json`:

```json
{
  "paperless_ngx": {
    "enabled": true,
    "api_key": "YOUR_REAL_API_TOKEN_HERE",
    "base_url": "http://paperless-ngx:8000",
    "hostname_url": "http://simple.local:8000",
    "timeout": 30,
    "page_size": 25
  }
}
```

## Getting Your API Token

1. Log into your Paperless-NGX instance
2. Go to **Settings** → **API Tokens**
3. Click **Create Token**
4. Give it a name (e.g., "Middleware Integration")
5. Copy the generated token and use it as your `api_key`

## Usage

Once configured, the plugin will:

1. Appear in the **Plugins** dropdown menu as "Paperless-NGX Documents"
2. Provide a web interface at `/paperless-ngx/documents`
3. Allow you to:
   - Browse all your documents with pagination
   - Search documents by title or content
   - View OCR content for any document
   - Access original documents in Paperless-NGX
   - Download documents directly

## API Endpoints

The plugin also provides API endpoints:

- `GET /paperless-ngx/documents` - List documents with search and pagination
- `GET /paperless-ngx/document/<id>` - Get document metadata
- `GET /paperless-ngx/document/<id>/content` - View document OCR content

## Error Handling

The plugin includes robust error handling for:

- Network connectivity issues
- Authentication problems
- API rate limiting
- Invalid document IDs
- Missing or corrupted documents

## Requirements

- Paperless-NGX instance (v1.10.0 or later recommended)
- Valid API token with read permissions
- Network access to your Paperless-NGX instance

## Troubleshooting

### Plugin Not Loading
- Check that `enabled = true` in your configuration
- Verify your API token is correct
- Ensure your Paperless-NGX instance is accessible

### No Documents Showing
- Verify your API token has the correct permissions
- Check that your Paperless-NGX instance is running
- Look at the application logs for detailed error messages

### Connection Issues
- Verify the `base_url` is correct (no trailing slash)
- Check firewall settings and network connectivity
- Try increasing the `timeout` value if requests are slow

## Security Notes

- Keep your API token secure and never commit it to version control
- Use environment variables for production deployments
- Consider using a dedicated API token with minimal required permissions
- Regularly rotate your API tokens for security

## Integration with Other Plugins

This plugin works well with:

- **OCR Processor Plugin**: For processing documents before uploading to Paperless-NGX
- **BigCapital Plugin**: For syncing financial documents between systems
- **Document Processing Pipeline**: For automated document workflows
