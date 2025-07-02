"""
Comprehensive tests for BigCapital Plugin

Test coverage for models, mappers, client, and plugin functionality.
"""
import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, Any, List

# Import the modules we're testing
from plugins.bigcapital.models import (
    BigCapitalContact, BigCapitalInvoice, BigCapitalInvoiceEntry,
    BigCapitalExpense, BigCapitalAccount, BigCapitalOrganization,
    create_contact_from_dict, create_invoice_from_dict, create_expense_from_dict
)
from plugins.bigcapital.mappers import (
    DocumentParser, PaperlessNGXMapper, GenericDataMapper, ValidationHelper
)
from plugins.bigcapital.client import BigCapitalClient, BigCapitalAPIError
from plugins.bigcapital.plugin import BigCapitalPlugin


class TestBigCapitalModels(unittest.TestCase):
    """Test BigCapital data models"""
    
    def test_bigcapital_contact_creation(self):
        """Test BigCapitalContact model creation and validation"""
        contact = BigCapitalContact(
            display_name="Test Company",
            contact_type="vendor",
            email="test@company.com",
            phone="555-1234"
        )
        
        self.assertEqual(contact.display_name, "Test Company")
        self.assertEqual(contact.contact_type, "vendor")
        self.assertEqual(contact.email, "test@company.com")
        self.assertEqual(contact.phone, "555-1234")
        self.assertTrue(contact.active)
        self.assertEqual(contact.currency_code, "USD")
    
    def test_bigcapital_contact_to_dict(self):
        """Test BigCapitalContact to_dict conversion"""
        contact = BigCapitalContact(
            display_name="Test Vendor",
            contact_type="vendor",
            email="vendor@test.com",
            billing_address_1="123 Main St",
            billing_city="Test City"
        )
        
        contact_dict = contact.to_dict()
        
        self.assertIn('display_name', contact_dict)
        self.assertIn('contact_type', contact_dict)
        self.assertIn('email', contact_dict)
        self.assertIn('billing_address', contact_dict)
        self.assertEqual(contact_dict['billing_address']['address_1'], "123 Main St")
        self.assertEqual(contact_dict['billing_address']['city'], "Test City")
    
    def test_bigcapital_invoice_entry(self):
        """Test BigCapitalInvoiceEntry model"""
        entry = BigCapitalInvoiceEntry(
            description="Test Item",
            quantity=Decimal('2.0'),
            rate=Decimal('100.0')
        )
        
        self.assertEqual(entry.description, "Test Item")
        self.assertEqual(entry.quantity, Decimal('2.0'))
        self.assertEqual(entry.rate, Decimal('100.0'))
        self.assertEqual(entry.amount, Decimal('200.0'))  # Auto-calculated
    
    def test_bigcapital_invoice_creation(self):
        """Test BigCapitalInvoice model creation"""
        invoice = BigCapitalInvoice(
            customer_id=1,
            invoice_date=date(2024, 1, 15),
            due_date=date(2024, 2, 15)
        )
        
        # Add line items
        entry1 = BigCapitalInvoiceEntry(
            description="Service 1",
            quantity=Decimal('1.0'),
            rate=Decimal('500.0')
        )
        entry2 = BigCapitalInvoiceEntry(
            description="Service 2",
            quantity=Decimal('2.0'),
            rate=Decimal('150.0')
        )
        
        invoice.entries = [entry1, entry2]
        invoice.calculate_totals()
        
        self.assertEqual(invoice.customer_id, 1)
        self.assertEqual(invoice.subtotal, Decimal('800.0'))
        self.assertEqual(invoice.total, Decimal('800.0'))  # No tax/adjustments
    
    def test_bigcapital_expense_creation(self):
        """Test BigCapitalExpense model creation"""
        expense = BigCapitalExpense(
            amount=Decimal('250.75'),
            description="Office supplies",
            payment_date=date(2024, 1, 10)
        )
        
        self.assertEqual(expense.amount, Decimal('250.75'))
        self.assertEqual(expense.description, "Office supplies")
        self.assertEqual(expense.payment_date, date(2024, 1, 10))
        self.assertEqual(expense.currency_code, "USD")
    
    def test_create_contact_from_dict(self):
        """Test helper function for creating contact from dictionary"""
        contact_data = {
            'display_name': 'John Doe',
            'email': 'john@example.com',
            'contact_type': 'customer',
            'phone': '555-0123'
        }
        
        contact = create_contact_from_dict(contact_data)
        
        self.assertIsInstance(contact, BigCapitalContact)
        self.assertEqual(contact.display_name, 'John Doe')
        self.assertEqual(contact.email, 'john@example.com')
        self.assertEqual(contact.contact_type, 'customer')


