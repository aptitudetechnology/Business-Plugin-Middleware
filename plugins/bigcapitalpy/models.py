"""
BigCapital Data Models

This module contains data models for BigCapital entities to ensure proper
data structure and validation when working with the BigCapital API.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal


@dataclass
class BigCapitalContact:
    """BigCapital Contact/Customer/Vendor model"""
    display_name: str
    contact_type: str = "customer"  # customer, vendor, employee
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    fax: Optional[str] = None
    
    # Address fields
    billing_address_1: Optional[str] = None
    billing_address_2: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_postal_code: Optional[str] = None
    billing_country: Optional[str] = None
    
    shipping_address_1: Optional[str] = None
    shipping_address_2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_country: Optional[str] = None
    
    # Financial fields
    currency_code: str = "USD"
    opening_balance: Decimal = field(default=Decimal('0.00'))
    
    # Metadata
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    active: bool = True
    note: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        data = {
            'display_name': self.display_name,
            'contact_type': self.contact_type,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'website': self.website,
            'fax': self.fax,
            'currency_code': self.currency_code,
            'opening_balance': float(self.opening_balance),
            'active': self.active,
            'note': self.note
        }
        
        # Add billing address if provided
        if any([self.billing_address_1, self.billing_city, self.billing_state]):
            data['billing_address'] = {
                'address_1': self.billing_address_1,
                'address_2': self.billing_address_2,
                'city': self.billing_city,
                'state': self.billing_state,
                'postal_code': self.billing_postal_code,
                'country': self.billing_country
            }
        
        # Add shipping address if provided
        if any([self.shipping_address_1, self.shipping_city, self.shipping_state]):
            data['shipping_address'] = {
                'address_1': self.shipping_address_1,
                'address_2': self.shipping_address_2,
                'city': self.shipping_city,
                'state': self.shipping_state,
                'postal_code': self.shipping_postal_code,
                'country': self.shipping_country
            }
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class BigCapitalInvoiceEntry:
    """BigCapital Invoice Line Item"""
    item_id: Optional[int] = None
    description: str = ""
    quantity: Decimal = field(default=Decimal('1.00'))
    rate: Decimal = field(default=Decimal('0.00'))
    amount: Optional[Decimal] = None
    
    # Tax information
    tax_rate_id: Optional[int] = None
    tax_amount: Decimal = field(default=Decimal('0.00'))
    
    def __post_init__(self):
        """Calculate amount if not provided"""
        if self.amount is None:
            self.amount = self.quantity * self.rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            'item_id': self.item_id,
            'description': self.description,
            'quantity': float(self.quantity),
            'rate': float(self.rate),
            'amount': float(self.amount or (self.quantity * self.rate)),
            'tax_rate_id': self.tax_rate_id,
            'tax_amount': float(self.tax_amount)
        }


@dataclass
class BigCapitalInvoice:
    """BigCapital Invoice model"""
    customer_id: int
    invoice_date: date
    due_date: date
    invoice_number: Optional[str] = None
    reference: Optional[str] = None
    note: Optional[str] = None
    terms_conditions: Optional[str] = None
    entries: List[BigCapitalInvoiceEntry] = field(default_factory=list)
    
    # Financial fields
    subtotal: Optional[Decimal] = None
    total: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    discount_amount: Decimal = field(default=Decimal('0.00'))
    adjustment: Decimal = field(default=Decimal('0.00'))
    
    # Status and metadata
    invoice_status: str = "draft"  # draft, sent, paid, partially_paid, overdue
    currency_code: str = "USD"
    exchange_rate: Decimal = field(default=Decimal('1.00'))
    
    # Metadata
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def calculate_totals(self):
        """Calculate invoice totals"""
        if not self.entries:
            self.subtotal = Decimal('0.00')
            self.tax_amount = Decimal('0.00')
            self.total = Decimal('0.00')
            return
        
        self.subtotal = sum(entry.amount or (entry.quantity * entry.rate) for entry in self.entries)
        self.tax_amount = sum(entry.tax_amount for entry in self.entries)
        self.total = self.subtotal + self.tax_amount + self.adjustment - self.discount_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        self.calculate_totals()
        
        return {
            'customer_id': self.customer_id,
            'invoice_date': self.invoice_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'invoice_number': self.invoice_number,
            'reference': self.reference,
            'note': self.note,
            'terms_conditions': self.terms_conditions,
            'entries': [entry.to_dict() for entry in self.entries],
            'subtotal': float(self.subtotal or 0),
            'total': float(self.total or 0),
            'tax_amount': float(self.tax_amount or 0),
            'discount_amount': float(self.discount_amount),
            'adjustment': float(self.adjustment),
            'invoice_status': self.invoice_status,
            'currency_code': self.currency_code,
            'exchange_rate': float(self.exchange_rate)
        }


@dataclass
class BigCapitalExpense:
    """BigCapital Expense model"""
    payee_id: Optional[int] = None
    payment_account_id: int = 1  # Default to first account
    payment_date: date = field(default_factory=date.today)
    amount: Decimal = field(default=Decimal('0.00'))
    currency_code: str = "USD"
    exchange_rate: Decimal = field(default=Decimal('1.00'))
    reference: Optional[str] = None
    description: Optional[str] = None
    
    # Categories and tracking
    expense_account_id: Optional[int] = None
    project_id: Optional[int] = None
    branch_id: Optional[int] = None
    
    # Attachments and metadata
    attachment_ids: List[int] = field(default_factory=list)
    
    # Metadata
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            'payee_id': self.payee_id,
            'payment_account_id': self.payment_account_id,
            'payment_date': self.payment_date.isoformat(),
            'amount': float(self.amount),
            'currency_code': self.currency_code,
            'exchange_rate': float(self.exchange_rate),
            'reference': self.reference,
            'description': self.description,
            'expense_account_id': self.expense_account_id,
            'project_id': self.project_id,
            'branch_id': self.branch_id,
            'attachment_ids': self.attachment_ids
        }


@dataclass
class BigCapitalAccount:
    """BigCapital Chart of Accounts entry"""
    name: str
    code: str
    account_type: str  # asset, liability, equity, income, expense
    parent_account_id: Optional[int] = None
    description: Optional[str] = None
    active: bool = True
    
    # Metadata
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    balance: Decimal = field(default=Decimal('0.00'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            'name': self.name,
            'code': self.code,
            'account_type': self.account_type,
            'parent_account_id': self.parent_account_id,
            'description': self.description,
            'active': self.active
        }


@dataclass
class BigCapitalOrganization:
    """BigCapital Organization information"""
    name: str
    base_currency: str = "USD"
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"
    fiscal_year: str = "january-december"
    
    # Contact information
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    
    # Address
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    # Metadata
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Helper functions for model creation
def create_contact_from_dict(data: Dict[str, Any]) -> BigCapitalContact:
    """Create BigCapitalContact from dictionary data"""
    # Get valid field names from the dataclass
    from dataclasses import fields
    valid_fields = {field.name for field in fields(BigCapitalContact)}
    
    # Filter data to only include valid fields
    filtered_data = {k: v for k, v in data.items() if k in valid_fields}
    
    # Ensure required fields are present
    if 'display_name' not in filtered_data:
        filtered_data['display_name'] = 'Unknown Contact'
    
    return BigCapitalContact(**filtered_data)


def create_invoice_from_dict(data: Dict[str, Any]) -> BigCapitalInvoice:
    """Create BigCapitalInvoice from dictionary data"""
    from dataclasses import fields
    
    # Make a copy to avoid modifying original data
    data_copy = data.copy()
    entries_data = data_copy.pop('entries', [])
    
    # Get valid field names
    valid_fields = {field.name for field in fields(BigCapitalInvoice)}
    filtered_data = {k: v for k, v in data_copy.items() if k in valid_fields}
    
    # Ensure required fields
    if 'customer_id' not in filtered_data:
        filtered_data['customer_id'] = 1
    if 'invoice_date' not in filtered_data:
        filtered_data['invoice_date'] = date.today()
    if 'due_date' not in filtered_data:
        filtered_data['due_date'] = date.today()
    
    invoice = BigCapitalInvoice(**filtered_data)
    
    # Add entries
    for entry_data in entries_data:
        entry_fields = {field.name for field in fields(BigCapitalInvoiceEntry)}
        entry_filtered = {k: v for k, v in entry_data.items() if k in entry_fields}
        if entry_filtered:  # Only add if there's valid data
            entry = BigCapitalInvoiceEntry(**entry_filtered)
            invoice.entries.append(entry)
    
    return invoice


def create_expense_from_dict(data: Dict[str, Any]) -> BigCapitalExpense:
    """Create BigCapitalExpense from dictionary data"""
    from dataclasses import fields
    
    # Get valid field names
    valid_fields = {field.name for field in fields(BigCapitalExpense)}
    filtered_data = {k: v for k, v in data.items() if k in valid_fields}
    
    return BigCapitalExpense(**filtered_data)
