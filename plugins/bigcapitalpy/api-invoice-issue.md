# BigCapitalPy Invoice API 400 Error Diagnosis

## Issue Summary
POST `/api/v1/invoices` returns HTTP 400 (Bad Request) instead of creating an invoice successfully.

## Root Cause Analysis

The 400 error occurs when the request fails JSON validation or contains invalid data. Based on code inspection of `packages/webapp/src/api/v1/invoices.py` and `packages/webapp/src/api/utils.py`, here are the possible causes:

### 1. JSON Validation Failures (400 responses from `@validate_json_request` decorator)

**Required Fields Check:**
- The endpoint requires: `customer_id`, `invoice_date`, `due_date`, `line_items`
- Missing any of these returns: `"Missing required fields: {field_names}"`

**Content-Type Check:**
- Request must have `Content-Type: application/json` header
- Missing/incorrect returns: `"Content-Type must be application/json"`

**JSON Body Check:**
- Request body must be valid JSON
- Invalid JSON returns: `"Request body must contain valid JSON"`

### 2. Business Logic Validation Failures (400 responses from endpoint code)

**Customer Validation:**
- `customer_id` must exist and belong to current user's organization
- Invalid customer returns: `404 "Customer not found"` (not 400)

**Line Items Validation:**
- `line_items` array must not be empty
- Empty array returns: `400 "At least one line item is required"`

**Line Item Description:**
- Each line item must have a `description` field
- Missing description raises `ValueError` → `400 "Invalid data: Line item description is required"`

**Date Format Validation:**
- `invoice_date` and `due_date` must be in `YYYY-MM-DD` format
- Invalid format raises `ValueError` → `400 "Invalid data: {error_message}"`

## Reproduction Steps

### 1. Login (if using session auth)
```bash
curl -c cookies.txt -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bigcapitalpy.com","password":"admin123"}' | jq
```

### 2. Create Invoice (Session Auth)
```bash
curl -b cookies.txt -i -X POST http://localhost:5000/api/v1/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "invoice_date": "2025-10-20",
    "due_date": "2025-11-20",
    "currency": "USD",
    "line_items": [
      {
        "description": "Consulting services",
        "quantity": 1,
        "rate": 100.00,
        "tax_rate": 0
      }
    ]
  }' | jq
```

### 3. Create Invoice (API Key Auth)
```bash
curl -i -X POST http://localhost:5000/api/v1/invoices \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "customer_id": 1,
    "invoice_date": "2025-10-20",
    "due_date": "2025-11-20",
    "currency": "USD",
    "line_items": [
      {
        "description": "Consulting services",
        "quantity": 1,
        "rate": 100.00,
        "tax_rate": 0
      }
    ]
  }' | jq
```

## Debugging Steps

### 1. Capture Full Response
Use `-i` flag to see HTTP headers and pipe through `jq` for readable JSON:
```bash
curl -b cookies.txt -i -X POST http://localhost:5000/api/v1/invoices \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1}' | jq
```

### 2. Check Server Logs
Look for Flask error messages in server console/logs that may provide more details about the validation failure.

### 3. Common Issues to Check

- **Missing Content-Type header** → `"Content-Type must be application/json"`
- **Invalid JSON syntax** → `"Request body must contain valid JSON"`
- **Missing required fields** → `"Missing required fields: customer_id, invoice_date, due_date, line_items"`
- **Empty line_items array** → `"At least one line item is required"`
- **Missing line item description** → `"Invalid data: Line item description is required"`
- **Wrong date format** → `"Invalid data: time data '10/20/2025' does not match format '%Y-%m-%d'"`

## Prerequisites Checklist

Before testing invoice creation:

1. **Valid customer exists**: `customer_id: 1` should reference an existing customer
2. **Correct date format**: Use `YYYY-MM-DD` format (e.g., `"2025-10-20"`)
3. **Valid JSON**: Ensure request body is properly formatted JSON
4. **Content-Type header**: Must be `application/json`
5. **Authentication**: Either valid session cookies or API key

## Error Response Format

All 400 errors follow this JSON structure:
```json
{
  "success": false,
  "error": "Error message here",
  "timestamp": "2025-10-20T10:45:31Z",
  "errors": {
    "missing_fields": ["field1", "field2"]
  }
}
```

## Next Steps

1. Run the reproduction curl commands above
2. Capture the exact error message from the JSON response
3. Check server logs for additional details
4. Fix the identified issue based on the error message
5. Re-test until invoice creation succeeds (returns 201 Created)
