# InvoicePlane Python API Specification

## Overview

This specification documents the REST API endpoints available in InvoicePlane Python for integration with external systems like the Business Plugin Middleware. The API provides programmatic access to invoice data, client information, products, payments, and other business entities.

## Base URL
```
http://your-invoiceplane-instance:8000
```

## Authentication

The API supports two authentication methods:

### 1. JWT Token Authentication (Recommended for API integration)
- **Header**: `Authorization: Bearer {jwt_token}`
- **Token Generation**: Login via `/auth/login` endpoint or use API keys

### 2. Session Cookie Authentication
- **Cookie**: `session_token={session_token}`
- **Login**: POST to `/auth/login` with form data

### API Key Authentication (For future implementation)
- API keys can be generated via the web interface at `/settings/api-keys`
- Use API key as JWT token in Authorization header

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

*Note: Currently only available through web interface. JSON API endpoint planned for future release.*

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

## 🔑 API Keys Management

### GET /api/keys

List API keys for authenticated user.

### POST /api/keys/generate

Generate a new API key.

#### Request Body
```json
{
  "name": "Business Plugin Middleware"
}
```

#### Response
```json
{
  "key": "sk_abc123def456...",
  "key_info": {
    "id": 1,
    "name": "Business Plugin Middleware",
    "key_prefix": "sk_abc123",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "last_used_at": null
  }
}
```

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

### 1. Get Authentication Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -d "username=admin&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

### 2. Use Token to Access API
```bash
curl -X GET "http://localhost:8000/invoices/api?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Test with API Key (Future)
```bash
curl -X GET "http://localhost:8000/invoices/api" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

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
const INVOICEPLANE_BASE_URL = 'http://your-instance:8000';
const JWT_TOKEN = 'your-jwt-token';

async function fetchInvoices(page = 1, limit = 100) {
  const response = await fetch(`${INVOICEPLANE_BASE_URL}/invoices/api?page=${page}&limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${JWT_TOKEN}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  const data = await response.json();
  return data;
}

// Fetch all invoices
async function syncAllInvoices() {
  let allInvoices = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const data = await fetchInvoices(page, 100);
    allInvoices = allInvoices.concat(data.invoices);

    if (page >= data.pagination.total_pages) {
      hasMore = false;
    } else {
      page++;
    }
  }

  return allInvoices;
}
```

---

## 📞 Support

For API integration support:
- Check the [API Documentation](http://localhost:8000/docs) (Swagger UI)
- Review [Application Logs](#) for error details
- Contact development team for custom integration requirements

---

*Last Updated: October 2025*
*API Version: 1.0.0*