"""
Invoice Ninja API Client
"""
import requests
from typing import Dict, Any, List, Optional
from loguru import logger


class InvoiceNinjaClient:
    """Client for Invoice Ninja API interactions"""
    
    def __init__(self, api_token: str, base_url: str):
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-Ninja-Token': api_token,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Business-Plugin-Middleware/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request to Invoice Ninja API"""
        try:
            url = f"{self.base_url}/api/v1/{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Invoice Ninja API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Invoice Ninja API request: {e}")
            return None
    
    def get_company_info(self) -> Optional[Dict[str, Any]]:
        """Get company information"""
        result = self._make_request('GET', 'companies')
        if result and result.get('data'):
            return result['data'][0] if isinstance(result['data'], list) else result['data']
        return None
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new invoice"""
        return self._make_request('POST', 'invoices', invoice_data)
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice by ID"""
        return self._make_request('GET', f'invoices/{invoice_id}')
    
    def get_recent_invoices(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent invoices"""
        result = self._make_request('GET', f'invoices?per_page={limit}&sort=created_at|desc')
        if result and result.get('data'):
            return result['data']
        return []
    
    def create_quote(self, quote_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new quote"""
        return self._make_request('POST', 'quotes', quote_data)
    
    def get_quote(self, quote_id: str) -> Optional[Dict[str, Any]]:
        """Get quote by ID"""
        return self._make_request('GET', f'quotes/{quote_id}')
    
    def get_recent_quotes(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent quotes"""
        result = self._make_request('GET', f'quotes?per_page={limit}&sort=created_at|desc')
        if result and result.get('data'):
            return result['data']
        return []
    
    def create_client(self, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new client"""
        return self._make_request('POST', 'clients', client_data)
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID"""
        return self._make_request('GET', f'clients/{client_id}')
    
    def get_clients(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get all clients"""
        result = self._make_request('GET', f'clients?per_page={limit}')
        if result and result.get('data'):
            return result['data']
        return []
    
    def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new product"""
        return self._make_request('POST', 'products', product_data)
    
    def get_products(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get all products"""
        result = self._make_request('GET', f'products?per_page={limit}')
        if result and result.get('data'):
            return result['data']
        return []
    
    def get_payment_terms(self) -> Optional[List[Dict[str, Any]]]:
        """Get available payment terms"""
        result = self._make_request('GET', 'payment_terms')
        if result and result.get('data'):
            return result['data']
        return []
    
    def get_tax_rates(self) -> Optional[List[Dict[str, Any]]]:
        """Get available tax rates"""
        result = self._make_request('GET', 'tax_rates')
        if result and result.get('data'):
            return result['data']
        return []
    
    def get_countries(self) -> Optional[List[Dict[str, Any]]]:
        """Get available countries"""
        result = self._make_request('GET', 'static/countries')
        if result and result.get('data'):
            return result['data']
        return []
    
    def get_currencies(self) -> Optional[List[Dict[str, Any]]]:
        """Get available currencies"""
        result = self._make_request('GET', 'static/currencies')
        if result and result.get('data'):
            return result['data']
        return []
    
    def send_invoice_email(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Send invoice via email"""
        return self._make_request('POST', f'invoices/{invoice_id}/email')
    
    def mark_invoice_sent(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Mark invoice as sent"""
        return self._make_request('PUT', f'invoices/{invoice_id}/mark_sent')
    
    def mark_invoice_paid(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Mark invoice as paid"""
        return self._make_request('PUT', f'invoices/{invoice_id}/mark_paid')
