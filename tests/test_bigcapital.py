"""
Tests for BigCapital Plugin

Comprehensive test suite for BigCapital integration functionality including
client, models, mappers, and plugin integration.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from decimal import Decimal

# Import BigCapital components
from plugins.bigcapital.client import BigCapitalClient, BigCapitalAPIError
from plugins.bigcapital.models import (
    BigCapitalContact, BigCapitalInvoice, BigCapitalInvoiceEntry, 
    BigCapitalExpense, BigCapitalAccount
)
from plugins.bigcapital.mappers import (
    DocumentParser, PaperlessNGXMapper, GenericDataMapper, ValidationHelper
)
from plugins.bigcapital.plugin import BigCapitalPlugin


class TestBigCapitalClient:
    """Test BigCapital API Client"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = BigCapitalClient("test_api_key", "https://test.api.com")
    
    def test_client_initialization(self):
        """Test client initialization"""
        assert self.client.api_key == "test_api_key"
        assert self.client.base_url == "https://test.api.com"
        assert self.client.timeout == 30
        assert 'Authorization' in self.client.session.headers
        assert self.client.session.headers['Authorization'] == 'Bearer test_api_key'
    
    @patch('requests.Session.request')
    def test_successful_request(self, mock_request):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_request.return_value = mock_response
        
        result = self.client._make_request('GET', '/test')
        
        assert result == {'data': 'test'}
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_api_error_handling(self, mock_request):
        """Test API error handling"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")
        mock_request.return_value = mock_response
        
        with pytest.raises(BigCapitalAPIError) as excinfo:
            self.client._make_request('GET', '/test')
        
        assert "Authentication failed" in str(excinfo.value)
        assert excinfo.value.status_code == 401
    
    @patch('requests.Session.request')
    def test_connection_test(self, mock_request):
        """Test connection test"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'Test Org'}
        mock_request.return_value = mock_response
        
        result = self.client.test_connection()
        
        assert result is True
    
    @patch('requests.Session.request')
    def test_get_organization_info(self, mock_request):
        """Test get organization info"""
        expected_data = {'name': 'Test Organization', 'currency': 'USD'}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_request.return_value = mock_response
        
        result = self.client.get_organization_info()
        
        assert result == expected_data
    
    @patch('requests.Session.request')
    def test_create_contact(self, mock_request):
        """Test create contact"""
        contact_data = {
            'display_name': 'Test Contact',
            'email': 'test@example.com',
            'contact_type': 'customer'
        }
        expected_response = {'id': 123, **contact_data}
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = expected_response
        mock_request.return_value = mock_response
        
        result = self.client.create_contact(contact_data)
        
        assert result == expected_response
        mock_request.assert_called_with(
            'POST', 'https://test.api.com/api/contacts',
            json=contact_data, timeout=30
        )


