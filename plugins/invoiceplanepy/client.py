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
        """Get invoice by ID with full details"""
        try:
            # Try direct endpoint first: /invoices/{id}/api
            url = f"{self.base_url}/invoices/{invoice_id}/api"
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = self.session.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'id' in data:
                    logger.info(f"Found invoice {invoice_id} directly at /invoices/{invoice_id}/api")
                    
                    # Check if items are included, if not, fetch them separately
                    if 'items' not in data or not data['items']:
                        logger.info(f"Invoice {invoice_id} has no items in response, fetching separately")
                        items = self.get_invoice_items(invoice_id)
                        if items:
                            data['items'] = items
                            logger.info(f"Added {len(items)} items to invoice {invoice_id}")
                        else:
                            logger.warning(f"Could not fetch items for invoice {invoice_id}")
                    
                    return data

            # Try with invoice_number if direct endpoint fails
            logger.info(f"Direct endpoint failed for {invoice_id}, trying with invoice_number")
            url = f"{self.base_url}/invoices/api"
            params = {
                'invoice_number': invoice_id,
                'limit': 1,
                'page': 1
            }

            response = self.session.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'invoices' in data and len(data['invoices']) > 0:
                    invoice = data['invoices'][0]
                    logger.info(f"Found invoice by invoice_number {invoice_id}")
                    
                    # Check if items are included, if not, fetch them separately
                    if 'items' not in invoice or not invoice['items']:
                        logger.info(f"Invoice {invoice_id} has no items in response, fetching separately")
                        items = self.get_invoice_items(invoice['id'])
                        if items:
                            invoice['items'] = items
                            logger.info(f"Added {len(items)} items to invoice {invoice_id}")
                        else:
                            logger.warning(f"Could not fetch items for invoice {invoice_id}")
                    
                    return invoice

            # Fallback to filtering by ID
            logger.info(f"Invoice number search failed, trying ID filter for {invoice_id}")
            params = {
                'id': invoice_id,
                'limit': 1,
                'page': 1
            }

            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            if 'invoices' in data and len(data['invoices']) > 0:
                invoice = data['invoices'][0]
                logger.info(f"Found invoice by ID filter {invoice_id}")
                
                # Check if items are included, if not, fetch them separately
                if 'items' not in invoice or not invoice['items']:
                    logger.info(f"Invoice {invoice_id} has no items in response, fetching separately")
                    items = self.get_invoice_items(invoice['id'])
                    if items:
                        invoice['items'] = items
                        logger.info(f"Added {len(items)} items to invoice {invoice_id}")
                    else:
                        logger.warning(f"Could not fetch items for invoice {invoice_id}")
                
                return invoice
            else:
                logger.warning(f"No invoice found with ID or invoice_number: {invoice_id}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch invoice {invoice_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching invoice {invoice_id}: {e}")
            return None
    
    def get_invoice_items(self, invoice_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get invoice items for a specific invoice"""
        try:
            # Try the correct InvoicePlane API endpoint for invoice items
            # Based on InvoicePlane API, items are typically at /invoice_items with invoice_id filter
            url = f"{self.base_url}/invoice_items/api"
            params = {
                'invoice_id': invoice_id,
                'limit': 100  # Get all items for this invoice
            }
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = self.session.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'invoice_items' in data and isinstance(data['invoice_items'], list):
                    logger.info(f"Found {len(data['invoice_items'])} items for invoice {invoice_id}")
                    return data['invoice_items']
                elif isinstance(data, list):
                    logger.info(f"Found {len(data)} items for invoice {invoice_id}")
                    return data
            
            # Fallback: try direct invoice items endpoint
            url = f"{self.base_url}/invoices/{invoice_id}/items/api"
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    logger.info(f"Found {len(data)} items for invoice {invoice_id} via direct endpoint")
                    return data
                elif 'items' in data and isinstance(data['items'], list):
                    logger.info(f"Found {len(data['items'])} items for invoice {invoice_id} via direct endpoint")
                    return data['items']
            
            logger.warning(f"No invoice items found for invoice {invoice_id}")
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch invoice items for {invoice_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching invoice items for {invoice_id}: {e}")
            return []
    
    def get_recent_invoices(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent invoices using the new API format"""
        try:
            # Use the new API endpoint from the specification
            url = f"{self.base_url}/invoices/api"
            params = {
                'limit': min(limit, 100),  # API max is 100
                'page': 1,
                'sort_by': 'created_at',
                'sort_order': 'desc'
            }
            
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if 'invoices' in data:
                return data['invoices']
            else:
                logger.warning("Unexpected response format from InvoicePlane API")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch recent invoices: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching recent invoices: {e}")
            return []
    
    def get_invoices(self, page: int = 1, per_page: int = 25, date_from: str = None, date_to: str = None, status: str = None) -> Optional[Dict[str, Any]]:
        """Get invoices with pagination and filtering"""
        try:
            # Use the new API endpoint from the specification
            url = f"{self.base_url}/invoices/api"
            params = {
                'limit': min(per_page, 100),  # API max is 100
                'page': page,
                'sort_by': 'created_at',
                'sort_order': 'desc'
            }
            
            # Add status filter if provided
            if status:
                params['status'] = status
            
            # Note: The API may not support date filtering directly
            # If date filtering is needed, it would need to be implemented differently
            
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform the response to match the expected format
            if 'invoices' in data:
                pagination_info = data.get('pagination', {})
                return {
                    'data': data['invoices'],
                    'page': pagination_info.get('page', page),
                    'per_page': pagination_info.get('limit', per_page),
                    'total': pagination_info.get('total', len(data['invoices'])),
                    'has_more': pagination_info.get('page', page) < pagination_info.get('total_pages', 1)
                }
            else:
                logger.warning("Unexpected response format from InvoicePlane API")
                return {
                    'data': [],
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'has_more': False
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch invoices: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching invoices: {e}")
            return None
    
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
        try:
            # Use the same pattern as invoices
            url = f"{self.base_url}/clients/api"
            params = {
                'id': client_id
            }
            
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and result:
                return result[0]
            elif isinstance(result, dict):
                return result
            return None
        except Exception as e:
            logger.error(f"Failed to get client {client_id}: {e}")
            return None
    
    def get_clients(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get all clients using the bulk API endpoint"""
        try:
            # Use the now-working bulk clients API endpoint
            url = f"{self.base_url}/clients/api"
            params = {
                'limit': min(limit, 100)
            }

            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()

            result = response.json()
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'clients' in result:
                return result['clients']
            return []
        except Exception as e:
            logger.error(f"Failed to get clients: {e}")
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
    
    def get_invoice_html(self, invoice_id: int) -> Optional[str]:
        """Get HTML representation of an invoice"""
        try:
            url = f"{self.base_url}/invoices/{invoice_id}"
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get invoice HTML for {invoice_id}: {e}")
            return None
    
    def get_quote_statuses(self) -> Optional[List[Dict[str, Any]]]:
        """Get available quote statuses"""
        result = self._make_request('GET', 'quotes/statuses')
        if result and isinstance(result, list):
            return result
        elif result and 'statuses' in result:
            return result['statuses']
        return []
