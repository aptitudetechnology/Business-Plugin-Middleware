# InvoicePlane Python API Specification

## Overview

This specification documents the REST API endpoints available in InvoicePlane Python for integration with external systems like the Business Plugin Middleware. The API provides programmatic access to invoice data, client information, products, payments, and other business entities.

## Base URL
```
http://your-invoiceplane-instance:8000
```

## Authentication

The API supports three authentication methods:

### 1. API Key Authentication (Recommended for API integration)
- **Header**: `Authorization: Bearer sk_abc123def456...`
- **API Key Generation**: Via web interface at `/settings/api-keys`
- **Format**: API keys start with `sk_` prefix

### 2. JWT Token Authentication
- **Header**: `Authorization: Bearer {jwt_token}`
- **Token Generation**: Login via `/auth/login` endpoint

### 3. Session Cookie Authentication
- **Cookie**: `session_token={session_token}`
- **Login**: POST to `/auth/login` with form data

## Common Response Format

All API responses follow this structure:

```json
{
  "data": [...],  // Array of requested items
  "pagination": {
    "page": 1,
    "limit": 100,
    "total": 150,
    "total_pages": 2
  },
  "filters": {
    "search": "optional search term",
    "status": "optional status filter",
    "sort_by": "field_name",
    "sort_order": "asc|desc"
  }
}
```

## Error Responses

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common HTTP status codes:
- `200`: Success
- `401`: Unauthorized (invalid/missing authentication)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

---

## 📄 Invoices API

### GET /invoices/api

Retrieve a paginated list of invoices with full details including client information and line items.

#### Query Parameters
- `page` (integer, default: 1): Page number (1-based)
- `limit` (integer, default: 100, max: 1000): Items per page
- `search` (string, optional): Search in invoice number, client name, notes, or terms
- `status` (string, optional): Filter by status
  - `draft`, `sent`, `viewed`, `paid`, `overdue`, `cancelled`
- `sort_by` (string, default: "created_at"): Sort field
  - `created_at`, `issue_date`, `due_date`, `total`, `invoice_number`
- `sort_order` (string, default: "desc"): Sort order (`asc` or `desc`)

#### Response Format

```json
{
  "invoices": [
    {
      "id": 1,
      "invoice_number": "INV-001",
      "status": 4,
      "status_name": "paid",
      "issue_date": "2024-01-15",
      "due_date": "2024-02-15",
      "terms": "Payment due within 30 days",
      "notes": "Thank you for your business",
      "url_key": "abc123def456",
      "subtotal": 1000.00,
      "tax_total": 100.00,
      "discount_amount": 0.00,
      "discount_percentage": 0.00,
      "total": 1100.00,
      "paid_amount": 1100.00,
      "balance": 0.00,
      "is_overdue": false,
      "days_overdue": 0,
      "client": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "address": "123 Main St"
      },
      "items": [
        {
          "id": 1,
          "name": "Web Development Service",
          "description": "Website development project",
          "quantity": 40.0,
          "price": 25.00,
          "subtotal": 1000.00,
          "tax_amount": 100.00,
          "discount_amount": 0.00,
          "total": 1100.00,
          "product": {
            "id": 1,
            "name": "Web Development",
            "sku": "WEB-001"
          }
        }
      ],
      "user_id": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 100,
    "total": 150,
    "total_pages": 2
  },
  "filters": {
    "search": null,
    "status": null,
    "sort_by": "created_at",
    "sort_order": "desc"
  }
}
```

#### Example Request
```bash
curl -X GET "http://localhost:8000/invoices/api?page=1&limit=50&status=paid" \
  -H "Authorization: Bearer your-jwt-token"
```

### GET /invoices/{invoice_id}

Retrieve the full HTML representation of a specific invoice document. This endpoint returns a complete, formatted HTML page that can be displayed directly in a web browser or embedded in other applications.

#### Path Parameters
- `invoice_id` (integer, required): The unique identifier of the invoice

#### Response Format
Returns complete HTML document with:
- Invoice header with number and client information
- Complete item table with quantities, prices, and totals
- Client and invoice details
- Payment status and balance information
- Formatted totals section
- Action buttons (PDF download, email, etc.)

#### Example Request
```bash
curl -X GET "http://localhost:8000/invoices/123" \
  -H "Authorization: Bearer sk_your_api_key_here"
```

#### Use Cases
- Display invoice in web applications
- Generate printable invoice views
- Embed invoice content in other systems
- Provide direct links to invoice documents

### GET /invoices/{invoice_id}/api

Retrieve complete JSON data for a specific invoice including all line items, client information, and calculated totals.

#### Path Parameters
- `invoice_id` (integer, required): The unique identifier of the invoice

#### Response Format