class TestDocumentParser(unittest.TestCase):
    """Test DocumentParser functionality"""
    
    def test_extract_amounts(self):
        """Test amount extraction from text"""
        test_text = "Invoice total: $1,250.00 Amount due: $1250.00 Balance $500"
        amounts = DocumentParser.extract_amounts(test_text)
        
        self.assertIn(Decimal('1250.00'), amounts)
        self.assertIn(Decimal('500'), amounts)
    
    def test_extract_dates(self):
        """Test date extraction from text"""
        test_text = "Invoice Date: 01/15/2024 Due Date: 2024-02-15"
        dates = DocumentParser.extract_dates(test_text)
        
        self.assertTrue(len(dates) >= 1)
        # Should find at least one valid date
    
    def test_extract_invoice_numbers(self):
        """Test invoice number extraction"""
        test_text = "Invoice #INV-2024-001 Invoice Number: 12345"
        numbers = DocumentParser.extract_invoice_numbers(test_text)
        
        self.assertIn('INV-2024-001', numbers)
        self.assertIn('12345', numbers)
    
    def test_extract_contact_info(self):
        """Test contact information extraction"""
        test_text = "Contact: john@company.com Phone: (555) 123-4567"
        contact_info = DocumentParser.extract_contact_info(test_text)
        
        self.assertEqual(contact_info.get('email'), 'john@company.com')
        self.assertIn('phone', contact_info)


