"""
InvoicePlane API Client
"""
import requests
from typing import Dict, Any, List, Optional
from loguru import logger


class InvoicePlanePagination:
    """Simple pagination class for InvoicePlane results"""
    
    def __init__(self, data: Dict[str, Any], page: int, per_page: int):
        self.data = data
        self.page = page
        self.per_page = per_page
        self.total = data.get('total', 0)
        self.results = data.get('data', [])
        
    @property
    def pages(self):
        """Total number of pages"""
        if self.per_page == 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page
    
    @property
    def has_prev(self):
        """Check if there's a previous page"""
        return self.page > 1
    
    @property
    def has_next(self):
        """Check if there's a next page"""
        return self.page < self.pages
    
    @property
    def prev_num(self):
        """Previous page number"""
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_num(self):
        """Next page number"""
        return self.page + 1 if self.has_next else None
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """Iterate over page numbers for pagination display"""
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None  # Gap
                yield num
                last = num


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
    
    def get_invoices(self, page: int = 1, per_page: int = 25, date_from: str = None, date_to: str = None, status: str = None) -> Optional[Dict[str, Any]]:
        """Get invoices with pagination and filtering"""
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        if status:
            params['status'] = status
            
        # Build query string
        query_parts = []
        for key, value in params.items():
            query_parts.append(f'{key}={value}')
        query_string = '&'.join(query_parts)
        
        result = self._make_request('GET', f'invoices?{query_string}')
        
        # InvoicePlane API returns different formats, try to normalize
        if result:
            if isinstance(result, list):
                # Return as paginated response
                return {
                    'data': result,
                    'page': page,
                    'per_page': per_page,
                    'total': len(result),  # This is approximate since we don't have total count
                    'has_more': len(result) == per_page
                }
            elif isinstance(result, dict) and 'invoices' in result:
                return {
                    'data': result['invoices'],
                    'page': page,
                    'per_page': per_page,
                    'total': result.get('total', len(result['invoices'])),
                    'has_more': len(result['invoices']) == per_page
                }
            else:
                # Single invoice or unexpected format
                return {
                    'data': [result] if isinstance(result, dict) else [],
                    'page': page,
                    'per_page': per_page,
                    'total': 1 if isinstance(result, dict) else 0,
                    'has_more': False
                }
        
        return None
    
    def get_recent_invoices(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent invoices (legacy method for backward compatibility)"""
        result = self.get_invoices(per_page=limit, page=1)
        if result and 'data' in result:
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
