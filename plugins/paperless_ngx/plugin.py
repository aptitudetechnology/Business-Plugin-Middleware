"""
Paperless-NGX Plugin for Business Plugin Middleware
Provides integration with Paperless-NGX document management system
"""

import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

from core.base_plugin import BasePlugin, ProcessingPlugin
from core.exceptions import PluginError, PluginConfigurationError


class PaperlessNGXPlugin(BasePlugin):
    """Plugin for integrating with Paperless-NGX document management system"""
    
    def __init__(self, config_or_name):
        # Handle both config dict and plugin name string
        if isinstance(config_or_name, dict):
            config = config_or_name
            super().__init__("paperless_ngx", "1.0.0")
        else:
            # Plugin manager passes name as string
            super().__init__(config_or_name, "1.0.0")
            config = {}
        
        self.description = "Integration with Paperless-NGX document management system"
        self.config = config
        
        # Configuration will be validated in initialize()
        self.base_url = None
        self.api_key = None
        self.timeout = 30
        self.page_size = 25
        self.verify_ssl = True
        self.session = None
        
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
    
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """Initialize the plugin and test connection"""
        try:
            # Setup configuration from config property
            config = self.config or {}
            self.base_url = config.get('base_url', '').rstrip('/')
            self.api_key = config.get('api_key', '')
            self.timeout = config.get('timeout', 30)
            self.page_size = config.get('page_size', 25)
            self.verify_ssl = config.get('verify_ssl', True)
            
            # Check for placeholder or invalid configuration
            if (not self.base_url or 
                not self.api_key or 
                self.base_url in ['http://localhost:8000', 'http://your-paperless-ngx-server:8000', 'https://your-paperless-instance.com'] or
                self.api_key in ['your_api_token_here', 'your-paperless-ngx-token', 'your-paperless-api-key']):
                self.logger.info("Paperless-NGX plugin initialized with placeholder configuration (connection not tested)")
                return True
            
            # Setup API client
            self._initialize_client()
            
            # Test the connection
            response = self._make_request('GET', '/api/documents/', params={'page_size': 1})
            self.logger.info(f"Paperless-NGX plugin initialized successfully. API connection tested.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Paperless-NGX plugin: {str(e)}")
            # Still return True for placeholder configurations to allow startup
            if (self.base_url in ['http://localhost:8000', 'http://your-paperless-ngx-server:8000', 'https://your-paperless-instance.com'] or
                self.api_key in ['your_api_token_here', 'your-paperless-ngx-token', 'your-paperless-api-key']):
                self.logger.info("Continuing initialization despite connection error (placeholder config)")
                return True
            return False
    
    def _initialize_client(self):
        """Initialize the API client with current configuration"""
        try:
            if self.session:
                self.session.close()
            
            self.session = requests.Session()
            self.session.headers.update({
                'Authorization': f'Token {self.api_key}',
                'Content-Type': 'application/json'
            })
            
            # Configure SSL verification
            self.session.verify = self.verify_ssl
            
            self.logger.info("Paperless-NGX API client initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize API client: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        try:
            if hasattr(self, 'session') and self.session:
                self.session.close()
            self.logger.info("Paperless-NGX plugin cleanup completed successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Error during Paperless-NGX plugin cleanup: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to Paperless-NGX API"""
        try:
            if not self.session or not self.base_url or not self.api_key:
                return False
            
            # Make a simple API call to test connection
            response = self._make_request('GET', '/api/documents/', params={'page_size': 1})
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def test_connection_with_config(self, test_config=None):
        """Test connection with current or provided configuration"""
        try:
            # Use test configuration if provided
            if test_config:
                base_url = test_config.get('base_url', self.base_url)
                api_key = test_config.get('api_key', self.api_key)
                verify_ssl = test_config.get('verify_ssl', self.verify_ssl)
            else:
                base_url = self.base_url
                api_key = self.api_key
                verify_ssl = self.verify_ssl
            
            if not base_url or not api_key:
                return False
            
            # Test API connection
            headers = {
                'Authorization': f'Token {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{base_url}/api/documents/",
                headers=headers,
                params={'page_size': 1},
                timeout=10,
                verify=verify_ssl
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_config_form(self):
        """Return HTML form for plugin configuration"""
        return f'''
        <form id="pluginConfigForm">
            <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="config_enabled" name="enabled" 
                       {'checked' if self.config.get('enabled', False) else ''}>
                <label class="form-check-label" for="config_enabled">
                    Enable Paperless-NGX Integration
                </label>
            </div>
            
            <div class="mb-3">
                <label for="config_base_url" class="form-label">Base URL</label>
                <input type="url" class="form-control" id="config_base_url" name="base_url" 
                       value="{self.config.get('base_url', '')}" 
                       placeholder="https://your-paperless-instance.com">
                <div class="form-text">The base URL of your Paperless-NGX instance</div>
            </div>
            
            <div class="mb-3">
                <label for="config_api_key" class="form-label">API Key</label>
                <input type="password" class="form-control" id="config_api_key" name="api_key" 
                       value="{'****' if self.config.get('api_key') else ''}" 
                       placeholder="Enter API key">
                <div class="form-text">Your Paperless-NGX API key. Leave blank to keep current value.</div>
            </div>
            
            <div class="mb-3">
                <label for="config_timeout" class="form-label">Request Timeout (seconds)</label>
                <input type="number" class="form-control" id="config_timeout" name="timeout" 
                       value="{self.config.get('timeout', 30)}" min="5" max="300">
                <div class="form-text">Timeout for API requests (5-300 seconds)</div>
            </div>
            
            <div class="mb-3">
                <label for="config_page_size" class="form-label">Default Page Size</label>
                <input type="number" class="form-control" id="config_page_size" name="page_size" 
                       value="{self.config.get('page_size', 25)}" min="1" max="100">
                <div class="form-text">Number of documents to fetch per page (1-100)</div>
            </div>
            
            <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="config_auto_refresh" name="auto_refresh" 
                       {'checked' if self.config.get('auto_refresh', False) else ''}>
                <label class="form-check-label" for="config_auto_refresh">
                    Auto-refresh document list
                </label>
                <div class="form-text">Automatically refresh the document list periodically</div>
            </div>
            
            <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="config_verify_ssl" name="verify_ssl" 
                       {'checked' if self.config.get('verify_ssl', True) else ''}>
                <label class="form-check-label" for="config_verify_ssl">
                    Verify SSL certificates
                </label>
                <div class="form-text">Disable only if using self-signed certificates</div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <button type="button" class="btn btn-outline-secondary w-100" onclick="testConnection()">
                        <i class="fas fa-plug"></i> Test Connection
                    </button>
                </div>
                <div class="col-md-6">
                    <button type="button" class="btn btn-outline-info w-100" onclick="refreshPluginStatus()">
                        <i class="fas fa-sync-alt"></i> Refresh Status
                    </button>
                </div>
            </div>
        </form>
        
        <script>
        function testConnection() {{
            const baseUrl = document.getElementById('config_base_url').value;
            const apiKey = document.getElementById('config_api_key').value;
            
            if (!baseUrl || !apiKey || apiKey === '****') {{
                alert('Please enter both Base URL and API Key to test connection');
                return;
            }}
            
            const testData = {{
                base_url: baseUrl,
                api_key: apiKey
            }};
            
            fetch('/api/plugins/paperless_ngx/test-connection', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify(testData)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert('Connection successful!');
                }} else {{
                    alert('Connection failed: ' + data.error);
                }}
            }})
            .catch(error => {{
                alert('Error testing connection: ' + error);
            }});
        }}
        
        function refreshPluginStatus() {{
            // Refresh plugin status display
            location.reload();
        }}
        </script>
        '''
    
    def update_config(self, config_data):
        """Update plugin configuration with new data"""
        try:
            # Validate configuration
            if 'base_url' in config_data and config_data['base_url']:
                # Ensure base_url ends without trailing slash
                config_data['base_url'] = config_data['base_url'].rstrip('/')
            
            if 'timeout' in config_data:
                timeout = int(config_data['timeout'])
                if timeout < 5 or timeout > 300:
                    raise ValueError("Timeout must be between 5 and 300 seconds")
                config_data['timeout'] = timeout
            
            if 'page_size' in config_data:
                page_size = int(config_data['page_size'])
                if page_size < 1 or page_size > 100:
                    raise ValueError("Page size must be between 1 and 100")
                config_data['page_size'] = page_size
            
            # Update configuration
            self.config.update(config_data)
            
            # Update instance attributes
            self.base_url = self.config.get('base_url', '')
            self.timeout = self.config.get('timeout', 30)
            self.page_size = self.config.get('page_size', 25)
            self.verify_ssl = self.config.get('verify_ssl', True)
            
            # Update API key if provided
            if 'api_key' in config_data and config_data['api_key'] and config_data['api_key'] != '****':
                self.api_key = config_data['api_key']
                self.config['api_key'] = config_data['api_key']
            
            # Reinitialize client with new configuration
            if self.config.get('enabled', False) and self.base_url and self.api_key:
                self._initialize_client()
            
            self.logger.info(f"Configuration updated for {self.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request to Paperless-NGX API"""
        url = urljoin(self.base_url, endpoint)
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise PluginError(f"Paperless-NGX API request failed: {str(e)}")
    
    def get_documents(self, page: int = 1, page_size: int = 25, search: str = None) -> Dict[str, Any]:
        """Get documents from Paperless-NGX"""
        params = {
            'page': page,
            'page_size': page_size,
            'ordering': '-created'
        }
        
        if search:
            params['search'] = search
        
        try:
            response = self._make_request('GET', '/api/documents/', params=params)
            data = response.json()
            
            # Process documents to include additional info
            documents = []
            for doc in data.get('results', []):
                processed_doc = self._process_document(doc)
                documents.append(processed_doc)
            
            return {
                'documents': documents,
                'count': data.get('count', 0),
                'next': data.get('next'),
                'previous': data.get('previous'),
                'page': page,
                'page_size': page_size,
                'total_pages': (data.get('count', 0) + page_size - 1) // page_size
            }
        except Exception as e:
            self.logger.error(f"Failed to fetch documents: {str(e)}")
            raise PluginError(f"Failed to fetch documents from Paperless-NGX: {str(e)}")
    
    def get_document(self, doc_id: int) -> Dict[str, Any]:
        """Get a specific document by ID"""
        try:
            response = self._make_request('GET', f'/api/documents/{doc_id}/')
            doc = response.json()
            return self._process_document(doc)
        except Exception as e:
            self.logger.error(f"Failed to fetch document {doc_id}: {str(e)}")
            raise PluginError(f"Failed to fetch document {doc_id}: {str(e)}")
    
    def get_document_content(self, doc_id: int) -> str:
        """Get OCR content of a document"""
        try:
            response = self._make_request('GET', f'/api/documents/{doc_id}/content/')
            return response.text
        except Exception as e:
            self.logger.error(f"Failed to fetch document content for {doc_id}: {str(e)}")
            raise PluginError(f"Failed to fetch document content: {str(e)}")
    
    def get_document_download_url(self, doc_id: int) -> str:
        """Get download URL for a document"""
        return f"{self.base_url}/api/documents/{doc_id}/download/"
    
    def get_document_preview_url(self, doc_id: int) -> str:
        """Get preview URL for a document"""
        return f"{self.base_url}/documents/{doc_id}/preview/"
    
    def upload_document(self, file_path: str, title: str = None, correspondent: str = None, 
                       document_type: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """Upload a document to Paperless-NGX"""
        try:
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {}
                
                if title:
                    data['title'] = title
                if correspondent:
                    data['correspondent'] = correspondent
                if document_type:
                    data['document_type'] = document_type
                if tags:
                    data['tags'] = tags
                
                response = self._make_request('POST', '/api/documents/post_document/', 
                                            files=files, data=data)
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to upload document: {str(e)}")
            raise PluginError(f"Failed to upload document to Paperless-NGX: {str(e)}")
    
    def get_correspondents(self) -> List[Dict[str, Any]]:
        """Get all correspondents"""
        try:
            response = self._make_request('GET', '/api/correspondents/')
            return response.json().get('results', [])
        except Exception as e:
            self.logger.error(f"Failed to fetch correspondents: {str(e)}")
            return []
    
    def get_document_types(self) -> List[Dict[str, Any]]:
        """Get all document types"""
        try:
            response = self._make_request('GET', '/api/document_types/')
            return response.json().get('results', [])
        except Exception as e:
            self.logger.error(f"Failed to fetch document types: {str(e)}")
            return []
    
    def get_tags(self) -> List[Dict[str, Any]]:
        """Get all tags"""
        try:
            response = self._make_request('GET', '/api/tags/')
            return response.json().get('results', [])
        except Exception as e:
            self.logger.error(f"Failed to fetch tags: {str(e)}")
            return []
    
    def _process_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Process document data to include additional information"""
        processed = doc.copy()
        
        # Add formatted dates
        if 'created' in doc:
            try:
                created_date = datetime.fromisoformat(doc['created'].replace('Z', '+00:00'))
                processed['created_formatted'] = created_date.strftime('%Y-%m-%d %H:%M')
                processed['created_date'] = created_date.date()
            except:
                processed['created_formatted'] = doc['created']
                processed['created_date'] = None
        
        # Add URLs
        processed['download_url'] = self.get_document_download_url(doc['id'])
        processed['preview_url'] = self.get_document_preview_url(doc['id'])
        
        # Process correspondent
        if 'correspondent' in doc and doc['correspondent']:
            correspondent_name = self._get_correspondent_name(doc['correspondent'])
            processed['correspondent_name'] = correspondent_name
        else:
            processed['correspondent_name'] = 'None'
        
        # Process document type
        if 'document_type' in doc and doc['document_type']:
            doc_type_name = self._get_document_type_name(doc['document_type'])
            processed['document_type_name'] = doc_type_name
        else:
            processed['document_type_name'] = 'None'
        
        # Process tags
        if 'tags' in doc and doc['tags']:
            tag_names = [self._get_tag_name(tag_id) for tag_id in doc['tags']]
            processed['tag_names'] = tag_names
        else:
            processed['tag_names'] = []
        
        return processed
    
    def _get_correspondent_name(self, correspondent_id: int) -> str:
        """Get correspondent name by ID"""
        try:
            response = self._make_request('GET', f'/api/correspondents/{correspondent_id}/')
            return response.json().get('name', f'Correspondent {correspondent_id}')
        except:
            return f'Correspondent {correspondent_id}'
    
    def _get_document_type_name(self, doc_type_id: int) -> str:
        """Get document type name by ID"""
        try:
            response = self._make_request('GET', f'/api/document_types/{doc_type_id}/')
            return response.json().get('name', f'Type {doc_type_id}')
        except:
            return f'Type {doc_type_id}'
    
    def _get_tag_name(self, tag_id: int) -> str:
        """Get tag name by ID"""
        try:
            response = self._make_request('GET', f'/api/tags/{tag_id}/')
            return response.json().get('name', f'Tag {tag_id}')
        except:
            return f'Tag {tag_id}'
    
    def get_capabilities(self) -> List[str]:
        """Return list of plugin capabilities"""
        return [
            'document_management',
            'document_search',
            'document_upload',
            'document_download',
            'ocr_content',
            'metadata_management'
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status and health information"""
        try:
            # Test API connection
            response = self._make_request('GET', '/api/documents/', params={'page_size': 1})
            doc_count = response.json().get('count', 0)
            
            return {
                'status': 'healthy',
                'connected': True,
                'base_url': self.base_url,
                'document_count': doc_count,
                'version': self.version,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'connected': False,
                'base_url': self.base_url,
                'error': str(e),
                'version': self.version,
                'last_check': datetime.now().isoformat()
            }
    
    def get_menu_items(self) -> List[Dict[str, str]]:
        """Get menu items for web interface"""
        return [
            {
                'name': 'Paperless-NGX Documents',
                'url': '/paperless-ngx/documents',
                'icon': 'fa-file-invoice',
                'description': 'Browse and search Paperless-NGX documents'
            }
        ]
    
    def get_web_routes(self) -> List[Dict[str, Any]]:
        """Get web routes provided by this plugin"""
        return [
            {
                'endpoint': 'paperless_ngx_documents',
                'url': '/paperless-ngx/documents',
                'methods': ['GET'],
                'description': 'List Paperless-NGX documents'
            },
            {
                'endpoint': 'paperless_ngx_document_content',
                'url': '/paperless-ngx/document/<int:doc_id>/content',
                'methods': ['GET'],
                'description': 'View document OCR content'
            },
            {
                'endpoint': 'paperless_ngx_document_detail',
                'url': '/paperless-ngx/document/<int:doc_id>',
                'methods': ['GET'],
                'description': 'Get document details (API)'
            }
        ]


class PaperlessNGXProcessingPlugin(ProcessingPlugin):
    """Processing plugin for Paperless-NGX integration"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("paperless_ngx_processing", "1.0.0")
        self.config = config
        self.paperless_plugin = PaperlessNGXPlugin(config)
    
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """Initialize the processing plugin"""
        try:
            # Create the main plugin instance
            self.paperless_plugin = PaperlessNGXPlugin(self.config)
            return self.paperless_plugin.initialize(app_context)
        except Exception as e:
            self.logger.error(f"Failed to initialize Paperless-NGX processing plugin: {str(e)}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup processing plugin resources"""
        if self.paperless_plugin:
            return self.paperless_plugin.cleanup()
        return True
    
    def process_document(self, document_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process and upload document to Paperless-NGX"""
        try:
            # Extract metadata for upload
            title = metadata.get('title') if metadata else None
            correspondent = metadata.get('correspondent') if metadata else None
            document_type = metadata.get('document_type') if metadata else None
            tags = metadata.get('tags', []) if metadata else []
            
            # Upload to Paperless-NGX
            result = self.paperless_plugin.upload_document(
                document_path, title, correspondent, document_type, tags
            )
            
            return {
                'success': True,
                'document_id': result.get('id'),
                'message': f"Document uploaded to Paperless-NGX successfully",
                'paperless_data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to upload document to Paperless-NGX: {str(e)}"
            }


def create_plugin(config: Dict[str, Any]) -> PaperlessNGXPlugin:
    """Factory function to create plugin instance"""
    return PaperlessNGXPlugin(config)


def create_processing_plugin(config: Dict[str, Any]) -> PaperlessNGXProcessingPlugin:
    """Factory function to create processing plugin instance"""
    return PaperlessNGXProcessingPlugin(config)
