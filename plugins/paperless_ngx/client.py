"""
Paperless-NGX API Client
Helper classes for interacting with Paperless-NGX API
"""

import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin
import json


class PaperlessNGXClient:
    """HTTP client for Paperless-NGX API"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        })
        
        self.logger = logging.getLogger(__name__)
    
    def get(self, endpoint: str, params: Dict[str, Any] = None) -> requests.Response:
        """Make GET request"""
        return self._request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Dict[str, Any] = None, files: Dict[str, Any] = None) -> requests.Response:
        """Make POST request"""
        if files:
            # Remove Content-Type header for file uploads
            headers = self.session.headers.copy()
            if 'Content-Type' in headers:
                del headers['Content-Type']
            return self._request('POST', endpoint, data=data, files=files, headers=headers)
        return self._request('POST', endpoint, json=data)
    
    def put(self, endpoint: str, data: Dict[str, Any] = None) -> requests.Response:
        """Make PUT request"""
        return self._request('PUT', endpoint, json=data)
    
    def patch(self, endpoint: str, data: Dict[str, Any] = None) -> requests.Response:
        """Make PATCH request"""
        return self._request('PATCH', endpoint, json=data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """Make DELETE request"""
        return self._request('DELETE', endpoint)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request"""
        url = urljoin(self.base_url, endpoint)
        kwargs.setdefault('timeout', self.timeout)
        
        # Use custom headers if provided, otherwise use session headers
        if 'headers' not in kwargs:
            kwargs['headers'] = self.session.headers
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.get('/api/documents/', params={'page_size': 1})
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False


class PaperlessNGXDocument:
    """Document model for Paperless-NGX"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.id = data.get('id')
        self.title = data.get('title', '')
        self.content = data.get('content', '')
        self.created = self._parse_datetime(data.get('created'))
        self.modified = self._parse_datetime(data.get('modified'))
        self.added = self._parse_datetime(data.get('added'))
        self.correspondent = data.get('correspondent')
        self.document_type = data.get('document_type')
        self.tags = data.get('tags', [])
        self.archive_serial_number = data.get('archive_serial_number')
        self.original_file_name = data.get('original_file_name', '')
        self.archived_file_name = data.get('archived_file_name', '')
    
    def _parse_datetime(self, dt_string: str) -> Optional[datetime]:
        """Parse datetime string"""
        if not dt_string:
            return None
        try:
            # Handle timezone info
            if dt_string.endswith('Z'):
                dt_string = dt_string[:-1] + '+00:00'
            return datetime.fromisoformat(dt_string)
        except (ValueError, TypeError):
            return None
    
    @property
    def created_date(self) -> Optional[str]:
        """Get formatted creation date"""
        return self.created.strftime('%Y-%m-%d') if self.created else None
    
    @property
    def created_datetime(self) -> Optional[str]:
        """Get formatted creation datetime"""
        return self.created.strftime('%Y-%m-%d %H:%M:%S') if self.created else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created': self.created.isoformat() if self.created else None,
            'created_date': self.created_date,
            'created_datetime': self.created_datetime,
            'modified': self.modified.isoformat() if self.modified else None,
            'added': self.added.isoformat() if self.added else None,
            'correspondent': self.correspondent,
            'document_type': self.document_type,
            'tags': self.tags,
            'archive_serial_number': self.archive_serial_number,
            'original_file_name': self.original_file_name,
            'archived_file_name': self.archived_file_name
        }


class PaperlessNGXPagination:
    """Pagination helper for Paperless-NGX API responses"""
    
    def __init__(self, data: Dict[str, Any], page: int = 1, page_size: int = 25):
        self.count = data.get('count', 0)
        self.next = data.get('next')
        self.previous = data.get('previous')
        self.page = page
        self.page_size = page_size
        self.results = data.get('results', [])
    
    @property
    def total_pages(self) -> int:
        """Calculate total pages"""
        if self.count == 0:
            return 0
        return (self.count + self.page_size - 1) // self.page_size
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page"""
        return self.next is not None
    
    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page"""
        return self.previous is not None
    
    @property
    def prev_num(self) -> Optional[int]:
        """Get previous page number"""
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_num(self) -> Optional[int]:
        """Get next page number"""
        return self.page + 1 if self.has_next else None
    
    def iter_pages(self, left_edge: int = 2, right_edge: int = 2, left_current: int = 2, right_current: int = 3) -> List[Optional[int]]:
        """Iterate over page numbers for pagination display"""
        last = self.total_pages
        pages = []
        
        # Left edge
        for num in range(1, min(left_edge + 1, last + 1)):
            pages.append(num)
        
        # Gap before current
        left_gap = self.page - left_current
        if left_gap > left_edge + 1:
            pages.append(None)
            
        # Around current page
        for num in range(max(left_gap, 1), min(self.page + right_current + 1, last + 1)):
            if num not in pages:
                pages.append(num)
        
        # Gap after current
        right_gap = self.page + right_current
        if right_gap < last - right_edge:
            pages.append(None)
            
        # Right edge
        for num in range(max(right_gap + 1, last - right_edge + 1), last + 1):
            if num not in pages:
                pages.append(num)
        
        return pages
    
    @property
    def total(self) -> int:
        """Total number of items (alias for count)"""
        return self.count


class PaperlessNGXError(Exception):
    """Custom exception for Paperless-NGX related errors"""
    pass


class PaperlessNGXConnectionError(PaperlessNGXError):
    """Exception for connection-related errors"""
    pass


class PaperlessNGXAuthenticationError(PaperlessNGXError):
    """Exception for authentication-related errors"""
    pass