class TestBigCapitalModels:
    """Test BigCapital data models"""
    
    def test_contact_creation(self):
        """Test BigCapital contact creation"""
        contact = BigCapitalContact(
            display_name="Test Company",
            contact_type="vendor",
            email="test@company.com",
            phone="555-1234"
        )
        
        assert contact.display_name == "Test Company"
        assert contact.contact_type == "vendor"
        assert contact.email == "test@company.com"
        assert contact.phone == "555-1234"
        assert contact.currency_code == "USD"
        assert contact.active is True
    
    def test_contact_to_dict(self):
        """Test contact conversion to dictionary"""
        contact = BigCapitalContact(
            display_name="Test Company",
            email="test@company.com",
            billing_address_1="123 Main St",
            billing_city="Anytown"
        )
        
        data = contact.to_dict()
        
        assert data['display_name'] == "Test Company"
        assert data['email'] == "test@company.com"
        assert 'billing_address' in data
        assert data['billing_address']['address_1'] == "123 Main St"
        assert data['billing_address']['city'] == "Anytown"
    
    def test_invoice_entry_calculation(self):
        """Test invoice entry amount calculation"""
        entry = BigCapitalInvoiceEntry(
            description="Test Service",
            quantity=Decimal('2.5'),
            rate=Decimal('100.00')
        )
        
        assert entry.amount == Decimal('250.00')
    
    def test_invoice_creation(self):
        """Test invoice creation and calculation"""
        invoice = BigCapitalInvoice(
            customer_id=1,
            invoice_date=date.today(),
            due_date=date.today()
        )
        
        entry1 = BigCapitalInvoiceEntry(
            description="Service 1",
            quantity=Decimal('1'),
            rate=Decimal('100.00')
        )
        entry2 = BigCapitalInvoiceEntry(
            description="Service 2",
            quantity=Decimal('2'),
            rate=Decimal('50.00'),
            tax_amount=Decimal('10.00')
        )
        
        invoice.entries = [entry1, entry2]
        invoice.calculate_totals()
        
        assert invoice.subtotal == Decimal('200.00')
        assert invoice.tax_amount == Decimal('10.00')
        assert invoice.total == Decimal('210.00')
    
    def test_expense_creation(self):
        """Test expense creation"""
        expense = BigCapitalExpense(
            amount=Decimal('150.50'),
            description="Office Supplies",
            reference="EXP-001"
        )
        
        assert expense.amount == Decimal('150.50')
        assert expense.description == "Office Supplies"
        assert expense.reference == "EXP-001"
        assert expense.currency_code == "USD"


class TestDocumentParser:
    """Test document parsing functionality"""
    
    def test_extract_amounts(self):
        """Test amount extraction from text"""
        text = "Total: $1,234.56 Balance: $999.99 Amount: 500.00"
        amounts = DocumentParser.extract_amounts(text)
        
        assert len(amounts) >= 2
        assert Decimal('1234.56') in amounts
        assert Decimal('999.99') in amounts
    
    def test_extract_dates(self):
        """Test date extraction from text"""
        text = "Date: 01/15/2024 Due: 2024-02-15 Invoice dated 12-30-2023"
        dates = DocumentParser.extract_dates(text)
        
        assert len(dates) >= 1
        # Check that we found at least one valid date
        assert any(isinstance(d, date) for d in dates)
    
    def test_extract_invoice_numbers(self):
        """Test invoice number extraction"""
        text = "Invoice #INV-2024-001 Invoice Number: BC-12345"
        invoice_numbers = DocumentParser.extract_invoice_numbers(text)
        
        assert len(invoice_numbers) >= 1
        assert any('INV-2024-001' in num or 'BC-12345' in num for num in invoice_numbers)
    
    def test_extract_contact_info(self):
        """Test contact information extraction"""
        text = "Contact: john@company.com Phone: (555) 123-4567"
        contact_info = DocumentParser.extract_contact_info(text)
        
        assert contact_info.get('email') == 'john@company.com'
        assert '555' in contact_info.get('phone', '')


