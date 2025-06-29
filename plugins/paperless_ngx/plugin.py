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

    def test_connection_with_config(self, test_config=None):
        """Test connection with current or provided configuration"""
        try:
            # Use test configuration if provided
            if test_config:
                base_url = test_config.get('base_url', self.base_url)
                api_key = test_config.get('api_key', self.api_key)
            else:
                base_url = self.base_url
                api_key = self.api_key
            
            if not base_url or not api_key:
                return False
            
            import requests
            
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
                verify=self.config.get('verify_ssl', True)
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
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
            self.session.verify = self.config.get('verify_ssl', True)
            
            self.logger.info("Paperless-NGX API client initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize API client: {e}")
            return False

    # ...existing code...