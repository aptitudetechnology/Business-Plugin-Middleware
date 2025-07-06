#!/usr/bin/env python3
"""
Database migration test script for BigCapitalPy
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, '/app')

try:
    from packages.server.src.database import db
    from app import create_app
    
    # Create application instance
    app = create_app()
    
    # Create database schema
    with app.app_context():
        db.create_all()
        print('✓ Database schema created successfully')
        
        # Optional: Test that we can query the database
        from packages.server.src.models import Account
        account_count = Account.query.count()
        print(f'✓ Database connection verified (accounts: {account_count})')
        
except Exception as e:
    print(f'✗ Database migration test failed: {e}')
    sys.exit(1)