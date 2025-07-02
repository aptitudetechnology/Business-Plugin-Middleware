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

**A robust integration plugin for [Paperless-NGX](https://github.com/paperless-ngx/paperless-ngx) document management system.**

![Status](https://img.shields.io/badge/status-pre--alpha-red.svg)
![Features](https://img.shields.io/badge/features-development-yellow.svg)
![Docker](https://img.shields.io/badge/docker-experimental-orange.svg)

## ⚠️ **Pre-Alpha Development Status**

This plugin is currently in **pre-alpha development** and should **NOT** be used in production environments. While basic functionality may work, expect bugs, breaking changes, and potential data issues.

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

## � **Development Progress**

Recent development work includes:
- **Basic OCR Viewer**: Initial implementation of OCR content viewing
- **Network Configuration**: Docker service name support (experimental)
- **Error Messages**: Basic error handling implementation
- **Plugin Structure**: Foundation plugin architecture
- **Logging**: Basic Loguru integration

**Note**: All features are experimental and subject to significant changes.

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

## 🗺️ **Roadmap**

### 🔨 **In Development (Current Version)**
- **Basic Integration**: Initial Paperless-NGX API connection attempts
- **Document Browsing**: Experimental document listing functionality
- **Simple OCR**: Basic OCR content display (unstable)
- **Configuration**: Rudimentary configuration management
- **Web Interface**: Basic UI components (incomplete)
- **Error Handling**: Minimal error reporting
- **Docker Support**: Experimental containerization

### 🎯 **Priority Development Goals**

#### **Phase 1: Core Functionality (Q3 2025)**
- [ ] **Stable API Integration**: Reliable Paperless-NGX connectivity
- [ ] **Document Management**: Complete browse and search functionality
- [ ] **OCR Content**: Dual-view OCR content (processed text + raw HTML/SVG)
- [ ] **Configuration**: Web UI and file-based configuration
- [ ] **Error Handling**: Comprehensive error messages with guidance
- [ ] **Testing**: Unit tests and integration tests
- [ ] **Bulk Operations**: Multi-document selection and batch actions
- [ ] **Document Upload**: Upload documents directly to Paperless-NGX
- [ ] **Tag Management**: Create, edit, and assign tags through the middleware
- [ ] **Workflow Automation**: Automated document processing rules
- [ ] **Document Versioning**: Track and manage document versions

#### **Phase 2: Advanced Search & Analytics**
- [ ] **Full-Text Search**: Enhanced search with fuzzy matching and filters
- [ ] **Search Suggestions**: Auto-complete and search history
- [ ] **Document Analytics**: Usage statistics and document insights
- [ ] **Custom Filters**: Save and reuse complex search filters
- [ ] **Advanced Sorting**: Multiple sort criteria with custom ordering

#### **Phase 3: Integration & Collaboration**
- [ ] **Webhook Support**: Real-time notifications for document events
- [ ] **API Rate Limiting**: Intelligent request throttling and queuing
- [ ] **Multi-Instance Support**: Connect to multiple Paperless-NGX instances
- [ ] **User Permissions**: Role-based access control integration
- [ ] **Collaborative Features**: Document sharing and comments

#### **Phase 4: Performance & Scalability**
- [ ] **Caching Layer**: Redis-based caching for improved performance
- [ ] **Background Processing**: Async document processing with Celery
- [ ] **Pagination Optimization**: Virtual scrolling for large document sets
- [ ] **Connection Pooling**: Optimized HTTP connection management
- [ ] **Health Monitoring**: Advanced plugin health checks and metrics

#### **Phase 5: Advanced Features**
- [ ] **AI Integration**: Document classification and content analysis
- [ ] **Custom Fields**: Support for Paperless-NGX custom fields
- [ ] **Document Templates**: Template-based document creation
- [ ] **Backup Integration**: Automated document backup workflows
- [ ] **Mobile Optimization**: Enhanced mobile interface and PWA support

### 🔮 **Future Considerations**
- **Machine Learning**: Auto-tagging and document classification
- **Blockchain Integration**: Document integrity verification
- **Cloud Storage**: Direct integration with cloud storage providers
- **API Marketplace**: Plugin ecosystem for extended functionality
- **Enterprise Features**: SSO, LDAP, and enterprise security features

### 📅 **Development Timeline**
- **Phase 1**: Q3-Q4 2025 (Core Functionality & Stability)
- **Alpha Release**: Q1 2026 (Basic feature completeness)
- **Beta Release**: Q2 2026 (Enhanced Document Processing)
- **Phase 2**: Q3 2026 (Search & Analytics)
- **Phase 3**: Q4 2026 (Integration & Collaboration)

**Note**: All timelines are estimates and subject to change based on development progress and testing results.

### 🤝 **Contributing to the Roadmap**
Want to influence the roadmap or contribute? We welcome:
- **Feature Requests**: Submit issues with enhancement proposals
- **Use Case Studies**: Share how you're using the plugin
- **Community Feedback**: Join discussions about prioritization
- **Code Contributions**: Submit PRs for roadmap features
- **Testing & QA**: Help test beta features and provide feedback

*Note: Timeline estimates are subject to change based on community feedback, development resources, and technical constraints.*
