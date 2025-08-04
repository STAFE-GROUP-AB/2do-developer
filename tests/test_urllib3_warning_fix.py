#!/usr/bin/env python3
"""
Test for urllib3 NotOpenSSLWarning suppression fix
This test verifies that the CLI properly suppresses urllib3 warnings on macOS/LibreSSL systems
"""

import unittest
import warnings
import urllib3
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/runner/work/2do-developer/2do-developer')

class TestUrllib3WarningSuppression(unittest.TestCase):
    """Test that urllib3 NotOpenSSLWarning is properly suppressed"""
    
    def test_cli_import_suppresses_warnings(self):
        """Test that importing CLI suppresses urllib3 NotOpenSSLWarning"""
        
        # Test the real scenario: import CLI and see if it suppresses future urllib3 warnings
        # Note: We don't override warnings filters in this test to simulate real usage
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("default")  # Use default warning behavior
            
            # Import the CLI module (this should call urllib3.disable_warnings)
            import twodo.cli
            
            # Test that urllib3 warnings are now filtered
            # Check the current warning filters
            openssl_filters = [
                f for f in warnings.filters 
                if f[2] == urllib3.exceptions.NotOpenSSLWarning and f[0] == 'ignore'
            ]
            
            self.assertGreater(
                len(openssl_filters), 0,
                "urllib3.disable_warnings should have added an 'ignore' filter for NotOpenSSLWarning"
            )
    
    def test_cli_functionality_preserved(self):
        """Test that CLI functionality is preserved after warning suppression"""
        
        # Import CLI and verify it works
        from twodo.cli import cli
        
        # Verify that basic CLI commands are available
        commands = cli.list_commands(None)
        expected_commands = ['mcp', 'setup', 'start', 'verify']
        
        for cmd in expected_commands:
            self.assertIn(cmd, commands, f"Command '{cmd}' not found in CLI commands: {commands}")
    
    def test_urllib3_warning_filter_installed(self):
        """Test that urllib3.disable_warnings installs the correct filter"""
        
        # Save current warning filters
        original_filters = warnings.filters.copy()
        
        try:
            # Reset filters to clean state
            warnings.resetwarnings()
            
            # Apply urllib3.disable_warnings
            urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
            
            # Check that a filter was added for NotOpenSSLWarning
            openssl_filters = [
                f for f in warnings.filters 
                if len(f) >= 3 and f[2] == urllib3.exceptions.NotOpenSSLWarning and f[0] == 'ignore'
            ]
            
            self.assertGreater(
                len(openssl_filters), 0,
                f"urllib3.disable_warnings should add an 'ignore' filter for NotOpenSSLWarning. Current filters: {warnings.filters}"
            )
            
        finally:
            # Restore original warning filters
            warnings.filters[:] = original_filters

if __name__ == '__main__':
    unittest.main()