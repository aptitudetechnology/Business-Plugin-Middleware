# BigCapitalPy API Documentation

## Overview
BigCapitalPy provides a comprehensive REST API for accounting and financial management operations. All API endpoints require authentication via API key or session authentication.

## Base URL
```
https://your-domain.com/api/v1
```

## Authentication
All API endpoints require authentication. Use one of the following methods:

### API Key Authentication
Include the API key in the request header:
```
X-API-Key: your-api-key-here
```

### Session Authentication
For web-based requests, session authentication is handled automatically.

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Pagination
List endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

Pagination response includes:
```json
{
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering and Sorting
Most list endpoints support:
- `search`: Text search across relevant fields
- `sort_by`: Field to sort by
- `sort_order`: 'asc' or 'desc'

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Organizations
- `GET /organizations` - List organizations
- `GET /organizations/{id}` - Get organization details
- `POST /organizations` - Create organization
- `PUT /organizations/{id}` - Update organization
- `DELETE /organizations/{id}` - Delete organization

### Customers
- `GET /customers` - List customers
- `GET /customers/{id}` - Get customer details
- `POST /customers` - Create customer
- `PUT /customers/{id}` - Update customer
- `DELETE /customers/{id}` - Delete customer

### Vendors
- `GET /vendors` - List vendors
- `GET /vendors/{id}` - Get vendor details
- `POST /vendors` - Create vendor
- `PUT /vendors/{id}` - Update vendor
- `DELETE /vendors/{id}` - Delete vendor

### Items
- `GET /items` - List items
- `GET /items/{id}` - Get item details
- `POST /items` - Create item
- `PUT /items/{id}` - Update item
- `DELETE /items/{id}` - Delete item

### Invoices
- `GET /invoices` - List invoices
- `GET /invoices/{id}` - Get invoice details
- `POST /invoices` - Create invoice
- `PUT /invoices/{id}` - Update invoice
- `DELETE /invoices/{id}` - Delete invoice
- `POST /invoices/{id}/send` - Send invoice via email

### Payments
- `GET /payments` - List payments
- `GET /payments/{id}` - Get payment details
- `POST /payments` - Create payment
- `PUT /payments/{id}` - Update payment
- `DELETE /payments/{id}` - Delete payment

### Accounts (Chart of Accounts)
- `GET /accounts` - List accounts
- `GET /accounts/{id}` - Get account details
- `POST /accounts` - Create account
- `PUT /accounts/{id}` - Update account
- `DELETE /accounts/{id}` - Delete account
- `GET /accounts/hierarchy` - Get account hierarchy

### Banking
- `GET /banking/accounts` - List bank accounts
- `GET /banking/accounts/{id}` - Get bank account details
- `POST /banking/accounts` - Create bank account
- `PUT /banking/accounts/{id}` - Update bank account
- `DELETE /banking/accounts/{id}` - Delete bank account

- `GET /banking/transactions` - List bank transactions
- `GET /banking/transactions/{id}` - Get transaction details
- `POST /banking/transactions` - Create transaction
- `PUT /banking/transactions/{id}` - Update transaction
- `DELETE /banking/transactions/{id}` - Delete transaction

- `POST /banking/transactions/{id}/reconcile` - Reconcile transaction
- `POST /banking/transactions/reconcile/bulk` - Bulk reconcile transactions
- `GET /banking/reconciliation/summary` - Get reconciliation summary

### Journal Entries
- `GET /journal` - List journal entries
- `GET /journal/{id}` - Get journal entry details
- `POST /journal` - Create journal entry
- `PUT /journal/{id}` - Update journal entry
- `DELETE /journal/{id}` - Delete journal entry

### Tax
- `GET /tax` - List taxes
- `GET /tax/{id}` - Get tax details
- `POST /tax` - Create tax
- `PUT /tax/{id}` - Update tax
- `DELETE /tax/{id}` - Delete tax
- `POST /tax/calculate` - Calculate tax amount

### Reports
- `GET /reports/balance-sheet` - Balance sheet report
- `GET /reports/income-statement` - Income statement report
- `GET /reports/trial-balance` - Trial balance report
- `GET /reports/aging` - Accounts receivable/payable aging
- `GET /reports/cash-flow` - Cash flow statement

## Data Models

### Common Fields
All models include:
- `id`: Unique identifier
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `organization_id`: Organization ownership

### Customer/Vendor
```json
{
  "id": 1,
  "name": "ABC Company",
  "email": "contact@abc.com",
  "phone": "+1-555-0123",
  "address": "123 Main St",
  "city": "Anytown",
  "state": "CA",
  "zip_code": "12345",
  "country": "USA",
  "tax_id": "12-3456789",
  "is_active": true
}
```

### Invoice
```json
{
  "id": 1,
  "invoice_number": "INV-001",
  "customer_id": 1,
  "date": "2024-01-15",
  "due_date": "2024-02-15",
  "status": "sent",
  "subtotal": 1000.00,
  "tax_amount": 100.00,
  "total": 1100.00,
  "notes": "Payment due within 30 days",
  "line_items": [
    {
      "item_id": 1,
      "description": "Service description",
      "quantity": 10,
      "unit_price": 100.00,
      "amount": 1000.00
    }
  ]
}
```

### Journal Entry
```json
{
  "id": 1,
  "entry_number": "JE000001",
  "reference": "REF-001",
  "date": "2024-01-15",
  "description": "Monthly expense entry",
  "source_type": "manual",
  "line_items": [
    {
      "account_id": 1,
      "debit": 1000.00,
      "credit": 0.00,
      "description": "Office supplies"
    },
    {
      "account_id": 2,
      "debit": 0.00,
      "credit": 1000.00,
      "description": "Cash payment"
    }
  ]
}
```

## Error Codes
- `VALIDATION_ERROR`: Input validation failed
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `CONFLICT`: Resource conflict (e.g., duplicate)
- `INTERNAL_ERROR`: Server error

## Rate Limiting
API requests are rate limited to prevent abuse. Limits vary by endpoint type:
- Read operations: 1000 requests/hour
- Write operations: 100 requests/hour
- Authentication: 10 requests/minute

## Webhooks
Configure webhooks to receive real-time notifications for:
- Invoice status changes
- Payment receipts
- New transactions
- Reconciliation updates

## SDKs and Libraries
- Python SDK: `pip install bigcapitalpy-sdk`
- JavaScript SDK: `npm install bigcapitalpy-sdk`

## Support
For API support, visit our documentation at https://docs.bigcapitalpy.com or contact support@bigcapitalpy.com.