class TestPaperlessNGXMapper(unittest.TestCase):
    """Test PaperlessNGX document mapping"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_document = {
            'id': 123,
            'title': 'Office Supplies Invoice - ABC Company',
            'created': '2024-01-15T10:30:00Z',
            'content': 'Invoice from ABC Company for office supplies'
        }
        
        self.sample_ocr_content = """
        ABC Company
        123 Business St
        Email: billing@abc.com
        Phone: (555) 123-4567
        
        Invoice #INV-2024-001
        Date: 01/15/2024
        
        Office supplies: $250.00
        Total: $250.00
        """
    
    def test_document_to_expense(self):
        """Test converting document to expense"""
        expense = PaperlessNGXMapper.document_to_expense(
            self.sample_document, 
            self.sample_ocr_content
        )
        
        self.assertIsInstance(expense, BigCapitalExpense)
        self.assertEqual(expense.amount, Decimal('250.00'))
        self.assertIn('Office Supplies Invoice', expense.description)
        self.assertEqual(expense.reference, 'Paperless-123')
    
    def test_document_to_invoice(self):
        """Test converting document to invoice"""
        invoice = PaperlessNGXMapper.document_to_invoice(
            self.sample_document,
            self.sample_ocr_content,
            customer_id=5
        )
        
        self.assertIsInstance(invoice, BigCapitalInvoice)
        self.assertEqual(invoice.customer_id, 5)
        self.assertEqual(invoice.reference, 'Paperless-123')
        self.assertTrue(len(invoice.entries) > 0)
    
    def test_extract_vendor_from_document(self):
        """Test vendor extraction from document"""
        vendor = PaperlessNGXMapper.extract_vendor_from_document(
            self.sample_document,
            self.sample_ocr_content
        )
        
        self.assertIsInstance(vendor, BigCapitalContact)
        self.assertEqual(vendor.contact_type, 'vendor')
        self.assertEqual(vendor.email, 'billing@abc.com')


class TestGenericDataMapper(unittest.TestCase):
    """Test GenericDataMapper functionality"""
    
    def test_dict_to_contact(self):
        """Test converting dictionary to contact"""
        contact_data = {
            'name': 'Test Company',
            'email': 'test@company.com',
            'phone': '555-1234',
            'company_name': 'Test Company Inc'
        }
        
        contact = GenericDataMapper.dict_to_contact(contact_data, 'vendor')
        
        self.assertIsInstance(contact, BigCapitalContact)
        self.assertEqual(contact.contact_type, 'vendor')
        self.assertEqual(contact.display_name, 'Test Company')
        self.assertEqual(contact.email, 'test@company.com')
    
    def test_normalize_amount(self):
        """Test amount normalization"""
        # Test various formats
        self.assertEqual(GenericDataMapper.normalize_amount('$1,250.00'), Decimal('1250.00'))
        self.assertEqual(GenericDataMapper.normalize_amount(1250), Decimal('1250'))
        self.assertEqual(GenericDataMapper.normalize_amount(Decimal('500.75')), Decimal('500.75'))
        self.assertEqual(GenericDataMapper.normalize_amount('invalid'), Decimal('0.00'))
    
    def test_normalize_date(self):
        """Test date normalization"""
        # Test various date formats
        test_date = GenericDataMapper.normalize_date('2024-01-15')
        self.assertEqual(test_date, date(2024, 1, 15))
        
        test_date = GenericDataMapper.normalize_date('01/15/2024')
        self.assertEqual(test_date, date(2024, 1, 15))


class TestValidationHelper(unittest.TestCase):
    """Test ValidationHelper functionality"""
    
    def test_validate_email(self):
        """Test email validation"""
        self.assertTrue(ValidationHelper.validate_email('test@example.com'))
        self.assertTrue(ValidationHelper.validate_email('user.name+tag@domain.co.uk'))
        self.assertFalse(ValidationHelper.validate_email('invalid-email'))
        self.assertFalse(ValidationHelper.validate_email(''))
    
    def test_validate_phone(self):
        """Test phone validation"""
        self.assertTrue(ValidationHelper.validate_phone('(555) 123-4567'))
        self.assertTrue(ValidationHelper.validate_phone('555-123-4567'))
        self.assertTrue(ValidationHelper.validate_phone('5551234567'))
        self.assertFalse(ValidationHelper.validate_phone('invalid'))
        self.assertFalse(ValidationHelper.validate_phone(''))
    
    def test_validate_amount(self):
        """Test amount validation"""
        self.assertTrue(ValidationHelper.validate_amount(100))
        self.assertTrue(ValidationHelper.validate_amount('250.50'))
        self.assertTrue(ValidationHelper.validate_amount(Decimal('75.25')))
        self.assertFalse(ValidationHelper.validate_amount(-50))
        self.assertFalse(ValidationHelper.validate_amount('invalid'))
        self.assertFalse(ValidationHelper.validate_amount(''))
        self.assertFalse(ValidationHelper.validate_amount(None))
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        # Test control character removal
        sanitized = ValidationHelper.sanitize_string('Test\x00String\x1f')
        self.assertEqual(sanitized, 'TestString')
        
        # Test length limiting
        long_string = 'a' * 300
        sanitized = ValidationHelper.sanitize_string(long_string, max_length=255)
        self.assertEqual(len(sanitized), 255)


class TestBigCapitalClient(unittest.TestCase):
    """Test BigCapitalClient functionality"""
    
    def setUp(self):
        """Set up test client"""
        self.client = BigCapitalClient(
            api_key='test_api_key',
            base_url='https://api.test.com'
        )
    
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': []}
        mock_request.return_value = mock_response
        
        result = self.client._make_request('GET', '/test')
        
        self.assertEqual(result, {'success': True, 'data': []})
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_make_request_error(self, mock_request):
        """Test API request error handling"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")
        mock_request.return_value = mock_response
        
        with self.assertRaises(BigCapitalAPIError):
            self.client._make_request('GET', '/test')
    
    @patch.object(BigCapitalClient, '_make_request')
    def test_get_organization_info(self, mock_request):
        """Test getting organization info"""
        mock_request.return_value = {'name': 'Test Org', 'id': 1}
        
        result = self.client.get_organization_info()
        
        self.assertEqual(result['name'], 'Test Org')
        mock_request.assert_called_with('GET', '/api/organization')
    
    @patch.object(BigCapitalClient, '_make_request')
    def test_get_contacts(self, mock_request):
        """Test getting contacts"""
        mock_request.return_value = {'data': [{'id': 1, 'name': 'Test Contact'}]}
        
        result = self.client.get_contacts()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Test Contact')
    
    @patch.object(BigCapitalClient, '_make_request')
    def test_create_contact(self, mock_request):
        """Test creating contact"""
        mock_request.return_value = {'id': 123, 'name': 'New Contact'}
        
        contact_data = {'name': 'New Contact', 'email': 'new@test.com'}
        result = self.client.create_contact(contact_data)
        
        self.assertEqual(result['id'], 123)
        mock_request.assert_called_with('POST', '/api/contacts', json=contact_data)


