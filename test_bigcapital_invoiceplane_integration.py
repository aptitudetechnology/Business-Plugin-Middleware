#!/usr/bin/env python3
"""
Test script for BigCapital Plugin InvoicePlane integration
Run this on your remote server to test the new sync functionality
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/home/chris/Business-Plugin-Middleware')

try:
    from plugins.bigcapitalpy.plugin import BigCapitalPlugin
    from plugins.bigcapitalpy.client import BigCapitalClient
    print("✅ Successfully imported BigCapital plugin modules")
except ImportError as e:
    print(f"❌ Failed to import BigCapital plugin: {e}")
    sys.exit(1)

def test_plugin_initialization():
    """Test basic plugin initialization"""
    print("\n🧪 Testing plugin initialization...")

    # Mock configuration
    config = {
        'api_key': 'test-key',
        'base_url': 'https://api.bigcapital.ly',
        'timeout': 30
    }

    plugin = BigCapitalPlugin("test-bigcapital")
    app_context = {'config': config}

    try:
        result = plugin.initialize(app_context)
        if result:
            print("✅ Plugin initialized successfully")
            return plugin
        else:
            print("❌ Plugin initialization failed")
            return None
    except Exception as e:
        print(f"❌ Plugin initialization error: {e}")
        return None

def test_invoiceplane_sync_methods(plugin):
    """Test the new InvoicePlane sync methods"""
    print("\n🧪 Testing InvoicePlane sync methods...")

    # Mock InvoicePlane invoice data
    mock_invoice_data = {
        'id': 123,
        'number': 'INV-001',
        'date_created': '2024-01-15',
        'date_due': '2024-02-15',
        'status': 'sent',
        'currency_code': 'USD',
        'exchange_rate': 1.0,
        'notes': 'Test invoice from InvoicePlane',
        'terms': 'Net 30',
        'discount_amount': 0,
        'client': {
            'name': 'Test Company Inc',
            'first_name': 'John',
            'last_name': 'Doe',
            'company': 'Test Company Inc',
            'email': 'john@testcompany.com',
            'phone': '+1-555-0123',
            'address_1': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip_code': '12345',
            'country': 'USA',
            'currency_code': 'USD'
        },
        'items': [
            {
                'name': 'Consulting Services',
                'description': 'Monthly consulting services',
                'quantity': 10,
                'price': 100.00,
                'total': 1000.00
            },
            {
                'name': 'Travel Expenses',
                'description': 'Business travel',
                'quantity': 1,
                'price': 500.00,
                'total': 500.00
            }
        ]
    }

    try:
        # Test data transformation
        print("  Testing data transformation...")
        transformed = plugin._transform_invoiceplane_to_bigcapital(mock_invoice_data)
        print("  ✅ Data transformation successful")
        print(f"    Invoice number: {transformed.get('invoice_number')}")
        print(f"    Items count: {len(transformed.get('items', []))}")

        # Test status mapping
        print("  Testing status mapping...")
        status = plugin._map_invoice_status('sent')
        print(f"  ✅ Status mapping: 'sent' -> '{status}'")

        # Test contact finding (will fail without real API, but tests the method)
        print("  Testing contact methods...")
        contact_result = plugin._find_existing_contact_from_invoiceplane(mock_invoice_data['client'])
        print("  ✅ Contact search method executed (expected to return None without API)")

        print("✅ All InvoicePlane sync methods tested successfully")
        return True

    except Exception as e:
        print(f"❌ InvoicePlane sync method test failed: {e}")
        return False

def test_config_validation():
    """Test configuration validation"""
    print("\n🧪 Testing configuration validation...")

    plugin = BigCapitalPlugin("test-bigcapital")

    # Test valid config
    valid_config = {
        'api_key': 'test-key-123',
        'base_url': 'https://api.bigcapital.ly'
    }

    if plugin.validate_config(valid_config):
        print("✅ Valid configuration accepted")
    else:
        print("❌ Valid configuration rejected")
        return False

    # Test invalid config
    invalid_config = {
        'base_url': 'https://api.bigcapital.ly'
        # Missing api_key
    }

    if not plugin.validate_config(invalid_config):
        print("✅ Invalid configuration properly rejected")
    else:
        print("❌ Invalid configuration accepted")
        return False

    return True

def main():
    """Main test function"""
    print("🚀 Starting BigCapital Plugin InvoicePlane Integration Tests")
    print("=" * 60)

    # Test plugin initialization
    plugin = test_plugin_initialization()
    if not plugin:
        print("\n❌ Plugin initialization failed - stopping tests")
        sys.exit(1)

    # Test configuration validation
    if not test_config_validation():
        print("\n❌ Configuration validation failed")
        sys.exit(1)

    # Test InvoicePlane sync methods
    if not test_invoiceplane_sync_methods(plugin):
        print("\n❌ InvoicePlane sync methods failed")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🎉 All tests passed successfully!")
    print("\n📋 Test Summary:")
    print("  ✅ Plugin initialization")
    print("  ✅ Configuration validation")
    print("  ✅ InvoicePlane data transformation")
    print("  ✅ Status mapping")
    print("  ✅ Contact management methods")
    print("\n💡 Next steps:")
    print("  1. Configure real BigCapital API credentials")
    print("  2. Test with real InvoicePlane data")
    print("  3. Set up automated sync workflows")

if __name__ == "__main__":
    main()