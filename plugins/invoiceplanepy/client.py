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
                    logger.debug(f"Direct invoice response keys: {list(data.keys())}")
                    logger.debug(f"Full direct response: {data}")
                    
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
            # Try different possible parameter names for invoice number filtering
            for param_name in ['invoice_number', 'number', 'invoice_no', 'invoice']:
                try:
                    url = f"{self.base_url}/invoices/api"
                    params = {param_name: invoice_id, 'limit': 1, 'page': 1}
                    response = self.session.get(url, params=params, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'invoices' in data and len(data['invoices']) > 0:
                            # Find the invoice that matches the requested ID/number
                            for inv in data['invoices']:
                                if (str(inv.get('id', '')) == str(invoice_id) or 
                                    str(inv.get('invoice_number', '')) == str(invoice_id) or
                                    str(inv.get('number', '')) == str(invoice_id)):
                                    logger.info(f"Found matching invoice by {param_name} {invoice_id}: ID={inv.get('id')}, Number={inv.get('invoice_number')}")
                                    
                                    # Check if items are included, if not, fetch them separately
                                    if 'items' not in inv or not inv['items']:
                                        logger.info(f"Invoice {invoice_id} has no items in response, fetching separately")
                                        items = self.get_invoice_items(inv['id'])
                                        if items:
                                            inv['items'] = items
                                            logger.info(f"Added {len(items)} items to invoice {invoice_id}")
                                        else:
                                            logger.warning(f"Could not fetch items for invoice {invoice_id}")
                                    
                                    return inv
                            
                            # If no exact match, take the first one but log a warning
                            if data['invoices']:
                                inv = data['invoices'][0]
                                logger.warning(f"No exact match for {invoice_id}, using first result: ID={inv.get('id')}, Number={inv.get('invoice_number')}")
                                
                                # Check if items are included, if not, fetch them separately
                                if 'items' not in inv or not inv['items']:
                                    logger.info(f"Invoice {invoice_id} has no items in response, fetching separately")
                                    items = self.get_invoice_items(inv['id'])
                                    if items:
                                        inv['items'] = items
                                        logger.info(f"Added {len(items)} items to invoice {invoice_id}")
                                    else:
                                        logger.warning(f"Could not fetch items for invoice {invoice_id}")
                                
                                return inv
                except requests.exceptions.RequestException:
                    continue

            # Fallback: Get all invoices and filter client-side
            logger.info(f"All previous methods failed, fetching all invoices and filtering for {invoice_id}")
            all_invoices_response = self.get_invoices(limit=1000)  # Get up to 1000 invoices
            if all_invoices_response and 'invoices' in all_invoices_response:
                # Try to match by ID first
                for inv in all_invoices_response['invoices']:
                    if str(inv.get('id', '')) == str(invoice_id):
                        logger.info(f"Found invoice by ID {invoice_id} in full list")
                        # Fetch items separately for this invoice
                        if 'items' not in inv or not inv['items']:
                            items = self.get_invoice_items(str(inv['id']))
                            if items:
                                inv['items'] = items
                                logger.info(f"Added {len(items)} items to invoice {invoice_id}")
                        return inv
                
                # Try to match by invoice_number
                for inv in all_invoices_response['invoices']:
                    if str(inv.get('invoice_number', '')) == str(invoice_id):
                        logger.info(f"Found invoice by invoice_number {invoice_id} in full list")
                        # Fetch items separately for this invoice
                        if 'items' not in inv or not inv['items']:
                            items = self.get_invoice_items(str(inv['id']))
                            if items:
                                inv['items'] = items
                                logger.info(f"Added {len(items)} items to invoice {invoice_id}")
                        return inv
            
            logger.warning(f"No invoice found with ID or invoice_number: {invoice_id} in full list")
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
            # Try different possible endpoints for invoice items
            possible_endpoints = [
                f"invoices/{invoice_id}/items",
                f"invoice_items/{invoice_id}",
                f"invoices/items/{invoice_id}",
                f"invoice_items",  # Try general endpoint with filter
                f"invoices/{invoice_id}/items/api",  # Try with /api
                f"invoice_items/{invoice_id}/api",
                f"invoices/items/{invoice_id}/api",
            ]
            
            for endpoint in possible_endpoints:
                try:
                    url = f"{self.base_url}/{endpoint}/api"
                    headers = {'Authorization': f'Bearer {self.api_key}'}
                    
            # For the general invoice_items endpoint, add invoice_id filter
                    if endpoint == "invoice_items":
                        params = {'invoice_id': invoice_id}
                        response = self.session.get(url, params=params, headers=headers)
                        logger.debug(f"Trying {url} with params {params}")
                    else:
                        response = self.session.get(url, headers=headers)
                        logger.debug(f"Trying {url}")
                    
                    logger.debug(f"Response status: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        logger.debug(f"Response data type: {type(data)}")
                        if isinstance(data, dict):
                            logger.debug(f"Response keys: {list(data.keys())}")
                        elif isinstance(data, list):
                            logger.debug(f"Response is list with {len(data)} items")
                            if data and isinstance(data[0], dict):
                                logger.debug(f"First item keys: {list(data[0].keys())}")
                        
                        if isinstance(data, list):
                            logger.info(f"Found {len(data)} invoice items at endpoint: {endpoint}")
                            return data
                        elif 'items' in data:
                            logger.info(f"Found {len(data['items'])} invoice items at endpoint: {endpoint}")
                            return data['items']
                        elif 'invoice_items' in data:
                            logger.info(f"Found {len(data['invoice_items'])} invoice items at endpoint: {endpoint}")
                            return data['invoice_items']
                        logger.info(f"Found invoice items at endpoint: {endpoint}")
                        return []
                        
                except requests.exceptions.RequestException:
                    continue  # Try next endpoint
            
            # Try getting all invoice items and filtering by invoice_id
            try:
                # Try different URLs for all invoice items
                for items_url in ["invoice_items/api", "invoice_items"]:
                    url = f"{self.base_url}/{items_url}"
                    headers = {'Authorization': f'Bearer {self.api_key}'}
                    response = self.session.get(url, headers=headers)
                    logger.debug(f"Trying {url} to get all invoice items")
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.debug(f"All invoice items response status: {response.status_code}")
                        if isinstance(data, dict):
                            logger.debug(f"All invoice items response keys: {list(data.keys())}")
                        elif isinstance(data, list):
                            logger.debug(f"All invoice items is list with {len(data)} items")
                        
                        if isinstance(data, list):
                            # Filter by invoice_id
                            filtered_items = [item for item in data if str(item.get('invoice_id', '')) == str(invoice_id)]
                            if filtered_items:
                                logger.info(f"Found {len(filtered_items)} invoice items by filtering all items from {items_url}")
                                return filtered_items
                        elif isinstance(data, dict) and 'invoice_items' in data:
                            filtered_items = [item for item in data['invoice_items'] if str(item.get('invoice_id', '')) == str(invoice_id)]
                            if filtered_items:
                                logger.info(f"Found {len(filtered_items)} invoice items by filtering from 'invoice_items' key in {items_url}")
                                return filtered_items
                        elif isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                            filtered_items = [item for item in data['data'] if str(item.get('invoice_id', '')) == str(invoice_id)]
                            if filtered_items:
                                logger.info(f"Found {len(filtered_items)} invoice items by filtering from 'data' key in {items_url}")
                                return filtered_items
            except requests.exceptions.RequestException as e:
                logger.debug(f"Failed to get all invoice items: {e}")
                pass
            
            # Last resort: Try to get the invoice directly and extract items if present
            logger.info(f"Last resort: getting invoice {invoice_id} directly to extract items")
            try:
                direct_invoice = self.get_invoice(invoice_id)
                if direct_invoice and direct_invoice.get('items'):
                    logger.info(f"Found {len(direct_invoice['items'])} items in direct invoice response")
                    return direct_invoice['items']
            except Exception as e:
                logger.debug(f"Failed to get invoice directly for items: {e}")
            
            logger.warning(f"No invoice items found for invoice {invoice_id}")
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
