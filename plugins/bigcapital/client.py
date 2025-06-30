"""
BigCapital API Client
"""
import requests
from loguru import logger
from typing import Dict, Any, List, Optional


class BigCapitalClient:
    """Client for BigCapital API interactions"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.bigcapital.ly"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request to BigCapital API"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"BigCapital API request failed: {e}")
            return None
    
    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        """Get organization information"""
        return self._make_request('GET', '/api/organization')
    
    def get_recent_invoices(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent invoices"""
        params = {'limit': limit, 'sort_by': 'created_at', 'sort_order': 'desc'}
        response = self._make_request('GET', '/api/invoices', params=params)
        return response.get('data', []) if response else []
    
    def get_recent_expenses(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent expenses"""
        params = {'limit': limit, 'sort_by': 'created_at', 'sort_order': 'desc'}
        response = self._make_request('GET', '/api/expenses', params=params)
        return response.get('data', []) if response else []
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new invoice"""
        return self._make_request('POST', '/api/invoices', json=invoice_data)
    
    def create_expense(self, expense_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new expense"""
        return self._make_request('POST', '/api/expenses', json=expense_data)
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new contact"""
        return self._make_request('POST', '/api/contacts', json=contact_data)
    
    def get_accounts(self) -> Optional[List[Dict[str, Any]]]:
        """Get chart of accounts"""
        response = self._make_request('GET', '/api/accounts')
        return response.get('data', []) if response else []
    
    def get_customers(self) -> Optional[List[Dict[str, Any]]]:
        """Get customers"""
        response = self._make_request('GET', '/api/customers')
        return response.get('data', []) if response else []
    
    def get_vendors(self) -> Optional[List[Dict[str, Any]]]:
        """Get vendors"""
        response = self._make_request('GET', '/api/vendors')
        return response.get('data', []) if response else []