```json
{
  "id": 1,
  "invoice_number": "INV-001",
  "status": 4,
  "status_name": "paid",
  "issue_date": "2024-01-15",
  "due_date": "2024-02-15",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:15:00Z",
  "subtotal": 1000.00,
  "tax_total": 100.00,
  "discount_amount": 0.00,
  "total": 1100.00,
  "balance": 0.00,
  "notes": "Thank you for your business",
  "terms": "Payment due within 30 days",
  "client": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "address": "123 Main St, City, State 12345",
    "phone": "+1-555-0123"
  },
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  },
  "items": [
    {
      "id": 1,
      "name": "Web Development Service",
      "description": "Website development project",
      "quantity": 40.0,
      "price": 25.00,
      "discount_amount": 0.00,
      "tax_amount": 100.00,
      "subtotal": 1000.00,
      "product": {
        "id": 1,
        "name": "Web Development",
        "sku": "WEB-001"
      }
    }
  ]
}
```

#### Example Request
```bash
curl -X GET "http://localhost:8000/invoices/123/api" \
  -H "Authorization: Bearer sk_your_api_key_here"
```

#### Use Cases
- Retrieve structured invoice data for processing
- Integrate invoice information into external systems
- Generate custom invoice reports or exports
- Sync invoice data with accounting software

---

## 📦 Products API

### GET /products/api

Retrieve a paginated list of products with pricing and inventory information.

#### Query Parameters
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 100, max: 1000): Items per page
- `search` (string, optional): Search in product name, SKU, or description
- `sort_by` (string, default: "name"): Sort field (`name`, `price`, `sku`, `created_at`)
- `sort_order` (string, default: "asc"): Sort order (`asc` or `desc`)

#### Response Format

```json
{
  "products": [
    {
      "id": 1,
      "name": "Web Development Service",
      "sku": "WEB-001",
      "price": 25.00,
      "description": "Professional web development services",
      "tax_rate": 10.00,
      "provider_name": "Internal",
      "purchase_price": 15.00,
      "sumex": false,
      "tariff": null,
      "family": {
        "id": 1,
        "name": "Services"
      },
      "unit": {
        "id": 1,
        "name": "Hours",
        "abbreviation": "hrs"
      },
      "user_id": 1,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 100,
    "total": 50,
    "total_pages": 1
  },
  "filters": {
    "search": null,
    "sort_by": "name",
    "sort_order": "asc"
  }
}
```

---

## 💳 Payments API

### GET /payments/api

Retrieve a paginated list of payment records.

#### Query Parameters
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 100, max: 1000): Items per page
- `search` (string, optional): Search in payer name or reference

#### Response Format

```json
{
  "payments": [
    {
      "id": 1,
      "amount": 1100.00,
      "payer": "John Doe",
      "reference": "PAY-001",
      "date": "2024-01-20",
      "status": "completed"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 100,
    "total": 25,
    "total_pages": 1
  }
}
```

---

## 🏢 Clients API

### GET /clients/api

Retrieve a paginated list of clients with full contact information including phone numbers, addresses, and company details.

#### Query Parameters
- `page` (integer, default: 1): Page number (1-based)
- `limit` (integer, default: 100, max: 1000): Items per page
- `search` (string, optional): Search in name, surname, email, company, phone, or mobile
- `is_active` (boolean, default: true): Filter by active status
- `sort_by` (string, default: "name"): Sort field (name, email, company, created_at)
- `sort_order` (string, default: "asc"): Sort order (`asc` or `desc`)

#### Response Format

```json
{
  "clients": [
    {
      "id": 1,
      "is_active": true,
      "name": "John Doe",
      "surname": "Smith",
      "company": "Acme Corp",
      "email": "john@acme.com",
      "phone": "+1-555-0123",
      "fax": "+1-555-0789",
      "mobile": "+1-555-0456",
      "website": "https://acme.com",
      "address_1": "123 Main St",
      "address_2": "Suite 100",
      "city": "Anytown",
      "state": "CA",
      "zip_code": "12345",
      "country": "USA",
      "language": "en",
      "gender": "male",
      "birthdate": "1980-01-15",
      "vat_id": "US123456789",
      "tax_code": "TX123",
      "abn": "12345678901",
      "title": "CEO",
      "notes": "Preferred customer",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 100,
    "total": 150,
    "total_pages": 2
  },
  "filters": {
    "search": null,
    "is_active": true,
    "sort_by": "name",
    "sort_order": "asc"
  }
}
```

#### Example Request
```bash
curl -X GET "http://localhost:8000/clients/api?page=1&limit=50&search=john" \
  -H "Authorization: Bearer sk_your_api_key"
```

#### Use Cases
- Sync client data with external CRM systems
- Generate client directories or contact lists
- Search and filter clients programmatically
- Integrate client information into other business applications

### GET /clients/{client_id}/api

Retrieve complete information for a specific client including all contact details and business information.

#### Path Parameters
- `client_id` (integer, required): The unique identifier of the client

#### Response Format
Returns a single client object with the same structure as shown in the list endpoint above.

#### Example Request
```bash
curl -X GET "http://localhost:8000/clients/123/api" \
  -H "Authorization: Bearer sk_your_api_key"
```

#### Use Cases
- Retrieve detailed client information for forms or displays
- Get client data for invoice generation
- Access specific client contact information
- Validate client existence in external systems

---

## 🏷️ Tax Rates API

### GET /tax_rates/api

Retrieve tax rates configuration.

#### Response Format