class TestBigCapitalPlugin(unittest.TestCase):
    """Test BigCapitalPlugin functionality"""
    
    def setUp(self):
        """Set up test plugin"""
        self.plugin = BigCapitalPlugin('bigcapital')
        self.plugin.config = {
            'api_key': 'test_key',
            'base_url': 'https://api.test.com',
            'enabled': True
        }
    
    def test_validate_config(self):
        """Test configuration validation"""
        # Valid config
        valid_config = {'api_key': 'test_key'}
        self.assertTrue(self.plugin.validate_config(valid_config))
        
        # Invalid config - missing api_key
        invalid_config = {'base_url': 'test'}
        self.assertFalse(self.plugin.validate_config(invalid_config))
    
    @patch.object(BigCapitalClient, 'get_organization_info')
    def test_test_connection_success(self, mock_org_info):
        """Test successful connection test"""
        mock_org_info.return_value = {'name': 'Test Org'}
        
        # Initialize client
        self.plugin.client = BigCapitalClient('test_key', 'https://api.test.com')
        
        result = self.plugin.test_connection()
        self.assertTrue(result)
    
    @patch.object(BigCapitalClient, 'get_organization_info')
    def test_test_connection_failure(self, mock_org_info):
        """Test failed connection test"""
        mock_org_info.side_effect = BigCapitalAPIError("Connection failed")
        
        # Initialize client
        self.plugin.client = BigCapitalClient('test_key', 'https://api.test.com')
        
        result = self.plugin.test_connection()
        self.assertFalse(result)
    
    def test_sync_data_invalid_type(self):
        """Test sync with invalid type"""
        data = {'type': 'invalid_type'}
        
        # Initialize client to avoid early failure
        self.plugin.client = Mock()
        
        result = self.plugin.sync_data(data)
        
        self.assertFalse(result['success'])
        self.assertIn('Unsupported sync type', result['error'])
    
    def test_validate_invoice_data(self):
        """Test invoice data validation"""
        # Valid invoice data
        valid_data = {
            'customer_id': 1,
            'line_items': [{'amount': 100, 'description': 'Test'}]
        }
        self.assertTrue(self.plugin._validate_invoice_data(valid_data))
        
        # Invalid - missing customer_id
        invalid_data = {'line_items': [{'amount': 100}]}
        self.assertFalse(self.plugin._validate_invoice_data(invalid_data))
        
        # Invalid - no line items
        invalid_data = {'customer_id': 1, 'line_items': []}
        self.assertFalse(self.plugin._validate_invoice_data(invalid_data))
    
    def test_validate_expense_data(self):
        """Test expense data validation"""
        # Valid expense data
        valid_data = {
            'amount': 250.50,
            'payment_account_id': 1
        }
        self.assertTrue(self.plugin._validate_expense_data(valid_data))
        
        # Invalid - missing amount
        invalid_data = {'payment_account_id': 1}
        self.assertFalse(self.plugin._validate_expense_data(invalid_data))
    
    def test_validate_contact_data(self):
        """Test contact data validation"""
        # Valid contact data
        valid_data = {
            'display_name': 'Test Contact',
            'email': 'test@example.com'
        }
        self.assertTrue(self.plugin._validate_contact_data(valid_data))
        
        # Invalid - missing display_name
        invalid_data = {'email': 'test@example.com'}
        self.assertFalse(self.plugin._validate_contact_data(invalid_data))
        
        # Invalid - bad email format
        invalid_data = {
            'display_name': 'Test',
            'email': 'invalid-email'
        }
        self.assertFalse(self.plugin._validate_contact_data(invalid_data))


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
