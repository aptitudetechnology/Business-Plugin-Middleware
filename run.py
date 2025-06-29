#!/usr/bin/env python3

"""
Simple run script for environments like Replit.
This is a minimal entry point that imports and runs the main application.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import and run main
from main import main

if __name__ == '__main__':
    main()
