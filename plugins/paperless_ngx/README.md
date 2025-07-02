# ⚠️ **CRITICAL WARNING - READ BEFORE PROCEEDING** ⚠️

> ## 🚨 PRE-ALPHA SOFTWARE - NOT FUNCTIONAL 🚨
> 
> **THIS PROJECT IS CURRENTLY IN PRE-ALPHA DEVELOPMENT AND IS NOT YET FUNCTIONAL.**
> 
> ### ❌ DO NOT USE FOR:
> - Production environments
> - Business-critical data
> - Live financial systems
> - Any mission-critical applications
> 
> ### ⚠️ IMPORTANT DISCLAIMERS:
> - **DATA LOSS RISK**: This software may corrupt, lose, or mishandle your data
> - **NO RELIABILITY GUARANTEE**: Features may not work as expected or at all
> - **BREAKING CHANGES**: API and functionality will change without notice
> - **NO SUPPORT**: Limited or no support available during pre-alpha phase
> 
> ### 🔬 INTENDED FOR:
> - Development and testing purposes only
> - Contributors and early adopters willing to accept risks
> - Non-critical experimentation environments
> 
> **By using this software, you acknowledge and accept full responsibility for any potential data loss, system issues, or other consequences.**

---


# Paperless-NGX Plugin

This plugin provides integration with [Paperless-NGX](https://github.com/paperless-ngx/paperless-ngx), a powerful document management system.

## Features

- **Document Browsing**: Browse and search your Paperless-NGX documents
- **OCR Content Viewing**: View extracted text content from documents
- **Document Metadata**: Access document types, correspondents, tags, and dates
- **Direct Links**: Quick access to documents in your Paperless-NGX instance
- **Download Support**: Download documents directly through the middleware
- **Search Functionality**: Search documents by title, content, or metadata
- **Pagination**: Efficient browsing of large document collections

## Configuration

### Using Configuration File

Add to your `config/config.ini`:

```ini
[paperless_ngx]
api_key = your-paperless-api-token
base_url = https://your-paperless-instance.com
enabled = true
timeout = 30
page_size = 25
```

### Using Environment Variables

Set these environment variables:

```bash
PAPERLESS_NGX_API_KEY=your-paperless-api-token
PAPERLESS_NGX_BASE_URL=https://your-paperless-instance.com
PAPERLESS_NGX_ENABLED=true
PAPERLESS_NGX_TIMEOUT=30
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
