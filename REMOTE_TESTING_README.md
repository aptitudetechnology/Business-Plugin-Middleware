# Remote Testing Guide for BigCapital Plugin

Since you do all testing on a remote server via SSH, here's how to test the new InvoicePlane integration functionality.

## Quick Test on Remote Server

1. **Copy the test script to your server:**
   ```bash
   scp test_bigcapital_invoiceplane_integration.py user@your-server:/path/to/test/
   ```

2. **SSH into your server:**
   ```bash
   ssh user@your-server
   ```

3. **Run the test:**
   ```bash
   cd /path/to/your/project
   python3 test_bigcapital_invoiceplane_integration.py
   ```

## What the Test Does

The test script will:
- ✅ Import all BigCapital plugin modules
- ✅ Test plugin initialization
- ✅ Validate configuration
- ✅ Test InvoicePlane data transformation methods
- ✅ Test contact management methods
- ✅ Test status mapping functionality

## Expected Output

```
🚀 Starting BigCapital Plugin InvoicePlane Integration Tests
============================================================
🧪 Testing plugin initialization...
✅ Plugin initialized successfully
🧪 Testing configuration validation...
✅ Valid configuration accepted
✅ Invalid configuration properly rejected
🧪 Testing InvoicePlane sync methods...
  Testing data transformation...
  ✅ Data transformation successful
    Invoice number: INV-001
    Items count: 2
  Testing status mapping...
  ✅ Status mapping: 'sent' -> 'sent'
  Testing contact methods...
  ✅ Contact search method executed (expected to return None without API)
✅ All InvoicePlane sync methods tested successfully
============================================================
🎉 All tests passed successfully!
```

## Next Steps After Testing

1. **Configure real API credentials** in your plugin config
2. **Test with real InvoicePlane data** by calling the sync methods
3. **Set up automated workflows** between InvoicePlane and BigCapital
4. **Monitor sync logs** for any issues

## Troubleshooting

If tests fail:
- Check Python path includes the project directory
- Ensure all dependencies are installed (`pip install loguru requests`)
- Verify plugin files are in the correct locations
- Check file permissions

## Integration Testing

Once basic tests pass, you can test real integration:

```python
# In your Python shell on the server
from plugins.bigcapitalpy.plugin import BigCapitalPlugin

plugin = BigCapitalPlugin("bigcapital")
plugin.initialize({'config': your_real_config})

# Test with real InvoicePlane invoice data
result = plugin.sync_invoice_from_invoiceplane(real_invoice_data)
print(result)
```