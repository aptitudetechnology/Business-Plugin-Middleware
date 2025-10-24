#!/usr/bin/env python3

"""
Test script to debug invoice sync duplication issue.
This script simulates the sync process with detailed logging.
"""

import sys
import os
import logging
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_sync_with_mock_data():
    """Test sync with mock invoice data"""
    try:
        from plugins.bigcapitalpy.plugin import BigCapitalPlugin
        from config.settings import Config

        # Load configuration
        config = Config()
        config.load()

        # Create plugin instance
        plugin = BigCapitalPlugin(config)

        # Initialize plugin
        if not plugin.initialize():
            print("Failed to initialize plugin")
            return

        # Mock invoice data that might cause duplication
        mock_invoice_data = {
            'id': '123',
            'invoice_number': 'INV-2024-001',
            'status': 'sent',
            'status_name': 'sent',
            'client': {
                'name': 'Test Client',
                'email': 'test@example.com',
                'address': '123 Test St'
            },
            'items': [
                {
                    'name': 'Test Service',
                    'description': 'Test service description',
                    'quantity': 1,
                    'price': 100.00,
                    'total': 100.00
                }
            ],
            'issue_date': '2024-01-15',
            'due_date': '2024-02-15'
        }

        print("Testing sync with mock invoice data...")
        print(f"Invoice data: {mock_invoice_data}")

        # Run sync
        result = plugin.sync_invoice_from_invoiceplane(mock_invoice_data)

        print(f"Sync result: {result}")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_sync_with_mock_data()