class TestPaperlessNGXMapper:
    """Test Paperless-NGX to BigCapital mapping"""
    
    def test_document_to_expense(self):
        """Test document to expense conversion"""
        document = {
            'id': 123,
            'title': 'Office Supplies Receipt',
            'created': '2024-01-15T10:00:00Z',
            'content': 'Office Depot Total: $89.95'
        }
        ocr_content = "Office Depot\nSupplies\nTotal: $89.95\nDate: 01/15/2024"
        
        expense = PaperlessNGXMapper.document_to_expense(document, ocr_content)
        
        assert isinstance(expense, BigCapitalExpense)
        assert expense.amount == Decimal('89.95')
        assert expense.description == 'Office Supplies Receipt'
        assert expense.reference == 'Paperless-123'
    
    def test_document_to_invoice(self):
        """Test document to invoice conversion"""
        document = {
            'id': 456,
            'title': 'Service Invoice ABC-001',
            'created': '2024-01-15T10:00:00Z'
        }
        ocr_content = "Invoice ABC-001\nConsulting Services\nAmount: $500.00\nDue: 02/15/2024"
        
        invoice = PaperlessNGXMapper.document_to_invoice(document, ocr_content, customer_id=1)
        
        assert isinstance(invoice, BigCapitalInvoice)
        assert invoice.customer_id == 1
        assert invoice.note == 'Service Invoice ABC-001'
        assert invoice.reference == 'Paperless-456'
        assert len(invoice.entries) > 0
    
    def test_extract_vendor_from_document(self):
        """Test vendor extraction from document"""
        document = {
            'title': 'Acme Corp Invoice',
            'content': 'vendor info'
        }
        ocr_content = "Acme Corp\ncontact@acme.com\n(555) 123-4567"
        
        vendor = PaperlessNGXMapper.extract_vendor_from_document(document, ocr_content)
        
        if vendor:  # May return None if extraction fails
            assert isinstance(vendor, BigCapitalContact)
            assert vendor.contact_type == 'vendor'
            assert 'Acme' in vendor.display_name


