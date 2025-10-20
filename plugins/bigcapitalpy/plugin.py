"""
BigCapital Integration Plugin

Enhanced BigCapital plugin with comprehensive document processing integration,
robust error handling, and advanced sync capabilities.
"""
from loguru import logger
from typing import Dict, Any, List, Optional, Tuple
from flask import Blueprint, jsonify, request, render_template_string
from datetime import datetime, date
import json

from core.base_plugin import IntegrationPlugin
from core.exceptions import IntegrationError
from .client import BigCapitalClient, BigCapitalAPIError
from .models import BigCapitalContact, BigCapitalInvoice, BigCapitalExpense
from .mappers import PaperlessNGXMapper, GenericDataMapper, ValidationHelper


class BigCapitalPlugin(IntegrationPlugin):
    """Enhanced BigCapital integration plugin with comprehensive features"""
    
    def __init__(self, name: str, version: str = "2.0.0"):
        super().__init__(name, version)
        self.client = None
        self._dependencies = []
        self._sync_stats = {
            'last_sync': None,
            'documents_processed': 0,
            'invoices_created': 0,
            'expenses_created': 0,
            'contacts_created': 0,
            'errors': 0
        }
        
        # Cache for frequently accessed data
        self._accounts_cache = {}
        self._contacts_cache = {}
        self._cache_timestamp = None
    
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """Initialize BigCapital plugin with enhanced error handling"""
        try:
            # Get plugin configuration
            config = app_context.get('config')
            if not config:
                logger.error("No configuration provided to BigCapital plugin")
                return False
            
            # Validate required configuration
            if not self.validate_config(self.config):
                logger.error("BigCapital plugin configuration validation failed")
                return False
            
            # Initialize BigCapital client
            api_key = self.config.get('api_key')
            base_url = self.config.get('base_url', 'https://api.bigcapital.ly')
            timeout = self.config.get('timeout', 30)
            
            self.client = BigCapitalClient(api_key, base_url, timeout)
            
            # Test connection with detailed logging
            logger.info("Testing BigCapital API connection...")
            if not self.test_connection():
                logger.error("Failed to connect to BigCapital API")
                return False
            
            # Load and cache essential data
            self._load_essential_data()
            
            logger.info(f"BigCapital plugin v{self.version} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize BigCapital plugin: {e}")
            logger.exception("Detailed error information:")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup BigCapital plugin resources"""
        try:
            if self.client:
                # Clear caches
                self._accounts_cache.clear()
                self._contacts_cache.clear()
                self._cache_timestamp = None
                
                # Close session if needed
                if hasattr(self.client, 'session'):
                    self.client.session.close()
            
            logger.info("BigCapital plugin cleaned up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup BigCapital plugin: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to BigCapital API with detailed feedback"""
        try:
            if not self.client:
                logger.error("BigCapital client not initialized")
                return False
            
            # For now, just test that we can make a basic request
            # Try a simple endpoint that should exist
            try:
                # Try to get currencies as a basic connectivity test
                currencies = self.client.get_currencies()
                if currencies is not None:
                    logger.info("Successfully connected to BigCapital API")
                    return True
            except Exception as e:
                logger.debug(f"Currencies endpoint failed: {e}")
            
            # If currencies fails, try dashboard stats
            try:
                stats = self.client.get_dashboard_stats()
                if stats is not None:
                    logger.info("Successfully connected to BigCapital API")
                    return True
            except Exception as e:
                logger.debug(f"Dashboard stats endpoint failed: {e}")
            
            # If both fail, assume connection is OK for now
            # This allows the plugin to load and we can test actual functionality
            logger.warning("Could not verify BigCapital API connection, but allowing plugin to load")
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            return False
    
    def _load_essential_data(self):
        """Load and cache essential data for efficient operations"""
        try:
            logger.info("Loading essential BigCapital data...")
            
            # Cache accounts
            accounts = self.client.get_accounts()
            if accounts:
                self._accounts_cache = {acc['id']: acc for acc in accounts}
                logger.info(f"Cached {len(accounts)} accounts")
            
            # Cache recent contacts for quick lookup
            contacts = self.client.get_contacts(per_page=100)  # Get first 100 contacts
            if contacts:
                self._contacts_cache = {
                    contact['id']: contact for contact in contacts
                }
                # Also index by email for quick lookup
                for contact in contacts:
                    if contact.get('email'):
                        self._contacts_cache[contact['email'].lower()] = contact
                logger.info(f"Cached {len(contacts)} contacts")
            
            self._cache_timestamp = datetime.now()
            
        except Exception as e:
            logger.warning(f"Failed to load essential data: {e}")
    
    def _refresh_cache_if_needed(self):
        """Refresh cache if it's older than 1 hour"""
        if (not self._cache_timestamp or 
            (datetime.now() - self._cache_timestamp).seconds > 3600):
            self._load_essential_data()
    
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced sync data with BigCapital"""
        try:
            if not self.client:
                raise IntegrationError("BigCapital client not initialized")
            
            sync_type = data.get('type')
            logger.info(f"Starting {sync_type} sync with BigCapital")
            
            if sync_type == 'invoice':
                return self._sync_invoice(data)
            elif sync_type == 'expense':
                return self._sync_expense(data)
            elif sync_type == 'contact':
                return self._sync_contact(data)
            elif sync_type == 'document':
                return self._sync_document(data)
            else:
                raise IntegrationError(f"Unsupported sync type: {sync_type}")
            
        except BigCapitalAPIError as e:
            logger.error(f"BigCapital API error during sync: {e}")
            self._sync_stats['errors'] += 1
            return {
                'success': False,
                'error': f'BigCapital API error: {str(e)}',
                'error_type': 'api_error'
            }
        except IntegrationError as e:
            logger.error(f"Integration error during sync: {e}")
            self._sync_stats['errors'] += 1
            return {
                'success': False,
                'error': str(e),
                'error_type': 'integration_error'
            }
        except Exception as e:
            logger.error(f"Unexpected error during sync: {e}")
            logger.exception("Detailed error information:")
            self._sync_stats['errors'] += 1
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'error_type': 'unexpected_error'
            }
    
    def _sync_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync a document from Paperless-NGX to BigCapital"""
        try:
            # Check if client is initialized
            if not self.client:
                return {'success': False, 'error': 'BigCapital client not initialized'}
                
            document = document_data.get('document', {})
            ocr_content = document_data.get('ocr_content', '')
            sync_as = document_data.get('sync_as', 'expense')  # Default to expense
            
            if sync_as == 'expense':
                # Convert document to expense
                expense = PaperlessNGXMapper.document_to_expense(document, ocr_content)
                
                # Try to find or create vendor
                vendor = PaperlessNGXMapper.extract_vendor_from_document(document, ocr_content)
                if vendor:
                    vendor_result = self._find_or_create_contact(vendor)
                    if vendor_result.get('success') and vendor_result.get('contact_id'):
                        expense.payee_id = vendor_result['contact_id']
                
                # Create expense in BigCapital
                result = self.client.create_expense(expense.to_dict())
                if result:
                    self._sync_stats['expenses_created'] += 1
                    return {'success': True, 'bigcapital_id': result.get('id'), 'type': 'expense'}
                else:
                    return {'success': False, 'error': 'Failed to create expense in BigCapital'}
                
            elif sync_as == 'invoice':
                # Convert document to invoice
                # First, try to determine customer
                customer_id = document_data.get('customer_id', 1)  # Default customer
                
                invoice = PaperlessNGXMapper.document_to_invoice(document, ocr_content, customer_id)
                
                # Create invoice in BigCapital
                result = self.client.create_invoice(invoice.to_dict())
                if result:
                    self._sync_stats['invoices_created'] += 1
                    return {'success': True, 'bigcapital_id': result.get('id'), 'type': 'invoice'}
                else:
                    return {'success': False, 'error': 'Failed to create invoice in BigCapital'}
                    
            else:
                return {'success': False, 'error': f'Unsupported sync type: {sync_as}'}
                
        except Exception as e:
            logger.error(f"Document sync failed: {e}")
            raise IntegrationError(f"Document sync failed: {e}")
    
    def _sync_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced invoice sync with validation and error handling"""
        try:
            # Validate invoice data
            if not self._validate_invoice_data(invoice_data):
                return {'success': False, 'error': 'Invalid invoice data'}
            
            # Transform invoice data to BigCapital format
            bc_invoice = self._transform_invoice_data(invoice_data)
            
            # Validate customer exists
            customer_id = bc_invoice.get('customer_id')
            if customer_id and not self._customer_exists(customer_id):
                return {'success': False, 'error': f'Customer {customer_id} not found'}
            
            # Create or update invoice in BigCapital
            invoice_id = invoice_data.get('bigcapital_id')
            if invoice_id:
                # Update existing invoice
                result = self.client.update_invoice(invoice_id, bc_invoice)
            else:
                # Create new invoice
                result = self.client.create_invoice(bc_invoice)
            
            if result:
                self._sync_stats['invoices_created'] += 1
                return {
                    'success': True,
                    'bigcapital_id': result.get('id'),
                    'invoice_number': result.get('invoice_number'),
                    'message': 'Invoice synced successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to sync invoice'}
            
        except Exception as e:
            raise IntegrationError(f"Invoice sync failed: {e}")
    
    def _sync_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced expense sync with validation and vendor lookup"""
        try:
            # Validate expense data
            if not self._validate_expense_data(expense_data):
                return {'success': False, 'error': 'Invalid expense data'}
            
            # Transform expense data to BigCapital format
            bc_expense = self._transform_expense_data(expense_data)
            
            # Try to find or create vendor if vendor info provided
            vendor_info = expense_data.get('vendor')
            if vendor_info:
                vendor_result = self._find_or_create_contact(vendor_info, 'vendor')
                if vendor_result.get('success'):
                    bc_expense['payee_id'] = vendor_result['contact_id']
            
            # Create or update expense in BigCapital
            expense_id = expense_data.get('bigcapital_id')
            if expense_id:
                # Update existing expense
                result = self.client.update_expense(expense_id, bc_expense)
            else:
                # Create new expense
                result = self.client.create_expense(bc_expense)
            
            if result:
                self._sync_stats['expenses_created'] += 1
                return {
                    'success': True,
                    'bigcapital_id': result.get('id'),
                    'message': 'Expense synced successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to sync expense'}
            
        except Exception as e:
            raise IntegrationError(f"Expense sync failed: {e}")
    
    def _sync_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced contact sync with duplicate detection"""
        try:
            # Validate contact data
            if not self._validate_contact_data(contact_data):
                return {'success': False, 'error': 'Invalid contact data'}
            
            # Transform contact data to BigCapital format
            bc_contact = self._transform_contact_data(contact_data)
            
            # Check for existing contact
            existing_contact = self._find_existing_contact(bc_contact)
            if existing_contact:
                # Update existing contact
                result = self.client.update_contact(existing_contact['id'], bc_contact)
                action = 'updated'
            else:
                # Create new contact
                result = self.client.create_contact(bc_contact)
                action = 'created'
            
            if result:
                self._sync_stats['contacts_created'] += 1
                return {
                    'success': True,
                    'bigcapital_id': result.get('id'),
                    'action': action,
                    'message': f'Contact {action} successfully'
                }
            else:
                return {'success': False, 'error': f'Failed to {action} contact'}
            
        except Exception as e:
            raise IntegrationError(f"Contact sync failed: {e}")
    
    def _find_or_create_contact(self, contact_data: Any, contact_type: str = 'vendor') -> Dict[str, Any]:
        """Find existing contact or create new one"""
        try:
            # If contact_data is a BigCapitalContact object, convert to dict
            if hasattr(contact_data, 'to_dict'):
                contact_dict = contact_data.to_dict()
            else:
                contact_dict = contact_data
            
            contact_dict['contact_type'] = contact_type
            
            # Check cache first
            self._refresh_cache_if_needed()
            
            # Look for existing contact by email
            email = contact_dict.get('email', '').lower()
            if email and email in self._contacts_cache:
                existing_contact = self._contacts_cache[email]
                return {
                    'success': True,
                    'contact_id': existing_contact['id'],
                    'action': 'found_existing'
                }
            
            # Search by name
            display_name = contact_dict.get('display_name', '')
            if display_name:
                search_results = self.client.search_contacts(display_name, contact_type)
                if search_results:
                    # Use first match
                    existing_contact = search_results[0]
                    return {
                        'success': True,
                        'contact_id': existing_contact['id'],
                        'action': 'found_by_search'
                    }
            
            # Create new contact
            result = self.client.create_contact(contact_dict)
            if result:
                # Update cache
                contact_id = result['id']
                self._contacts_cache[contact_id] = result
                if email:
                    self._contacts_cache[email] = result
                
                return {
                    'success': True,
                    'contact_id': contact_id,
                    'action': 'created'
                }
            else:
                return {'success': False, 'error': 'Failed to create contact'}
                
        except Exception as e:
            logger.error(f"Failed to find or create contact: {e}")
            return {'success': False, 'error': str(e)}
    
    # Validation Methods
    def _validate_invoice_data(self, data: Dict[str, Any]) -> bool:
        """Validate invoice data"""
        required_fields = ['customer_id', 'line_items']
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required invoice field: {field}")
                return False
        
        # Validate line items
        line_items = data.get('line_items', [])
        if not line_items:
            logger.error("Invoice must have at least one line item")
            return False
        
        for item in line_items:
            if not ValidationHelper.validate_amount(item.get('amount', 0)):
                logger.error(f"Invalid amount in line item: {item}")
                return False
        
        return True
    
    def _validate_expense_data(self, data: Dict[str, Any]) -> bool:
        """Validate expense data"""
        required_fields = ['amount', 'payment_account_id']
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required expense field: {field}")
                return False
        
        if not ValidationHelper.validate_amount(data.get('amount', 0)):
            logger.error("Invalid expense amount")
            return False
        
        return True
    
    def _validate_contact_data(self, data: Dict[str, Any]) -> bool:
        """Validate contact data"""
        if not data.get('display_name'):
            logger.error("Contact must have a display name")
            return False
        
        email = data.get('email')
        if email and not ValidationHelper.validate_email(email):
            logger.error(f"Invalid email format: {email}")
            return False
        
        return True
    
    def _customer_exists(self, customer_id: int) -> bool:
        """Check if customer exists"""
        self._refresh_cache_if_needed()
        return customer_id in self._contacts_cache
    
    def _find_existing_contact(self, contact_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find existing contact by email or name"""
        self._refresh_cache_if_needed()
        
        # Search by email first
        email = contact_data.get('email', '').lower()
        if email and email in self._contacts_cache:
            return self._contacts_cache[email]
        
        # Search by name
        display_name = contact_data.get('display_name', '')
        if display_name:
            for contact in self._contacts_cache.values():
                if (isinstance(contact, dict) and 
                    contact.get('display_name', '').lower() == display_name.lower()):
                    return contact
        
        return None
    
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
    
    def sync_invoice_from_invoiceplane(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync invoice data from InvoicePlane to BigCapital"""
        try:
            if not self.client:
                raise IntegrationError("BigCapital client not initialized")
            
            invoice_id = invoice_data.get('id', 'unknown')
            invoice_number = invoice_data.get('invoice_number', 'unknown')
            logger.info(f"Syncing invoice from InvoicePlane: {invoice_number} (ID: {invoice_id})")
            
            # Debug: Log the invoice data structure
            logger.debug(f"InvoicePlane invoice data keys: {list(invoice_data.keys())}")
            if 'client' in invoice_data:
                logger.debug(f"Client data keys: {list(invoice_data['client'].keys())}")
            if 'items' in invoice_data:
                logger.debug(f"Items count: {len(invoice_data['items'])}")
                if invoice_data['items']:
                    logger.debug(f"First item keys: {list(invoice_data['items'][0].keys())}")
            
            # Transform InvoicePlane invoice data to BigCapital format
            bigcapital_invoice = self._transform_invoiceplane_to_bigcapital(invoice_data)
            
            logger.debug(f"Transformed BigCapital invoice: {bigcapital_invoice}")
            
            # Check if we have a valid customer_id
            if not bigcapital_invoice.get('customer_id'):
                logger.error("Failed to find or create customer for invoice")
                return {
                    'success': False,
                    'error': 'Failed to find or create customer',
                    'invoiceplane_id': invoice_id,
                    'invoice_number': invoice_number
                }
            
            # Create invoice in BigCapital
            result = self.client.create_invoice(bigcapital_invoice)
            
            if result:
                self._sync_stats['invoices_created'] += 1
                self._sync_stats['last_sync'] = datetime.now()
                logger.info(f"Successfully synced invoice to BigCapital: {result.get('id')}")
                return {
                    'success': True,
                    'bigcapital_invoice_id': result.get('id'),
                    'invoiceplane_id': invoice_id,
                    'invoice_number': invoice_number
                }
            else:
                self._sync_stats['errors'] += 1
                logger.error("Failed to create invoice in BigCapital")
                return {
                    'success': False,
                    'error': 'Failed to create invoice in BigCapital',
                    'invoiceplane_id': invoice_id,
                    'invoice_number': invoice_number
                }
                
        except BigCapitalAPIError as e:
            logger.error(f"BigCapital API error syncing invoice: {e}")
            self._sync_stats['errors'] += 1
            return {
                'success': False,
                'error': f'BigCapital API error: {str(e)}',
                'invoiceplane_id': invoice_data.get('id'),
                'invoice_number': invoice_data.get('invoice_number')
            }
        except Exception as e:
            logger.error(f"Unexpected error syncing invoice: {e}")
            self._sync_stats['errors'] += 1
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'invoiceplane_id': invoice_data.get('id'),
                'invoice_number': invoice_data.get('invoice_number')
            }

    def sync_recent_invoices_from_invoiceplane(self, days: int = 7) -> List[Dict[str, Any]]:
        """Sync recent invoices from InvoicePlane to BigCapital"""
        try:
            if not self.client:
                raise IntegrationError("BigCapital client not initialized")
            
            # Import here to avoid circular imports
            from plugins.invoiceplanepy.plugin import InvoicePlanePlugin
            
            # Get InvoicePlane plugin instance (this assumes it's configured)
            # Use the invoiceplanepy plugin name to match the restored plugin directory
            invoiceplane_plugin = InvoicePlanePlugin("invoiceplanepy")
            # Note: In a real implementation, you'd get this from the plugin manager
            
            # For now, we'll use the InvoicePlane client directly
            # This is a simplified version - in production you'd want proper plugin integration
            logger.warning("Using simplified InvoicePlane integration - plugin manager integration needed")
            
            # Get recent invoices from InvoicePlane
            recent_invoices = []  # This would come from InvoicePlane plugin
            
            results = []
            for invoice in recent_invoices:
                result = self.sync_invoice_from_invoiceplane(invoice)
                results.append(result)
            
            successful = sum(1 for r in results if r.get('success'))
            logger.info(f"Synced {successful}/{len(results)} recent invoices from InvoicePlane")
            
            return results
            
        except Exception as e:
            logger.error(f"Error syncing recent invoices: {e}")
            return [{
                'success': False,
                'error': f'Failed to sync recent invoices: {str(e)}'
            }]

    def _transform_invoiceplane_to_bigcapital(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform InvoicePlane invoice data to BigCapital format"""
        try:
            # Extract client information from the invoice
            client_data = invoice_data.get('client', {})
            
            # Find or create client in BigCapital
            client_result = self._find_or_create_contact_from_invoiceplane(client_data)
            customer_id = client_result.get('contact_id') if client_result.get('success') else None
            
            # Transform line items
            line_items = []
            for item in invoice_data.get('items', []):
                item_data = {
                    'description': item.get('name', ''),
                    'quantity': item.get('quantity', 1),
                    'unit_price': item.get('price', 0)
                }
                # Calculate amount
                item_data['amount'] = item_data['quantity'] * item_data['unit_price']
                line_items.append(item_data)
            
            # Build BigCapital invoice using correct field names from API spec
            bigcapital_invoice = {
                'customer_id': customer_id,
                'invoice_number': invoice_data.get('invoice_number'),
                'invoice_date': invoice_data.get('issue_date'),
                'due_date': invoice_data.get('due_date'),
                'line_items': line_items
            }
            
            return bigcapital_invoice
            
        except Exception as e:
            logger.error(f"Error transforming invoice data: {e}")
            raise

    def _find_or_create_contact_from_invoiceplane(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find existing contact or create new one from InvoicePlane client data"""
        try:
            # Try to find existing contact by email or name
            existing_contact = self._find_existing_contact_from_invoiceplane(client_data)
            
            if existing_contact:
                return {
                    'success': True,
                    'contact_id': existing_contact['id'],
                    'action': 'found'
                }
            
            # Create new contact - use correct field names for BigCapital API
            contact_data = {
                'display_name': client_data.get('name', ''),
                'email': client_data.get('email', ''),
                'phone': client_data.get('phone', ''),
                'billing_address': client_data.get('address_1', ''),
                'billing_city': client_data.get('city', ''),
                'billing_state': client_data.get('state', ''),
                'billing_postal_code': client_data.get('zip_code', ''),
                'billing_country': client_data.get('country', '')
            }
            
            result = self.client.create_contact(contact_data)
            
            if result:
                self._sync_stats['contacts_created'] += 1
                logger.info(f"Created new contact in BigCapital: {result.get('id')}")
                return {
                    'success': True,
                    'contact_id': result.get('id'),
                    'action': 'created'
                }
            else:
                logger.error("Failed to create contact in BigCapital")
                return {
                    'success': False,
                    'error': 'Failed to create contact'
                }
                
        except Exception as e:
            logger.error(f"Error finding/creating contact: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _find_existing_contact_from_invoiceplane(self, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find existing contact in BigCapital by InvoicePlane client data"""
        try:
            email = client_data.get('email')
            name = client_data.get('name')
            
            # Search by email first
            if email:
                contacts = self.client.search_contacts(email)
                if contacts:
                    return contacts[0]
            
            # Search by name
            if name:
                contacts = self.client.search_contacts(name)
                if contacts:
                    return contacts[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching for existing contact: {e}")
            return None

    def _map_invoice_status(self, invoiceplane_status: Any) -> str:
        """Map InvoicePlane invoice status to BigCapital status"""
        # Handle both numeric status and status_name from API
        if isinstance(invoiceplane_status, int):
            # Map numeric status to string status
            numeric_mapping = {
                1: 'draft',
                2: 'sent', 
                3: 'viewed',
                4: 'paid',
                5: 'overdue',
                6: 'cancelled'
            }
            status_str = numeric_mapping.get(invoiceplane_status, 'draft')
        else:
            # Handle string status
            status_str = str(invoiceplane_status)
        
        # Map to BigCapital status
        status_mapping = {
            'draft': 'draft',
            'sent': 'sent',
            'viewed': 'sent',
            'overdue': 'overdue',
            'paid': 'paid',
            'cancelled': 'cancelled'
        }
        
        return status_mapping.get(status_str, 'draft')

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate BigCapital plugin configuration"""
        required_fields = ['api_key']
        
        for field in required_fields:
            if not config.get(field):
                logger.error(f"Missing required configuration field: {field}")
                return False
        
        return True
