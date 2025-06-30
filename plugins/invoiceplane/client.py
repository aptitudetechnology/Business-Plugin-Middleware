"""
InvoicePlane API Client
"""
import requests
from typing import Dict, Any, List, Optional
from loguru import logger


class InvoicePlaneClient:
    """Client for InvoicePlane API interactions"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Business-Plugin-Middleware/1.0',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request to InvoicePlane API"""
        try:
            url = f"{self.base_url}/index.php/api/v1/{endpoint}"
            params = {'key': self.api_key}
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                params.update(data or {})
                response = self.session.post(url, data=params)
            elif method.upper() == 'PUT':
                params.update(data or {})
                response = self.session.put(url, data=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # InvoicePlane API may return JSON or plain text
            try:
                return response.json()
            except ValueError:
                return {'response': response.text}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"InvoicePlane API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in InvoicePlane API request: {e}")
            return None
    
    def get_system_info(self) -> Optional[Dict[str, Any]]:
        """Get InvoicePlane system information"""
        return self._make_request('GET', 'system')
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new invoice"""
        return self._make_request('POST', 'invoices', invoice_data)
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice by ID"""
        return self._make_request('GET', f'invoices/{invoice_id}')
    
    def get_recent_invoices(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent invoices"""
        result = self._make_request('GET', f'invoices?limit={limit}')
        if result and isinstance(result, list):
            return result
        elif result and 'invoices' in result:
            return result['invoices']
        return []
    
    def create_quote(self, quote_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new quote"""
        return self._make_request('POST', 'quotes', quote_data)
    
    def get_quote(self, quote_id: str) -> Optional[Dict[str, Any]]:
        """Get quote by ID"""
        return self._make_request('GET', f'quotes/{quote_id}')
    
    def get_recent_quotes(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent quotes"""
        result = self._make_request('GET', f'quotes?limit={limit}')
        if result and isinstance(result, list):
            return result
        elif result and 'quotes' in result:
            return result['quotes']
        return []
    
    def create_client(self, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new client"""
        return self._make_request('POST', 'clients', client_data)
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID"""
        return self._make_request('GET', f'clients/{client_id}')
    
    def get_clients(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get all clients"""
        result = self._make_request('GET', f'clients?limit={limit}')
        if result and isinstance(result, list):
            return result
        elif result and 'clients' in result:
            return result['clients']
        return []
    
    def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new product"""
        return self._make_request('POST', 'products', product_data)
    
    def get_products(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get all products"""
        result = self._make_request('GET', f'products?limit={limit}')
        if result and isinstance(result, list):
            return result
        elif result and 'products' in result:
            return result['products']
        return []
    
    def get_invoice_statuses(self) -> Optional[List[Dict[str, Any]]]:
        """Get available invoice statuses"""
        result = self._make_request('GET', 'invoices/statuses')
        if result and isinstance(result, list):
            return result
        elif result and 'statuses' in result:
            return result['statuses']
        return []
    
    def get_quote_statuses(self) -> Optional[List[Dict[str, Any]]]:
        """Get available quote statuses"""
        result = self._make_request('GET', 'quotes/statuses')
        if result and isinstance(result, list):
            return result
        elif result and 'statuses' in result:
            return result['statuses']
        return []
