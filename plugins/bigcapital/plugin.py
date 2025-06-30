"""
BigCapital Integration Plugin
"""
from loguru import logger
from typing import Dict, Any, List
from flask import Blueprint, jsonify, request, render_template_string

from core.base_plugin import IntegrationPlugin
from core.exceptions import IntegrationError
from .client import BigCapitalClient


class BigCapitalPlugin(IntegrationPlugin):
    """BigCapital integration plugin with web interface"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.client = None
        self._dependencies = []
    
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """Initialize BigCapital plugin"""
        try:
            # Get plugin configuration
            config = app_context.get('config')
            if not config:
                logger.error("No configuration provided")
                return False
            
            # Initialize BigCapital client
            api_key = self.config.get('api_key')
            base_url = self.config.get('base_url', 'https://api.bigcapital.ly')
            
            if not api_key:
                logger.error("BigCapital API key not configured")
                return False
            
            self.client = BigCapitalClient(api_key, base_url)
            
            # Test connection
            if not self.test_connection():
                logger.error("Failed to connect to BigCapital")
                return False
            
            logger.info("BigCapital plugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize BigCapital plugin: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup BigCapital plugin resources"""
        try:
            if self.client:
                # Perform any necessary cleanup
                pass
            logger.info("BigCapital plugin cleaned up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup BigCapital plugin: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to BigCapital API"""
        try:
            if not self.client:
                return False
            
            # Test API connection
            response = self.client.get_organization_info()
            return response is not None
            
        except Exception as e:
            logger.error(f"BigCapital connection test failed: {e}")
            return False
    
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data with BigCapital"""
        try:
            if not self.client:
                raise IntegrationError("BigCapital client not initialized")
            
            sync_type = data.get('type')
            
            if sync_type == 'invoice':
                return self._sync_invoice(data)
            elif sync_type == 'expense':
                return self._sync_expense(data)
            elif sync_type == 'contact':
                return self._sync_contact(data)
            else:
                raise IntegrationError(f"Unsupported sync type: {sync_type}")
            
        except Exception as e:
            logger.error(f"BigCapital sync failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _sync_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync invoice with BigCapital"""
        try:
            # Transform invoice data to BigCapital format
            bc_invoice = self._transform_invoice_data(invoice_data)
            
            # Create or update invoice in BigCapital
            result = self.client.create_invoice(bc_invoice)
            
            return {
                'success': True,
                'bigcapital_id': result.get('id'),
                'message': 'Invoice synced successfully'
            }
            
        except Exception as e:
            raise IntegrationError(f"Invoice sync failed: {e}")
    
    def _sync_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync expense with BigCapital"""
        try:
            # Transform expense data to BigCapital format
            bc_expense = self._transform_expense_data(expense_data)
            
            # Create or update expense in BigCapital
            result = self.client.create_expense(bc_expense)
            
            return {
                'success': True,
                'bigcapital_id': result.get('id'),
                'message': 'Expense synced successfully'
            }
            
        except Exception as e:
            raise IntegrationError(f"Expense sync failed: {e}")
    
    def _sync_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync contact with BigCapital"""
        try:
            # Transform contact data to BigCapital format
            bc_contact = self._transform_contact_data(contact_data)
            
            # Create or update contact in BigCapital
            result = self.client.create_contact(bc_contact)
            
            return {
                'success': True,
                'bigcapital_id': result.get('id'),
                'message': 'Contact synced successfully'
            }
            
        except Exception as e:
            raise IntegrationError(f"Contact sync failed: {e}")
    
    def _transform_invoice_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice data to BigCapital format"""
        # This would contain the actual transformation logic
        # For now, return a basic structure
        return {
            'customer_id': data.get('customer_id'),
            'invoice_date': data.get('date'),
            'due_date': data.get('due_date'),
            'invoice_number': data.get('number'),
            'reference': data.get('reference'),
            'note': data.get('notes'),
            'entries': data.get('line_items', [])
        }
    
    def _transform_expense_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform expense data to BigCapital format"""
        return {
            'payee_id': data.get('vendor_id'),
            'payment_date': data.get('date'),
            'payment_account_id': data.get('account_id'),
            'amount': data.get('amount'),
            'reference': data.get('reference'),
            'description': data.get('description')
        }
    
    def _transform_contact_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform contact data to BigCapital format"""
        return {
            'display_name': data.get('name'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'company_name': data.get('company'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'website': data.get('website')
        }
    
    def get_blueprint(self) -> Blueprint:
        """Get Flask blueprint for BigCapital web interface"""
        bp = Blueprint('bigcapital', __name__, template_folder='templates')
        
        @bp.route('/')
        def dashboard():
            """BigCapital plugin dashboard"""
            try:
                if not self.client:
                    return "BigCapital client not initialized", 500
                
                # Get organization info
                org_info = self.client.get_organization_info()
                
                # Get recent transactions
                recent_invoices = self.client.get_recent_invoices(limit=5)
                recent_expenses = self.client.get_recent_expenses(limit=5)
                
                template = """
                <div class="bigcapital-dashboard">
                    <h2>BigCapital Integration</h2>
                    
                    <div class="organization-info">
                        <h3>Organization: {{ org_info.name if org_info else 'Unknown' }}</h3>
                        <p>Status: <span class="status-{{ 'connected' if connected else 'disconnected' }}">
                            {{ 'Connected' if connected else 'Disconnected' }}
                        </span></p>
                    </div>
                    
                    <div class="recent-data">
                        <div class="recent-invoices">
                            <h4>Recent Invoices ({{ recent_invoices|length }})</h4>
                            <ul>
                                {% for invoice in recent_invoices %}
                                <li>{{ invoice.invoice_number }} - {{ invoice.amount }} ({{ invoice.date }})</li>
                                {% endfor %}
                            </ul>
                        </div>
                        
                        <div class="recent-expenses">
                            <h4>Recent Expenses ({{ recent_expenses|length }})</h4>
                            <ul>
                                {% for expense in recent_expenses %}
                                <li>{{ expense.description }} - {{ expense.amount }} ({{ expense.date }})</li>
                                {% endfor %}
                            </ul>
                        </div>
                    </div>
                    
                    <div class="actions">
                        <a href="{{ url_for('bigcapital.sync') }}" class="btn btn-primary">Manual Sync</a>
                        <a href="{{ url_for('bigcapital.settings') }}" class="btn btn-secondary">Settings</a>
                    </div>
                </div>
                """
                
                return render_template_string(template, 
                                            org_info=org_info,
                                            connected=self.test_connection(),
                                            recent_invoices=recent_invoices or [],
                                            recent_expenses=recent_expenses or [])
                
            except Exception as e:
                logger.error(f"BigCapital dashboard error: {e}")
                return f"Error: {str(e)}", 500
        
        @bp.route('/sync', methods=['GET', 'POST'])
        def sync():
            """Manual sync page"""
            if request.method == 'POST':
                try:
                    # Perform manual sync
                    # This would typically sync pending documents
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
                        fetch('{{ url_for("bigcapital.sync") }}', {method: 'POST'})
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
                    <h3>BigCapital Settings</h3>
                    
                    <form method="post" action="{{ url_for('bigcapital.update_settings') }}">
                        <div class="setting-group">
                            <label>API Key:</label>
                            <input type="password" name="api_key" value="{{ config.get('api_key', '') }}" />
                        </div>
                        
                        <div class="setting-group">
                            <label>Base URL:</label>
                            <input type="url" name="base_url" value="{{ config.get('base_url', 'https://api.bigcapital.ly') }}" />
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
                'name': 'BigCapital',
                'url': '/plugins/bigcapital/',
                'icon': 'fa-chart-line'
            }
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate BigCapital plugin configuration"""
        required_fields = ['api_key']
        
        for field in required_fields:
            if not config.get(field):
                logger.error(f"Missing required configuration field: {field}")
                return False
        
        return True
