"""
BigCapital Data Mappers

This module contains mappers to transform data between various document sources
(like Paperless-NGX) and BigCapital API format.
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from loguru import logger

from .models import (
    BigCapitalContact, BigCapitalInvoice, BigCapitalInvoiceEntry, 
    BigCapitalExpense, create_contact_from_dict
)


class DocumentParser:
    """Parse OCR content to extract financial data"""
    
    # Common patterns for extracting financial information
    AMOUNT_PATTERNS = [
        r'total[:\s]+\$?([0-9,]+\.?[0-9]*)',
        r'amount[:\s]+\$?([0-9,]+\.?[0-9]*)',
        r'balance[:\s]+\$?([0-9,]+\.?[0-9]*)',
        r'\$([0-9,]+\.?[0-9]*)',
        r'([0-9,]+\.?[0-9]*)\s*(?:usd|dollars?)',
    ]
    
    DATE_PATTERNS = [
        r'(?:date|dated?)[:\s]+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
        r'([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
        r'([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})',
    ]
    
    INVOICE_NUMBER_PATTERNS = [
        r'invoice\s*#?[:\s]*([A-Z0-9-]+)',
        r'inv\s*#?[:\s]*([A-Z0-9-]+)',
        r'number[:\s]+([A-Z0-9-]+)',
    ]
    
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
    
    @staticmethod
    def extract_amounts(text: str) -> List[Decimal]:
        """Extract monetary amounts from text"""
        amounts = []
        text_lower = text.lower()
        
        for pattern in DocumentParser.AMOUNT_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove commas and convert to decimal
                    amount_str = match.replace(',', '')
                    amount = Decimal(amount_str)
                    amounts.append(amount)
                except (InvalidOperation, ValueError):
                    continue
        
        # Remove duplicates and sort
        unique_amounts = list(set(amounts))
        unique_amounts.sort(reverse=True)
        return unique_amounts
    
    @staticmethod
    def extract_dates(text: str) -> List[date]:
        """Extract dates from text"""
        dates = []
        
        for pattern in DocumentParser.DATE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Try different date formats
                    date_formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y']
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(match, fmt).date()
                            dates.append(parsed_date)
                            break
                        except ValueError:
                            continue
                except Exception:
                    continue
        
        # Remove duplicates and sort
        unique_dates = list(set(dates))
        unique_dates.sort()
        return unique_dates
    
    @staticmethod
    def extract_invoice_numbers(text: str) -> List[str]:
        """Extract invoice numbers from text"""
        invoice_numbers = []
        
        for pattern in DocumentParser.INVOICE_NUMBER_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            invoice_numbers.extend(matches)
        
        return list(set(invoice_numbers))  # Remove duplicates
    
    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, Any]:
        """Extract contact information from text"""
        contact_info = {}
        
        # Extract email
        email_matches = re.findall(DocumentParser.EMAIL_PATTERN, text)
        if email_matches:
            contact_info['email'] = email_matches[0]
        
        # Extract phone
        phone_matches = re.findall(DocumentParser.PHONE_PATTERN, text)
        if phone_matches:
            contact_info['phone'] = phone_matches[0]
        
        return contact_info


class PaperlessNGXMapper:
    """Map Paperless-NGX documents to BigCapital entities"""
    
    @staticmethod
    def document_to_expense(document: Dict[str, Any], ocr_content: str = None) -> BigCapitalExpense:
        """Convert Paperless-NGX document to BigCapital expense"""
        try:
            # Extract basic information
            title = document.get('title', '')
            created_date = document.get('created', '')
            content = ocr_content or document.get('content', '')
            
            # Parse OCR content for financial data
            amounts = DocumentParser.extract_amounts(content)
            dates = DocumentParser.extract_dates(content)
            
            # Use the largest amount as expense amount
            expense_amount = amounts[0] if amounts else Decimal('0.00')
            
            # Use the most recent date or document created date
            expense_date = dates[0] if dates else date.today()
            if isinstance(created_date, str):
                try:
                    expense_date = datetime.fromisoformat(created_date.replace('Z', '+00:00')).date()
                except ValueError:
                    expense_date = date.today()
            
            # Create expense object
            expense = BigCapitalExpense(
                payment_date=expense_date,
                amount=expense_amount,
                description=title,
                reference=f"Paperless-{document.get('id', '')}"
            )
            
            # Try to extract vendor information
            contact_info = DocumentParser.extract_contact_info(content)
            if contact_info:
                # This would need to be matched against existing vendors
                # or create a new vendor - handled in the plugin
                expense.description += f" - Contact: {contact_info.get('email', '')}"
            
            return expense
            
        except Exception as e:
            logger.error(f"Failed to convert document to expense: {e}")
            # Return minimal expense
            return BigCapitalExpense(
                amount=Decimal('0.00'),
                description=document.get('title', 'Unknown Document'),
                reference=f"Paperless-{document.get('id', '')}"
            )
    
    @staticmethod
    def document_to_invoice(document: Dict[str, Any], ocr_content: str = None, customer_id: int = None) -> BigCapitalInvoice:
        """Convert Paperless-NGX document to BigCapital invoice"""
        try:
            # Extract basic information
            title = document.get('title', '')
            created_date = document.get('created', '')
            content = ocr_content or document.get('content', '')
            
            # Parse OCR content for financial data
            amounts = DocumentParser.extract_amounts(content)
            dates = DocumentParser.extract_dates(content)
            invoice_numbers = DocumentParser.extract_invoice_numbers(content)
            
            # Use dates for invoice and due date
            invoice_date = dates[0] if dates else date.today()
            due_date = dates[1] if len(dates) > 1 else date.today()
            
            if isinstance(created_date, str):
                try:
                    invoice_date = datetime.fromisoformat(created_date.replace('Z', '+00:00')).date()
                except ValueError:
                    pass
            
            # Create invoice object
            invoice = BigCapitalInvoice(
                customer_id=customer_id or 1,  # Default customer
                invoice_date=invoice_date,
                due_date=due_date,
                invoice_number=invoice_numbers[0] if invoice_numbers else None,
                note=title,
                reference=f"Paperless-{document.get('id', '')}"
            )
            
            # Create invoice entries from amounts
            for i, amount in enumerate(amounts[:5]):  # Limit to 5 line items
                entry = BigCapitalInvoiceEntry(
                    description=f"Line item {i+1}" if len(amounts) > 1 else title,
                    quantity=Decimal('1.00'),
                    rate=amount,
                    amount=amount
                )
                invoice.entries.append(entry)
            
            # If no amounts found, create a placeholder entry
            if not invoice.entries:
                entry = BigCapitalInvoiceEntry(
                    description=title,
                    quantity=Decimal('1.00'),
                    rate=Decimal('0.00'),
                    amount=Decimal('0.00')
                )
                invoice.entries.append(entry)
            
            return invoice
            
        except Exception as e:
            logger.error(f"Failed to convert document to invoice: {e}")
            # Return minimal invoice
            invoice = BigCapitalInvoice(
                customer_id=customer_id or 1,
                invoice_date=date.today(),
                due_date=date.today(),
                note=document.get('title', 'Unknown Document'),
                reference=f"Paperless-{document.get('id', '')}"
            )
            # Add placeholder entry
            entry = BigCapitalInvoiceEntry(
                description=document.get('title', 'Unknown Document'),
                quantity=Decimal('1.00'),
                rate=Decimal('0.00'),
                amount=Decimal('0.00')
            )
            invoice.entries.append(entry)
            return invoice
    
    @staticmethod
    def extract_vendor_from_document(document: Dict[str, Any], ocr_content: str = None) -> Optional[BigCapitalContact]:
        """Extract vendor/contact information from document"""
        try:
            content = ocr_content or document.get('content', '')
            contact_info = DocumentParser.extract_contact_info(content)
            
            if not contact_info:
                return None
            
            # Try to extract company/vendor name from title or content
            title = document.get('title', '')
            
            # Simple heuristics to extract vendor name
            vendor_name = None
            title_parts = title.split()
            
            # Look for common business indicators
            business_indicators = ['inc', 'llc', 'corp', 'ltd', 'company', 'co', 'services', 'group']
            for part in title_parts:
                if part.lower() in business_indicators and len(title_parts) > 1:
                    # Take the part before the business indicator
                    idx = title_parts.index(part)
                    if idx > 0:
                        vendor_name = ' '.join(title_parts[:idx+1])
                    break
            
            if not vendor_name:
                # Fallback to first few words of title
                vendor_name = ' '.join(title_parts[:3]) if title_parts else 'Unknown Vendor'
            
            contact = BigCapitalContact(
                display_name=vendor_name,
                contact_type='vendor',
                email=contact_info.get('email'),
                phone=contact_info.get('phone'),
                company_name=vendor_name
            )
            
            return contact
            
        except Exception as e:
            logger.error(f"Failed to extract vendor from document: {e}")
            return None


class GenericDataMapper:
    """Generic data mapper for various data sources"""
    
    @staticmethod
    def dict_to_contact(data: Dict[str, Any], contact_type: str = 'customer') -> BigCapitalContact:
        """Convert dictionary data to BigCapital contact"""
        # Map common field variations
        field_mappings = {
            'name': ['name', 'display_name', 'full_name', 'company_name'],
            'first_name': ['first_name', 'fname'],
            'last_name': ['last_name', 'lname', 'surname'],
            'email': ['email', 'email_address', 'mail'],
            'phone': ['phone', 'phone_number', 'tel', 'telephone'],
            'company': ['company', 'company_name', 'organization', 'business_name'],
            'website': ['website', 'web', 'url', 'homepage'],
        }
        
        mapped_data = {'contact_type': contact_type}
        
        for target_field, source_fields in field_mappings.items():
            for source_field in source_fields:
                if source_field in data and data[source_field]:
                    if target_field == 'name':
                        mapped_data['display_name'] = data[source_field]
                    elif target_field == 'company':
                        mapped_data['company_name'] = data[source_field]
                    else:
                        mapped_data[target_field] = data[source_field]
                    break
        
        # Ensure display_name is set
        if 'display_name' not in mapped_data:
            if mapped_data.get('company_name'):
                mapped_data['display_name'] = mapped_data['company_name']
            elif mapped_data.get('first_name') and mapped_data.get('last_name'):
                mapped_data['display_name'] = f"{mapped_data['first_name']} {mapped_data['last_name']}"
            elif mapped_data.get('first_name'):
                mapped_data['display_name'] = mapped_data['first_name']
            else:
                mapped_data['display_name'] = 'Unknown Contact'
        
        return create_contact_from_dict(mapped_data)
    
    @staticmethod
    def normalize_amount(value: Any) -> Decimal:
        """Normalize various amount formats to Decimal"""
        if isinstance(value, Decimal):
            return value
        
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        
        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.-]', '', value)
            try:
                return Decimal(cleaned)
            except (InvalidOperation, ValueError):
                return Decimal('0.00')
        
        return Decimal('0.00')
    
    @staticmethod
    def normalize_date(value: Any) -> date:
        """Normalize various date formats to date object"""
        if isinstance(value, date):
            return value
        
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, str):
            # Try common date formats
            formats = [
                '%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y',
                '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            
            # Try ISO format with timezone
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
            except ValueError:
                pass
        
        # Fallback to today
        return date.today()


class ValidationHelper:
    """Helper class for data validation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        return bool(re.match(DocumentParser.EMAIL_PATTERN, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        return bool(re.match(DocumentParser.PHONE_PATTERN, phone))
    
    @staticmethod
    def validate_amount(amount: Any) -> bool:
        """Validate that amount is positive and valid"""
        try:
            # First check if it's a valid numeric value
            if isinstance(amount, str):
                # Remove currency symbols and commas for validation
                cleaned = re.sub(r'[^\d.-]', '', amount)
                if not cleaned or cleaned in ['-', '.', '-.']:
                    return False
                try:
                    float(cleaned)
                except ValueError:
                    return False
            elif not isinstance(amount, (int, float, Decimal)):
                return False
            
            decimal_amount = GenericDataMapper.normalize_amount(amount)
            return decimal_amount >= 0
        except Exception:
            return False
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not value:
            return ""
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(value))
        
        # Trim to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].strip()
        
        return sanitized.strip()
