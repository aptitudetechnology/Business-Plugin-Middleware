# PDF2MD Document Management System + Plugin Development Instructions

 OpenGovSG's pdf2md library (https://github.com/opengovsg/pdf2md), plus a corresponding plugin for the Business Plugin Middleware (https://github.com/aptitudetechnology/Business-Plugin-Middleware) that integrates with this service via API.



## Overview
Build a lightweight document management web application (similar to Paperless-NGX) with client-side PDF to Markdown conversion using OpenGovSG's pdf2md library, plus a corresponding plugin for the Business Plugin Middleware that integrates with this system via API.

## Two-Part Architecture

### Part 1: PDF2MD Document Management System (Web Application)
Standalone web application with client-side processing and document management

### Part 2: PDF2MD Plugin (Python)
Plugin that integrates the document system with your middleware via API

---

## Part 1: PDF2MD Document Management System

### Application Structure
```
pdf2md-docs/
  backend/
    app.py                    # Flask application
    models/
      document.py             # Document model
      metadata.py             # Metadata model
    routes/
      documents.py            # Document CRUD API
      search.py               # Search endpoints
      upload.py               # Upload handling
    utils/
      storage.py              # File storage utilities
      indexing.py             # Search indexing
    config/
      settings.py             # Application config
    requirements.txt
  frontend/
    static/
      js/
        pdf2md.js             # Client-side PDF conversion
        document-viewer.js    # Document viewer
        search.js             # Search functionality
        upload.js             # Upload handling
      css/
        styles.css            # Application styles
      lib/
        pdf2md.min.js         # OpenGovSG pdf2md library
    templates/
      base.html
      documents.html          # Document list/grid
      upload.html             # Upload interface
      viewer.html             # Document viewer
  docker/
    Dockerfile
  README.md
```

### Core Features

#### Document Management
- **Upload Interface**: Drag-and-drop PDF upload
- **Document Storage**: File system or cloud storage
- **Metadata Management**: Tags, categories, dates, notes
- **Document Viewer**: Preview PDFs and converted Markdown
- **Search**: Full-text search across documents and metadata

#### Client-Side Processing
- **PDF2MD Conversion**: Browser-based PDF to Markdown
- **Real-time Progress**: Visual feedback during conversion
- **Batch Processing**: Multiple document conversion
- **Format Options**: Configurable conversion settings

#### API Endpoints
- `POST /api/documents` - Upload and process document
- `GET /api/documents` - List documents with filters
- `GET /api/documents/{id}` - Get specific document
- `PUT /api/documents/{id}` - Update document metadata
- `DELETE /api/documents/{id}` - Delete document
- `GET /api/documents/{id}/markdown` - Get converted markdown
- `GET /api/search` - Search documents
- `GET /api/health` - System health check

### Database Schema
```sql
-- Documents table
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255),
    original_name VARCHAR(255),
    file_path VARCHAR(500),
    markdown_content TEXT,
    file_size INTEGER,
    mime_type VARCHAR(100),
    upload_date DATETIME,
    processed_date DATETIME,
    status VARCHAR(50), -- 'uploaded', 'processing', 'processed', 'failed'
    uploaded_by VARCHAR(100),
    notes TEXT
);

-- Tags table
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE
);

-- Document tags relationship
CREATE TABLE document_tags (
    document_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- Metadata table
CREATE TABLE document_metadata (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    key VARCHAR(100),
    value TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

### Client-Side PDF Processing
```javascript
// pdf2md.js - Core conversion logic
class PDF2MDProcessor {
    constructor() {
        this.pdf2md = new PDF2MD(); // OpenGovSG library
    }
    
    async convertPDF(file, options = {}) {
        // Convert PDF to Markdown in browser
        // Show progress, handle errors
        // Return markdown content
    }
    
    async batchConvert(files, options = {}) {
        // Process multiple PDFs
        // Update progress for each file
    }
}
```

### Frontend Features
- **Upload Interface**: Modern drag-and-drop with progress
- **Document Grid**: Thumbnail view with metadata
- **Search Interface**: Advanced search with filters
- **Document Viewer**: Side-by-side PDF and Markdown view
- **Tagging System**: Tag management and filtering
- **Responsive Design**: Mobile-friendly interface

---

## Part 2: PDF2MD Plugin (Python)

### Plugin Directory Structure
```
plugins/
  pdf2md_plugin/
    __init__.py
    plugin.py                 # Main plugin class
    config.json              # Plugin configuration
    client.py               # API client for document system
    requirements.txt        # Python dependencies
    tests/
      test_plugin.py        # Unit tests
    README.md               # Documentation
