#!/usr/bin/env python3

"""
Test script to debug BigCapital invoice creation issues.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from plugins.bigcapitalpy.client import BigCapitalClient
    from plugins.bigcapitalpy.plugin import BigCapitalPlugin
    from config.settings import load_config

    def test_invoice_creation():
        """Test invoice creation with proper data"""
        print("Testing BigCapital invoice creation...")

        # Load config
        config = load_config()
        if not config:
            print("Failed to load config")
            return

        # Get BigCapital config
        bigcapital_config = config.get('plugins', {}).get('bigcapitalpy', {})
        if not bigcapital_config:
            print("BigCapital config not found")
            return

        # Create client
        client = BigCapitalClient(
            api_key=bigcapital_config.get('api_key'),
            base_url=bigcapital_config.get('base_url')
        )

        # Test data that should work
        test_invoice = {
            'customer_id': 1,  # Assuming customer ID 1 exists
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'due_date': (datetime.now().replace(day=datetime.now().day + 30)).strftime('%Y-%m-%d'),
            'currency': 'USD',
            'line_items': [
                {
                    'description': 'Test consulting services',
                    'quantity': 1,
                    'rate': 100.00
                }
            ]
        }

        print(f"Test invoice data: {test_invoice}")

        try:
            result = client.create_invoice(test_invoice)
            if result:
                print(f"✅ Invoice created successfully: {result}")
            else:
                print("❌ Invoice creation failed - check logs for details")
        except Exception as e:
            print(f"❌ Exception during invoice creation: {e}")

    if __name__ == '__main__':
        test_invoice_creation()

except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required dependencies")