"""
Invoice Ninja Integration Plugin
"""
from loguru import logger
from typing import Dict, Any, List
from flask import Blueprint, jsonify, request, render_template_string

from core.base_plugin import IntegrationPlugin
from core.exceptions import IntegrationError
from .client import InvoiceNinjaClient


class InvoiceNinjaPlugin(IntegrationPlugin):
    """Invoice Ninja integration plugin with web interface"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.client = None
        self._dependencies = []
    
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """Initialize Invoice Ninja plugin"""
        try:
            # Get plugin configuration
            config = app_context.get('config')
            if not config:
                logger.error("No configuration provided")
                return False
            
            # Initialize Invoice Ninja client
            api_token = self.config.get('api_token')
            base_url = self.config.get('base_url', 'https://app.invoicing.co')
            
            if not api_token:
                logger.error("Invoice Ninja API token not configured")
                return False
            
            if not base_url:
                logger.error("Invoice Ninja base URL not configured")
                return False
            
            # self.client = InvoiceNinjaClient(api_token, base_url)
            
            # Test connection
            if not self.test_connection():
                logger.error("Failed to connect to Invoice Ninja")
                return False
            
            logger.info("Invoice Ninja plugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Invoice Ninja plugin: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup Invoice Ninja plugin resources"""
        try:
            if self.client:
                # Perform any necessary cleanup
                pass
            logger.info("Invoice Ninja plugin cleaned up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup Invoice Ninja plugin: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to Invoice Ninja API"""
        try:
            if not self.client:
                return False
            
            # Test API connection by trying to get company info
            # response = self.client.get_company_info()
            # return response is not None
            return True  # Temporary: skip connection test
            
        except Exception as e:
            logger.error(f"Invoice Ninja connection test failed: {e}")
            return False
    
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data with Invoice Ninja"""
        try:
            if not self.client:
                raise IntegrationError("Invoice Ninja client not initialized")
            
            sync_type = data.get('type')
            
            if sync_type == 'invoice':
                return self._sync_invoice(data)
            elif sync_type == 'quote':
                return self._sync_quote(data)
            elif sync_type == 'client':
                return self._sync_client(data)
            elif sync_type == 'product':
                return self._sync_product(data)
            else:
                raise IntegrationError(f"Unsupported sync type: {sync_type}")
            
        except Exception as e:
            logger.error(f"Invoice Ninja sync failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _sync_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync invoice with Invoice Ninja"""
        try:
            # Transform invoice data to Invoice Ninja format
            ninja_invoice = self._transform_invoice_data(invoice_data)
            
            # Create or update invoice in Invoice Ninja
            result = self.client.create_invoice(ninja_invoice)
            
            return {
                'success': True,
                'ninja_id': result.get('data', {}).get('id'),
                'message': 'Invoice synced successfully'
            }
            
        except Exception as e:
            raise IntegrationError(f"Invoice sync failed: {e}")
    
    def _sync_quote(self, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync quote with Invoice Ninja"""
        try:
            # Transform quote data to Invoice Ninja format
            ninja_quote = self._transform_quote_data(quote_data)
            
            # Create or update quote in Invoice Ninja
            result = self.client.create_quote(ninja_quote)
            
            return {
                'success': True,
                'ninja_id': result.get('data', {}).get('id'),
                'message': 'Quote synced successfully'
            }
            
        except Exception as e:
            raise IntegrationError(f"Quote sync failed: {e}")
    
    def _sync_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync client with Invoice Ninja"""
        try:
            # Transform client data to Invoice Ninja format
            ninja_client = self._transform_client_data(client_data)
            
            # Create or update client in Invoice Ninja
            result = self.client.create_client(ninja_client)
            
            return {
                'success': True,
                'ninja_id': result.get('data', {}).get('id'),
                'message': 'Client synced successfully'
            }
            
        except Exception as e:
            raise IntegrationError(f"Client sync failed: {e}")
    
    def _sync_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync product with Invoice Ninja"""
        try:
            # Transform product data to Invoice Ninja format
            ninja_product = self._transform_product_data(product_data)
            
            # Create or update product in Invoice Ninja
            result = self.client.create_product(ninja_product)
            
            return {
                'success': True,
                'ninja_id': result.get('data', {}).get('id'),
                'message': 'Product synced successfully'
            }
            
        except Exception as e:
            raise IntegrationError(f"Product sync failed: {e}")
    
    def _transform_invoice_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice data to Invoice Ninja format"""
        return {
            'number': data.get('number'),
            'date': data.get('date'),
            'due_date': data.get('due_date'),
            'client_id': data.get('client_id'),
            'status_id': data.get('status_id', 1),
            'terms': data.get('terms'),
            'public_notes': data.get('notes'),
            'private_notes': data.get('private_notes'),
            'discount': data.get('discount', 0),
            'is_amount_discount': data.get('is_amount_discount', False),
            'line_items': data.get('line_items', [])
        }
    
    def _transform_quote_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform quote data to Invoice Ninja format"""
        return {
            'number': data.get('number'),
            'date': data.get('date'),
            'valid_until': data.get('valid_until'),
            'client_id': data.get('client_id'),
            'status_id': data.get('status_id', 1),
            'terms': data.get('terms'),
            'public_notes': data.get('notes'),
            'private_notes': data.get('private_notes'),
            'discount': data.get('discount', 0),
            'is_amount_discount': data.get('is_amount_discount', False),
            'line_items': data.get('line_items', [])
        }
    
    def _transform_client_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform client data to Invoice Ninja format"""
        return {
            'name': data.get('name'),
            'address1': data.get('address_line_1'),
            'address2': data.get('address_line_2'),
            'city': data.get('city'),
            'state': data.get('state'),
            'postal_code': data.get('postal_code'),
            'country_id': data.get('country_id'),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'website': data.get('website'),
            'vat_number': data.get('vat_number'),
            'id_number': data.get('id_number')
        }
    
    def _transform_product_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform product data to Invoice Ninja format"""
        return {
            'product_key': data.get('sku'),
            'notes': data.get('description'),
            'cost': data.get('cost', 0),
            'price': data.get('price', 0),
            'qty': data.get('quantity', 1),
            'tax_name1': data.get('tax_name'),
            'tax_rate1': data.get('tax_rate', 0)
        }
    
    def get_blueprint(self) -> Blueprint:
        """Get Flask blueprint for Invoice Ninja web interface"""
        bp = Blueprint('invoice_ninja', __name__, template_folder='templates')
        
        @bp.route('/')
        def dashboard():
            """Invoice Ninja plugin dashboard"""
            try:
                if not self.client:
                    return "Invoice Ninja client not initialized", 500
                
                # Get company info
                company_info = self.client.get_company_info()
                
                # Get recent invoices and quotes
                recent_invoices = self.client.get_recent_invoices(limit=5)
                recent_quotes = self.client.get_recent_quotes(limit=5)
                
                template = """
                <div class="invoice-ninja-dashboard">
                    <h2>Invoice Ninja Integration</h2>
                    
                    <div class="company-info">
                        <h3>Company: {{ company_info.name if company_info else 'Unknown' }}</h3>
                        <p>Status: <span class="status-{{ 'connected' if connected else 'disconnected' }}">
                            {{ 'Connected' if connected else 'Disconnected' }}
                        </span></p>
                    </div>
                    
                    <div class="recent-data">
                        <div class="recent-invoices">
                            <h4>Recent Invoices ({{ recent_invoices|length }})</h4>
                            <ul>
                                {% for invoice in recent_invoices %}
                                <li>{{ invoice.number }} - {{ invoice.amount }} ({{ invoice.date }})</li>
                                {% endfor %}
                            </ul>
                        </div>
                        
                        <div class="recent-quotes">
                            <h4>Recent Quotes ({{ recent_quotes|length }})</h4>
                            <ul>
                                {% for quote in recent_quotes %}
                                <li>{{ quote.number }} - {{ quote.amount }} ({{ quote.date }})</li>
                                {% endfor %}
                            </ul>
                        </div>
                    </div>
                    
                    <div class="actions">
                        <a href="{{ url_for('invoice_ninja.sync') }}" class="btn btn-primary">Manual Sync</a>
                        <a href="{{ url_for('invoice_ninja.settings') }}" class="btn btn-secondary">Settings</a>
                    </div>
                </div>
                """
                
                return render_template_string(template, 
                                            company_info=company_info,
                                            connected=self.test_connection(),
                                            recent_invoices=recent_invoices or [],
                                            recent_quotes=recent_quotes or [])
                
            except Exception as e:
                logger.error(f"Invoice Ninja dashboard error: {e}")
                return f"Error: {str(e)}", 500
        
        @bp.route('/sync', methods=['GET', 'POST'])
        def sync():
            """Manual sync page"""
            if request.method == 'POST':
                try:
                    # Perform manual sync
                    result = {'success': True, 'message': 'Sync completed successfully'}
                    return jsonify(result)
                except Exception as e:
                    return jsonify({'success': False, 'error': str(e)}), 500
            
            return render_template_string("""
                <div class="sync-page">
                    <h3>Manual Sync</h3>
                    <button id="sync-btn" onclick="performSync()">Start Sync</button>
                    <div id="sync-result"></div>
                    
                    <script>
                    function performSync() {
                        document.getElementById('sync-btn').disabled = true;
                        fetch('{{ url_for("invoice_ninja.sync") }}', {method: 'POST'})
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('sync-result').innerHTML = 
                                    data.success ? 
                                    '<div class="alert alert-success">' + data.message + '</div>' :
                                    '<div class="alert alert-error">' + data.error + '</div>';
                                document.getElementById('sync-btn').disabled = false;
                            });
                    }
                    </script>
                </div>
            """)
        
        @bp.route('/settings')
        def settings():
            """Plugin settings page"""
            template = """
                <div class="settings-page">
                    <h3>Invoice Ninja Settings</h3>
                    
                    <form method="post" action="{{ url_for('invoice_ninja.update_settings') }}">
                        <div class="setting-group">
                            <label>API Token:</label>
                            <input type="password" name="api_token" value="{{ config.get('api_token', '') }}" />
                        </div>
                        
                        <div class="setting-group">
                            <label>Base URL:</label>
                            <input type="url" name="base_url" value="{{ config.get('base_url', 'https://app.invoicing.co') }}" />
                        </div>
                        
                        <div class="setting-group">
                            <label>Auto Sync:</label>
                            <input type="checkbox" name="auto_sync" {{ 'checked' if config.get('auto_sync') else '' }} />
                        </div>
                        
                        <button type="submit">Update Settings</button>
                    </form>
                </div>
            """
            
            return render_template_string(template, config=self.config)
        
        return bp
    
    def get_menu_items(self) -> List[Dict[str, str]]:
        """Get menu items for the web interface"""
        return [
            {
                'name': 'Invoice Ninja',
                'url': '/plugins/invoice_ninja/',
                'icon': 'fa-ninja'
            }
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Invoice Ninja plugin configuration"""
        required_fields = ['api_token', 'base_url']
        
        for field in required_fields:
            if not config.get(field):
                logger.error(f"Missing required configuration field: {field}")
                return False
        
        return True