```

### Plugin Manager Integration

#### Core Plugin Class
```python
class PDF2MDPlugin(ProcessingPlugin):
    def __init__(self, name):
        # Initialize with document system client
        
    def validate_config(self, config):
        # Validate document system endpoint, auth, etc.
        
    def initialize(self, app_context):
        # Initialize API client, test connectivity
        
    def process_document(self, document_path, metadata=None):
        # Upload PDF to document system
        # Return processing status and document ID
        
    def get_processed_documents(self, filters=None):
        # Query processed documents from system
        
    def search_documents(self, query):
        # Search documents via API
        
    def cleanup(self):
        # Cleanup resources
        
    def get_health_status(self):
        # Check document system connectivity
```

#### Plugin Configuration
```json
{
  "name": "pdf2md_plugin",
  "version": "1.0.0",
  "enabled": true,
  "supported_formats": [".pdf"],
  "document_system": {
    "endpoint": "http://localhost:5000",
    "api_key": "your-api-key",
    "timeout": 30,
    "retry_attempts": 3
  },
  "processing": {
    "auto_tag": true,
    "default_tags": ["middleware-upload"],
    "preserve_original": true,
    "notify_on_complete": true
  },
  "integration": {
    "webhook_url": "http://middleware:8000/webhook/pdf2md",
    "sync_metadata": true
  }
}
```

---

## Development Phases

### Phase 1: Document System Backend
1. **Flask Application Setup**
   - Basic Flask app with SQLAlchemy
   - Document model and database schema
   - File storage configuration

2. **Core API Endpoints**
   - Document upload endpoint
   - Document CRUD operations
   - Search functionality

3. **Storage & Indexing**
   - File storage utilities
   - Search indexing setup
   - Metadata management

### Phase 2: Client-Side Processing
1. **PDF2MD Integration**
   - Integrate OpenGovSG pdf2md library
   - Client-side conversion logic
   - Progress tracking and error handling

2. **Upload Interface**
   - Modern drag-and-drop upload
   - Real-time conversion feedback
   - Batch processing support

3. **Document Viewer**
   - PDF preview functionality
   - Markdown display
   - Side-by-side comparison

### Phase 3: Document Management UI
1. **Document List/Grid**
   - Responsive document grid
   - Sorting and filtering
   - Thumbnail generation

2. **Search Interface**
   - Advanced search form
   - Full-text search results
   - Search filters and facets

3. **Tagging System**
   - Tag management interface
   - Auto-tagging features
   - Tag-based organization

### Phase 4: Plugin Development
1. **Plugin Structure**
   - ProcessingPlugin implementation
   - API client for document system
   - Configuration management

2. **Integration Logic**
   - Document upload via API
   - Status monitoring
   - Metadata synchronization

3. **Advanced Features**
   - Webhook notifications
   - Batch processing
   - Search integration

### Phase 5: Integration & Testing
1. **End-to-End Testing**
   - Document upload workflow
   - Plugin integration testing
   - Performance testing

2. **UI/UX Polish**
   - Responsive design
   - Loading states
   - Error handling

3. **Deployment**
   - Docker containerization
   - Production configuration
   - Monitoring setup

---

## Technical Architecture

### Client-Side Processing Flow
```
1. User uploads PDF via web interface
2. PDF2MD processes file in browser
3. Converted Markdown sent to backend
4. Document stored with metadata
5. Search index updated
6. Plugin notified via webhook (optional)
```

### Plugin Integration Flow
```
1. Middleware receives document
2. PDF2MD Plugin uploads to document system
3. Document system processes client-side
4. Plugin receives processing status
5. Plugin returns result to middleware
6. Webhook notifies middleware when complete
```

### Data Flow
- **Documents**: Stored in filesystem/cloud storage
- **Metadata**: Stored in database (SQLite/PostgreSQL)
- **Search Index**: Full-text search engine
- **Client Processing**: No server-side PDF processing needed

---

## Key Benefits

### Performance
- **Client-Side Processing**: No server load for PDF conversion
- **Faster Response**: Real-time conversion feedback
- **Scalability**: Processing scales with users

### User Experience
- **Modern Interface**: Drag-and-drop, real-time feedback
- **Document Organization**: Tagging, search, categorization
- **Viewer Integration**: Preview and markdown in one place

### Integration
- **API-First**: Clean API for external integrations
- **Plugin Support**: Easy middleware integration
- **Webhook Notifications**: Real-time status updates

---

## Next Session Deliverables

### Document System
1. ✅ Flask backend with document API
2. ✅ Database schema and models
3. ✅ File storage and upload handling
4. ✅ Client-side PDF2MD integration
5. ✅ Basic document viewer interface

### Plugin Implementation
1. ✅ ProcessingPlugin class structure
2. ✅ API client for document system
3. ✅ Configuration management
4. ✅ Integration with plugin manager
5. ✅ Webhook handling for notifications

### Integration Testing
1. ✅ End-to-end document processing
2. ✅ Plugin communication with document system
3. ✅ Upload interface integration
4. ✅ Search functionality testing

This architecture creates a powerful document management system with modern client-side processing while maintaining clean integration with your existing plugin middleware.