#!/usr/bin/env python3

"""
Debug script to test invoice retrieval from InvoicePlane
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from plugins.invoiceplanepy.client import InvoicePlaneClient
    from config.settings import Config

    def test_invoice_retrieval():
        """Test retrieving specific invoices"""
        print("Testing InvoicePlane invoice retrieval...")

        # Load config
        config = Config()
        if not config:
            print("Failed to load config")
            return

        # Get InvoicePlane config
        invoiceplane_config = config.get_plugin_config('invoiceplanepy')
        if not invoiceplane_config:
            print("InvoicePlane config not found")
            return

        # Create client
        client = InvoicePlaneClient(
            api_key=invoiceplane_config.get('api_key'),
            base_url=invoiceplane_config.get('base_url')
        )

        # Test different invoice IDs
        test_ids = ['1527', '1489', '63', '31']

        for invoice_id in test_ids:
            print(f"\n--- Testing invoice ID: {invoice_id} ---")
            try:
                invoice = client.get_invoice(invoice_id)
                if invoice:
                    print(f"✅ Found invoice:")
                    print(f"  ID: {invoice.get('id')}")
                    print(f"  Invoice Number: {invoice.get('invoice_number')}")
                    print(f"  Client: {invoice.get('client', {}).get('name', 'N/A')}")
                    print(f"  Total: {invoice.get('total', 'N/A')}")
                    print(f"  Items count: {len(invoice.get('items', []))}")
                    if invoice.get('items'):
                        print(f"  First item: {invoice['items'][0]}")
                    else:
                        print("  ❌ No items found!")
                else:
                    print(f"❌ Invoice {invoice_id} not found")
            except Exception as e:
                print(f"❌ Error retrieving invoice {invoice_id}: {e}")

    if __name__ == '__main__':
        test_invoice_retrieval()

except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required dependencies")