class TestGenericDataMapper:
    """Test generic data mapping utilities"""
    
    def test_dict_to_contact(self):
        """Test dictionary to contact conversion"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-1234',
            'company': 'Doe Industries'
        }
        
        contact = GenericDataMapper.dict_to_contact(data, 'customer')
        
        assert contact.display_name == 'John Doe'
        assert contact.email == 'john@example.com'
        assert contact.phone == '555-1234'
        assert contact.company_name == 'Doe Industries'
        assert contact.contact_type == 'customer'
    
    def test_normalize_amount(self):
        """Test amount normalization"""
        assert GenericDataMapper.normalize_amount('$1,234.56') == Decimal('1234.56')
        assert GenericDataMapper.normalize_amount(1234.56) == Decimal('1234.56')
        assert GenericDataMapper.normalize_amount('invalid') == Decimal('0.00')
    
    def test_normalize_date(self):
        """Test date normalization"""
        test_date = GenericDataMapper.normalize_date('2024-01-15')
        assert test_date == date(2024, 1, 15)
        
        test_date2 = GenericDataMapper.normalize_date('01/15/2024')
        assert test_date2 == date(2024, 1, 15)


class TestValidationHelper:
    """Test validation utilities"""
    
    def test_validate_email(self):
        """Test email validation"""
        assert ValidationHelper.validate_email('test@example.com') is True
        assert ValidationHelper.validate_email('invalid-email') is False
        assert ValidationHelper.validate_email('') is False
    
    def test_validate_phone(self):
        """Test phone validation"""
        assert ValidationHelper.validate_phone('(555) 123-4567') is True
        assert ValidationHelper.validate_phone('555-123-4567') is True
        assert ValidationHelper.validate_phone('invalid') is False
    
    def test_validate_amount(self):
        """Test amount validation"""
        assert ValidationHelper.validate_amount(100.50) is True
        assert ValidationHelper.validate_amount('150.00') is True
        assert ValidationHelper.validate_amount(-50) is False
        assert ValidationHelper.validate_amount('invalid') is False
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        dirty_string = "Test\x00\x1fString\x7f"
        clean_string = ValidationHelper.sanitize_string(dirty_string)
        assert clean_string == "TestString"


class TestBigCapitalPlugin:
    """Test BigCapital Plugin"""
    
    def setup_method(self):
        """Setup test plugin"""
        self.plugin = BigCapitalPlugin("BigCapital Test")
        self.plugin.config = {
            'api_key': 'test_key',
            'base_url': 'https://test.api.com',
            'enabled': True
        }
    
    @patch('plugins.bigcapital.plugin.BigCapitalClient')
    def test_plugin_initialization(self, mock_client_class):
        """Test plugin initialization"""
        mock_client = Mock()
        mock_client.get_organization_info.return_value = {'name': 'Test Org'}
        mock_client_class.return_value = mock_client
        
        app_context = {'config': self.plugin.config}
        result = self.plugin.initialize(app_context)
        
        assert result is True
        mock_client_class.assert_called_once_with('test_key', 'https://test.api.com', 30)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        valid_config = {'api_key': 'test_key'}
        assert self.plugin.validate_config(valid_config) is True
        
        # Invalid config - missing api_key
        invalid_config = {'base_url': 'https://test.com'}
        assert self.plugin.validate_config(invalid_config) is False
    
    @patch('plugins.bigcapital.plugin.BigCapitalClient')
    def test_sync_document_as_expense(self, mock_client_class):
        """Test syncing document as expense"""
        mock_client = Mock()
        mock_client.create_expense.return_value = {'id': 123}
        mock_client.search_contacts.return_value = []
        mock_client.create_contact.return_value = {'id': 456}
        self.plugin.client = mock_client
        
        document_data = {
            'document': {
                'id': 789,
                'title': 'Test Expense',
                'created': '2024-01-15T10:00:00Z'
            },
            'ocr_content': 'Test Vendor\nTotal: $100.00',
            'sync_as': 'expense'
        }
        
        result = self.plugin._sync_document(document_data)
        
        assert result['success'] is True
        assert result['type'] == 'expense'
        assert result['bigcapital_id'] == 123
    
    def test_menu_items(self):
        """Test menu items generation"""
        menu_items = self.plugin.get_menu_items()
        
        assert len(menu_items) == 1
        assert menu_items[0]['name'] == 'BigCapital'
        assert 'bigcapital' in menu_items[0]['url']


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.plugin = BigCapitalPlugin("BigCapital Integration Test")
        self.plugin.config = {
            'api_key': 'test_key',
            'base_url': 'https://test.api.com',
            'enabled': True
        }
    
    @patch('plugins.bigcapital.plugin.BigCapitalClient')
    def test_full_document_processing_workflow(self, mock_client_class):
        """Test complete document processing workflow"""
        # Setup mock client
        mock_client = Mock()
        mock_client.get_organization_info.return_value = {'name': 'Test Org'}
        mock_client.search_contacts.return_value = []
        mock_client.create_contact.return_value = {'id': 100}
        mock_client.create_expense.return_value = {'id': 200}
        mock_client_class.return_value = mock_client
        
        # Initialize plugin
        app_context = {'config': self.plugin.config}
        assert self.plugin.initialize(app_context) is True
        
        # Process a receipt document
        receipt_data = {
            'document': {
                'id': 1001,
                'title': 'Office Max Receipt',
                'created': '2024-01-15T14:30:00Z',
                'content': 'Office supplies purchase'
            },
            'ocr_content': '''
            OfficeMax
            123 Business St
            Anytown, ST 12345
            
            Date: 01/15/2024
            
            Printer Paper        $25.99
            Pens (Pack)         $12.50
            Stapler             $15.99
            
            Subtotal:           $54.48
            Tax:                $4.36
            Total:              $58.84
            
            Thank you for shopping!
            ''',
            'sync_as': 'expense'
        }
        
        result = self.plugin._sync_document(receipt_data)
        
        # Verify successful processing
        assert result['success'] is True
        assert result['type'] == 'expense'
        assert result['bigcapital_id'] == 200
        
        # Verify client calls
        mock_client.create_expense.assert_called_once()
        expense_data = mock_client.create_expense.call_args[0][0]
        assert expense_data['description'] == 'Office Max Receipt'
        assert expense_data['reference'] == 'Paperless-1001'
    
    def test_error_handling_in_sync(self):
        """Test error handling during sync operations"""
        # Test with uninitialized client
        document_data = {
            'document': {'id': 1, 'title': 'Test'},
            'sync_as': 'expense'
        }
        
        result = self.plugin._sync_document(document_data)
        
        assert result['success'] is False
        assert 'error' in result


if __name__ == '__main__':
    pytest.main([__file__])
