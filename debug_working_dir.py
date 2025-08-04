#!/usr/bin/env python3
"""
Debug script to test working directory context in 2do
"""

import os
import sys
from pathlib import Path

def debug_working_directory():
    """Debug the working directory context"""
    print("=== WORKING DIRECTORY DEBUG ===")
    print(f"os.getcwd(): {os.getcwd()}")
    print(f"Path.cwd(): {Path.cwd()}")
    print(f"sys.path[0]: {sys.path[0]}")
    print(f"__file__ location: {Path(__file__).parent}")
    print(f"Script executed from: {os.getcwd()}")
    
    # Test if we can create a file in current directory
    test_file = Path.cwd() / "test_2do_debug.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("2do debug test")
        print(f"✅ Can write to current directory: {test_file}")
        test_file.unlink()  # Clean up
    except Exception as e:
        print(f"❌ Cannot write to current directory: {e}")

if __name__ == "__main__":
    debug_working_directory()
