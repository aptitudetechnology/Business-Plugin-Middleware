# BigCapital Plugin

**A plugin for integrating BigCapital accounting software with InvoicePlanePy for automated invoice synchronization.**

![Status](https://img.shields.io/badge/status-beta-blue.svg)
![Features](https://img.shields.io/badge/features-invoice--sync-green.svg)
![Integration](https://img.shields.io/badge/integration-invoiceplanepy-orange.svg)

## Overview

This plugin integrates with the Business-Plugin-Middleware to provide seamless synchronization of invoices from InvoicePlanePy to BigCapital accounting software. It automatically downloads invoices from InvoicePlanePy and creates corresponding records in BigCapital, including contacts, invoices, and line items.

## Features

### 📄 **Invoice Synchronization**
- ✅ **Automatic Invoice Sync**: Download invoices from InvoicePlanePy and sync to BigCapital
- ✅ **Contact Management**: Automatically create or match contacts in BigCapital
- ✅ **Invoice Status Mapping**: Map InvoicePlanePy statuses to BigCapital invoice states
- ✅ **Data Transformation**: Convert InvoicePlanePy data format to BigCapital format
- ✅ **Error Handling**: Comprehensive error handling and reporting

### 🔗 **Plugin Architecture**
- ✅ **Middleware Integration**: Seamless integration with Business-Plugin-Middleware
- ✅ **API Clients**: Robust clients for both BigCapital and InvoicePlanePy APIs
- ✅ **Data Models**: Well-defined models for invoices, contacts, and metadata
- ✅ **Configuration**: Flexible configuration options for both systems

### 📊 **Sync Statistics**
- ✅ **Success/Failure Tracking**: Monitor sync success rates
- ✅ **Performance Metrics**: Track processing times and statistics
- ✅ **Health Monitoring**: Plugin health and status monitoring

## Installation

1. Place the `bigcapitalpy` folder in your `plugins/` directory
2. Configure the plugin in your middleware configuration
3. Ensure InvoicePlanePy plugin is also installed and configured
4. Restart the middleware to load the plugin

## Configuration

Create or update `config/plugins.json` in your middleware configuration:

```json
{
  "bigcapitalpy": {
    "enabled": true,
    "api_key": "YOUR_BIGCAPITAL_API_KEY",
    "base_url": "https://api.bigcapital.ly",
    "timeout": 30,
    "organization_id": "YOUR_ORGANIZATION_ID"
  },
  "invoiceplanepy": {
    "enabled": true,
    "api_key": "YOUR_INVOICEPLANE_API_KEY",
    "base_url": "https://your-invoiceplane-instance.com",
    "timeout": 30
  }
}
```

### Configuration Parameters

#### BigCapital Configuration
- `api_key`: Your BigCapital API key (required)
- `base_url`: BigCapital API base URL (default: "https://api.bigcapital.ly")
- `timeout`: API request timeout in seconds (default: 30)
- `organization_id`: Your BigCapital organization ID (required)

#### InvoicePlanePy Configuration
- `api_key`: Your InvoicePlanePy API key (required)
- `base_url`: InvoicePlanePy instance base URL (required)
- `timeout`: API request timeout in seconds (default: 30)

## Usage

### Web Interface

The plugin provides a web interface accessible through the middleware:

1. Navigate to `/plugins/bigcapitalpy` in your middleware
2. View sync statistics and recent activity
3. Manually trigger invoice synchronization
4. Monitor plugin health and configuration

### API Integration

#### Sync Invoice from InvoicePlanePy

```http
POST /api/bigcapital/sync/invoiceplane/{invoice_id}
```

Syncs a specific invoice from InvoicePlanePy to BigCapital.

**Response:**
```json
{
  "success": true,
  "message": "Invoice synced successfully to BigCapital",
  "sync_result": {
    "invoice_id": "INV-001",
    "bigcapital_invoice_id": 12345,
    "contact_created": true,
    "status": "completed"
  }
}
```

#### Bulk Sync Invoices

```http
POST /api/bigcapital/sync/bulk
Content-Type: application/json

{
  "invoice_ids": ["INV-001", "INV-002", "INV-003"],
  "create_contacts": true,
  "update_existing": false
}
```

### Programmatic Usage

```python
from plugins.bigcapitalpy.plugin import BigCapitalPlugin

# Initialize plugin
plugin = BigCapitalPlugin("bigcapitalpy")
plugin.initialize(app_context)

# Sync specific invoice
result = plugin.sync_invoice_from_invoiceplane(invoice_data)
print(f"Sync result: {result}")
```

## Data Mapping

### Invoice Fields Mapping

| InvoicePlanePy Field | BigCapital Field | Notes |
|---------------------|------------------|-------|
| `invoice_number` | `invoice_number` | Direct mapping |
| `issue_date` | `invoice_date` | Date conversion |
| `due_date` | `due_date` | Date conversion |
| `total` | `amount` | Numeric conversion |
| `tax_total` | `tax_amount` | Tax calculation |
| `client.name` | `contact.name` | Contact creation |
| `items[]` | `entries[]` | Line item mapping |

### Status Mapping

| InvoicePlanePy Status | BigCapital Status |
|----------------------|-------------------|
| `paid` | `paid` |
| `sent` | `sent` |
| `overdue` | `overdue` |
| `draft` | `draft` |
| `viewed` | `sent` |

## Error Handling

The plugin includes comprehensive error handling:

- **API Connection Errors**: Automatic retry with exponential backoff
- **Data Validation Errors**: Detailed validation messages
- **Authentication Errors**: Clear authentication failure messages
- **Rate Limiting**: Built-in rate limit handling
- **Partial Failures**: Continue processing other items on individual failures

## Monitoring

### Health Checks

```http
GET /api/plugins/bigcapitalpy/health
```

Returns plugin health status and recent sync statistics.

### Statistics

```http
GET /api/plugins/bigcapitalpy/stats
```

Returns detailed sync statistics including:
- Total invoices synced
- Success/failure rates
- Processing times
- Error counts by type

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   - Verify your BigCapital API key is correct
   - Check InvoicePlanePy API key format

2. **Connection Timeouts**
   - Increase timeout values in configuration
   - Check network connectivity

3. **Data Mapping Errors**
   - Review InvoicePlanePy data structure
   - Check BigCapital field requirements

4. **Contact Creation Failures**
   - Verify contact data completeness
   - Check for duplicate contact handling

### Debug Mode

Enable debug logging by setting the log level to DEBUG in your middleware configuration.

## Development

### Testing

Run the test suite:

```bash
python -m pytest tests/test_bigcapital_plugin.py -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This plugin is part of the Business-Plugin-Middleware project. See the main project license for details.

## Support

For support and questions:
- Check the middleware logs for error details
- Review the API documentation
- Create an issue in the project repository
