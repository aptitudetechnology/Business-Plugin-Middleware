"""
BigCapital API Client

Enhanced client for comprehensive BigCapital API interactions with proper
error handling, retry logic, and extensive API coverage.
"""
import requests
import time
from loguru import logger
from typing import Dict, Any, List, Optional, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BigCapitalAPIError(Exception):
    """Custom exception for BigCapital API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class BigCapitalClient:
    """Enhanced client for BigCapital API interactions"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.bigcapital.ly", timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Business-Plugin-Middleware/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request to BigCapital API with enhanced error handling"""
        try:
            # Ensure endpoint starts with /api/v1
            if not endpoint.startswith('/api/v1'):
                if endpoint.startswith('/'):
                    endpoint = f'/api/v1{endpoint}'
                else:
                    endpoint = f'/api/v1/{endpoint}'
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            # Add timeout if not specified
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            
            logger.debug(f"Making {method} request to {url}")
            
            response = self.session.request(method, url, **kwargs)
            
            # Log response details
            logger.debug(f"Response status: {response.status_code}")
            
            # Handle different response scenarios
            if response.status_code == 204:  # No content
                return {}
            
            if response.status_code == 401:
                raise BigCapitalAPIError("Authentication failed - check API key", response.status_code)
            
            if response.status_code == 403:
                raise BigCapitalAPIError("Access forbidden - insufficient permissions", response.status_code)
            
            if response.status_code == 404:
                raise BigCapitalAPIError(f"Resource not found: {endpoint}", response.status_code)
            
            if response.status_code == 429:
                raise BigCapitalAPIError("Rate limit exceeded", response.status_code)
            
            # Handle 400 Bad Request with detailed error info
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Bad request')
                    raise BigCapitalAPIError(f"Bad request: {error_msg}", response.status_code, error_data)
                except ValueError:
                    raise BigCapitalAPIError(f"Bad request: {response.text}", response.status_code)
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            try:
                return response.json()
            except ValueError as e:
                logger.warning(f"Could not parse JSON response: {e}")
                return {'raw_response': response.text}
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            raise BigCapitalAPIError(f"Request timeout for {endpoint}")
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {endpoint}")
            raise BigCapitalAPIError(f"Connection error for {endpoint}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"BigCapital API request failed: {e}")
            raise BigCapitalAPIError(f"API request failed: {str(e)}")
        
        except BigCapitalAPIError:
            raise  # Re-raise our custom errors
            
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            raise BigCapitalAPIError(f"Unexpected error: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test connection to BigCapital API"""
        try:
            response = self.get_organization_info()
            return response is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    
    # Organization and User Management
    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        """Get organization information"""
        try:
            return self._make_request('GET', 'organization')
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get organization info: {e}")
            return None
    
    def update_organization(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update organization information"""
        try:
            return self._make_request('PUT', 'organization', json=data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to update organization: {e}")
            return None
    
    def get_users(self) -> Optional[List[Dict[str, Any]]]:
        """Get users list"""
        try:
            response = self._make_request('GET', 'users')
            return response.get('data', []) if response else []
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get users: {e}")
            return []
    
    # Chart of Accounts
    def get_accounts(self, account_type: str = None) -> Optional[List[Dict[str, Any]]]:
        """Get accounts (chart of accounts)"""
        try:
            params = {}
            if account_type:
                params['type'] = account_type
            
            response = self._make_request('GET', 'accounts', params=params)
            return response.get('data', []) if response else []
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get accounts: {e}")
            return []
    
    def create_account(self, account_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new account"""
        try:
            return self._make_request('POST', 'accounts', json=account_data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to create account: {e}")
            return None
    
    def update_account(self, account_id: int, account_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing account"""
        try:
            return self._make_request('PUT', f'accounts/{account_id}', json=account_data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to update account {account_id}: {e}")
            return None
    
    def delete_account(self, account_id: int) -> bool:
        """Delete an account"""
        try:
            self._make_request('DELETE', f'accounts/{account_id}')
            return True
        except BigCapitalAPIError as e:
            logger.error(f"Failed to delete account {account_id}: {e}")
            return False    # Contact Management (Customers, Vendors, etc.)
    def get_contacts(self, contact_type: str = None, page: int = 1, per_page: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Get contacts with pagination"""
        try:
            params = {'page': page, 'per_page': per_page}
            if contact_type:
                params['contact_type'] = contact_type
            
            response = self._make_request('GET', 'customers', params=params)
            return response.get('data', {}).get('customers', []) if response else []
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get contacts: {e}")
            return []
    
    def get_customers(self, page: int = 1, per_page: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Get customers"""
        return self.get_contacts('customer', page, per_page)
    
    def get_vendors(self, page: int = 1, per_page: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Get vendors"""
        return self.get_contacts('vendor', page, per_page)
    
    def get_contact(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific contact"""
        try:
            return self._make_request('GET', f'customers/{contact_id}')
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get contact {contact_id}: {e}")
            return None
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new contact"""
        try:
            return self._make_request('POST', 'customers', json=contact_data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to create contact: {e}")
            return None
    
    def update_contact(self, contact_id: int, contact_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing contact"""
        try:
            return self._make_request('PUT', f'customers/{contact_id}', json=contact_data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to update contact {contact_id}: {e}")
            return None
    
    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact"""
        try:
            self._make_request('DELETE', f'customers/{contact_id}')
            return True
        except BigCapitalAPIError as e:
            logger.error(f"Failed to delete contact {contact_id}: {e}")
            return False
    
    def search_contacts(self, query: str, contact_type: str = None) -> Optional[List[Dict[str, Any]]]:
        """Search contacts by name or email - since BigCapital doesn't have a search endpoint, get all contacts and filter locally"""
        try:
            # Get all contacts since BigCapital doesn't have a search endpoint
            all_contacts = self.get_contacts()
            if not all_contacts:
                return []
            
            # Filter contacts locally
            query_lower = query.lower()
            filtered_contacts = []
            for contact in all_contacts:
                name = contact.get('name', '').lower()
                email = contact.get('email', '').lower()
                if query_lower in name or query_lower in email:
                    filtered_contacts.append(contact)
            
            return filtered_contacts
        except BigCapitalAPIError as e:
            logger.error(f"Failed to search contacts: {e}")
            return []
    
    # Invoice Management
    def get_invoices(self, page: int = 1, per_page: int = 50, status: str = None) -> Optional[List[Dict[str, Any]]]:
        """Get invoices with pagination and filtering"""
        try:
            params = {'page': page, 'per_page': per_page, 'sort_by': 'created_at', 'sort_order': 'desc'}
            if status:
                params['status'] = status
                
            response = self._make_request('GET', 'invoices', params=params)
            return response.get('data', []) if response else []
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get invoices: {e}")
            return []
    
    def get_recent_invoices(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent invoices"""
        return self.get_invoices(per_page=limit)
    
    def get_invoice(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific invoice"""
        try:
            return self._make_request('GET', f'invoices/{invoice_id}')
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get invoice {invoice_id}: {e}")
            return None
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new invoice"""
        try:
            logger.debug(f"Creating invoice with data: {invoice_data}")
            return self._make_request('POST', 'invoices', json=invoice_data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to create invoice: {e}")
            # Log additional error details if available
            if hasattr(e, 'response_data') and e.response_data:
                logger.error(f"BigCapital error response: {e.response_data}")
            return None
    
    def update_invoice(self, invoice_id: int, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing invoice"""
        try:
            return self._make_request('PUT', f'invoices/{invoice_id}', json=invoice_data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to update invoice {invoice_id}: {e}")
            return None
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """Delete an invoice"""
        try:
            self._make_request('DELETE', f'invoices/{invoice_id}')
            return True
        except BigCapitalAPIError as e:
            logger.error(f"Failed to delete invoice {invoice_id}: {e}")
            return False
    
    def send_invoice(self, invoice_id: int, email_data: Dict[str, Any] = None) -> bool:
        """Send invoice via email"""
        try:
            data = email_data or {}
            self._make_request('POST', f'invoices/{invoice_id}/send', json=data)
            return True
        except BigCapitalAPIError as e:
            logger.error(f"Failed to send invoice {invoice_id}: {e}")
            return False
    
    def mark_invoice_paid(self, invoice_id: int, payment_data: Dict[str, Any] = None) -> bool:
        """Mark invoice as paid"""
        try:
            data = payment_data or {'payment_date': time.strftime('%Y-%m-%d')}
            self._make_request('POST', f'invoices/{invoice_id}/payments', json=data)
            return True
        except BigCapitalAPIError as e:
            logger.error(f"Failed to mark invoice {invoice_id} as paid: {e}")
            return False
    
    # Expense Management
    def get_expenses(self, page: int = 1, per_page: int = 50, account_id: int = None) -> Optional[List[Dict[str, Any]]]:
        """Get expenses with pagination and filtering"""
        try:
            params = {'page': page, 'per_page': per_page, 'sort_by': 'payment_date', 'sort_order': 'desc'}
            if account_id:
                params['account_id'] = account_id
                
            response = self._make_request('GET', 'expenses', params=params)
            return response.get('data', []) if response else []
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get expenses: {e}")
            return []
    
    def get_recent_expenses(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent expenses"""
        return self.get_expenses(per_page=limit)
    
    def get_expense(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific expense"""
        try:
            return self._make_request('GET', f'expenses/{expense_id}')
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get expense {expense_id}: {e}")
            return None
    
    def create_expense(self, expense_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new expense"""
        try:
            return self._make_request('POST', 'expenses', json=expense_data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to create expense: {e}")
            return None
    
    def update_expense(self, expense_id: int, expense_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing expense"""
        try:
            return self._make_request('PUT', f'expenses/{expense_id}', json=expense_data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to update expense {expense_id}: {e}")
            return None
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense"""
        try:
            self._make_request('DELETE', f'expenses/{expense_id}')
            return True
        except BigCapitalAPIError as e:
            logger.error(f"Failed to delete expense {expense_id}: {e}")
            return False
    
    # Items and Services
    def get_items(self, item_type: str = None, page: int = 1, per_page: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Get items/services"""
        try:
            params = {'page': page, 'per_page': per_page}
            if item_type:
                params['type'] = item_type
                
            response = self._make_request('GET', 'items', params=params)
            return response.get('data', []) if response else []
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get items: {e}")
            return []
    
    def create_item(self, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new item/service"""
        try:
            return self._make_request('POST', 'items', json=item_data)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to create item: {e}")
            return None
    
    # Financial Reports
    def get_profit_loss_report(self, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """Get Profit & Loss report"""
        try:
            params = {'start_date': start_date, 'end_date': end_date}
            return self._make_request('GET', 'reports/profit-loss', params=params)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get P&L report: {e}")
            return None
    
    def get_balance_sheet_report(self, as_date: str) -> Optional[Dict[str, Any]]:
        """Get Balance Sheet report"""
        try:
            params = {'as_date': as_date}
            return self._make_request('GET', 'reports/balance-sheet', params=params)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get balance sheet: {e}")
            return None
    
    def get_cash_flow_report(self, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """Get Cash Flow report"""
        try:
            params = {'start_date': start_date, 'end_date': end_date}
            return self._make_request('GET', 'reports/cash-flow', params=params)
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get cash flow report: {e}")
            return None
    
    # Utility Methods
    def get_dashboard_stats(self) -> Optional[Dict[str, Any]]:
        """Get dashboard statistics"""
        try:
            return self._make_request('GET', 'dashboard/stats')
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return None
    
    def get_currencies(self) -> Optional[List[Dict[str, Any]]]:
        """Get supported currencies"""
        try:
            response = self._make_request('GET', 'currencies')
            return response.get('data', []) if response else []
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get currencies: {e}")
            return []
    
    def get_tax_rates(self) -> Optional[List[Dict[str, Any]]]:
        """Get tax rates"""
        try:
            response = self._make_request('GET', 'tax-rates')
            return response.get('data', []) if response else []
        except BigCapitalAPIError as e:
            logger.error(f"Failed to get tax rates: {e}")
            return []
    
    # Bulk Operations
    def bulk_create_contacts(self, contacts_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create multiple contacts in bulk"""
        try:
            return self._make_request('POST', 'contacts/bulk', json={'contacts': contacts_data})
        except BigCapitalAPIError as e:
            logger.error(f"Failed to bulk create contacts: {e}")
            return None
    
    def bulk_create_invoices(self, invoices_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create multiple invoices in bulk"""
        try:
            return self._make_request('POST', 'invoices/bulk', json={'invoices': invoices_data})
        except BigCapitalAPIError as e:
            logger.error(f"Failed to bulk create invoices: {e}")
            return None