```json
{
  "tax_rates": [
    {
      "id": 1,
      "name": "GST",
      "percent": 10.00,
      "is_default": true,
      "is_active": true
    }
  ]
}
```

---

## 🔑 API Key Management

### Generating API Keys

1. **Log in** to InvoicePlanePy web interface as an admin user
2. **Navigate** to **Settings** in the top navigation
3. **Click** on **API Keys** in the settings menu (`/settings/api-keys`)
4. **Click** the **"Generate New API Key"** button
5. **Enter** a descriptive name (e.g., "Business Plugin Middleware")
6. **Click** **"Generate Key"**
7. **Important**: Copy the full API key immediately - it will only be shown once!
8. **Store securely** - API keys have the same access as your user account

### API Key Format
- **Prefix**: `sk_` (for "secret key")
- **Length**: 43 characters total
- **Example**: `sk_abc123def456ghi789jkl012mno345pqr678stu`

### API Key Permissions
- API keys inherit the permissions of the user who created them
- **Admin users**: Access to all data
- **Regular users**: Access only to their own records

### Managing API Keys
- **List keys**: View all your API keys at `/settings/api-keys`
- **Delete keys**: Remove compromised or unused keys
- **Monitor usage**: Check `last_used_at` timestamp for activity

---

## 🔐 Authentication Endpoints

### POST /auth/login

Authenticate and receive JWT token.

#### Request (Form Data)
```
username: admin@example.com
password: yourpassword
```

#### Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true
  }
}
```

---

## 📊 Data Models

### Invoice Status Values
- `1`: Draft
- `2`: Sent
- `3`: Viewed
- `4`: Paid
- `5`: Overdue
- `6`: Cancelled

### Common Data Types
- **Dates**: ISO 8601 format (`YYYY-MM-DD`)
- **Timestamps**: ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`)
- **Monetary Values**: Float with 2 decimal places
- **Percentages**: Float (e.g., 10.00 for 10%)

---

## 🔒 Security & Permissions

### User Permissions
- **Admin Users**: Access to all invoices and data
- **Regular Users**: Access only to their own invoices

### Rate Limiting
- Default: 100 requests per minute per IP
- Configurable in application settings

### Data Privacy
- All API responses respect user permissions
- Sensitive client data only accessible to authorized users
- Invoice URLs are protected by unique keys

---

## 🧪 Testing the API

### Method 1: Using API Keys (Recommended)

1. **Generate API Key**:
   - Log in to web interface
   - Go to Settings → API Keys
   - Generate a new key named "Test Key"
   - Copy the key immediately

2. **Test API Access**:
```bash
# Replace sk_your_key_here with your actual API key
curl -X GET "http://localhost:8000/invoices/api?page=1&limit=5" \
  -H "Authorization: Bearer sk_your_key_here"
```

### Method 2: Using JWT Tokens

1. **Get JWT Token**:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -d "username=admin&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

2. **Extract Token** from response and use it:
```bash
curl -X GET "http://localhost:8000/invoices/api?page=1&limit=5" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Method 4: Using Test Script
- Run the included test script: `python scripts/test_api_keys.py`
- Edit the `API_KEY` variable with your generated key
- The script will test authentication and multiple endpoints

---

## 🔧 Integration Guidelines

### For Business Plugin Middleware

1. **Authentication**: Use JWT tokens for API access
2. **Pagination**: Handle pagination for large datasets
3. **Error Handling**: Implement retry logic for 5xx errors
4. **Rate Limiting**: Respect rate limits and implement backoff
5. **Data Sync**: Use `updated_at` timestamps for incremental sync
6. **Invoice Status**: Monitor status changes for business logic

### Recommended Sync Strategy

1. **Initial Sync**: Fetch all invoices with pagination
2. **Incremental Sync**: Query for invoices updated since last sync
3. **Real-time Updates**: Poll API periodically or implement webhooks (future)

### Sample Integration Code (JavaScript/Node.js)

```javascript
const INVOICEPLANE_BASE_URL = 'http://your-invoiceplane-instance:8000';
const API_KEY = 'sk_your_api_key_here'; // Generated from /settings/api-keys

async function fetchInvoices(page = 1, limit = 100) {
  const response = await fetch(`${INVOICEPLANE_BASE_URL}/invoices/api?page=${page}&limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  const data = await response.json();
  return data;
}

async function fetchClients(search = '', page = 1, limit = 100) {
  const searchParam = search ? `&search=${encodeURIComponent(search)}` : '';
  const response = await fetch(`${INVOICEPLANE_BASE_URL}/clients/api?page=${page}&limit=${limit}${searchParam}`, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  const data = await response.json();
  return data;
}

async function getClient(clientId) {
  const response = await fetch(`${INVOICEPLANE_BASE_URL}/clients/${clientId}/api`, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  const client = await response.json();
  return client;
}
```

---

## 📞 Support

For API integration support:
- Check the [API Documentation](http://localhost:8000/docs) (Swagger UI)
- Review [Application Logs](#) for error details
- Contact development team for custom integration requirements

---

*Last Updated: 20 October 2025*
*API Version: 1.0.0*