#!/usr/bin/env python3
"""
Test to verify all required dependencies can be imported successfully.
This test helps prevent regression of the PIL import issue.
"""

import unittest
import sys


class TestDependencies(unittest.TestCase):
    """Test that all required dependencies can be imported"""

    def test_pil_import(self):
        """Test that PIL can be imported successfully"""
        try:
            from PIL import Image, ImageOps
            self.assertTrue(True, "PIL import successful")
        except ImportError as e:
            self.fail(f"PIL import failed: {e}")

    def test_pyperclip_import(self):
        """Test that pyperclip can be imported successfully"""
        try:
            import pyperclip
            self.assertTrue(True, "pyperclip import successful")
        except ImportError as e:
            self.fail(f"pyperclip import failed: {e}")

    def test_image_handler_import(self):
        """Test that image_handler module can be imported"""
        try:
            from twodo.image_handler import ImageHandler
            self.assertTrue(True, "ImageHandler import successful")
        except ImportError as e:
            self.fail(f"ImageHandler import failed: {e}")

    def test_cli_import(self):
        """Test that CLI module can be imported without errors"""
        try:
            import twodo.cli
            self.assertTrue(True, "CLI import successful")
        except ImportError as e:
            self.fail(f"CLI import failed: {e}")

    def test_core_dependencies(self):
        """Test all core dependencies can be imported"""
        core_deps = [
            'click',
            'openai', 
            'anthropic',
            'pydantic',
            'yaml',
            'requests',
            'aiohttp',
            'rich',
            'github',
            'git',
            'playwright',
            'psutil'
        ]
        
        failed_imports = []
        for dep in core_deps:
            try:
                if dep == 'yaml':
                    __import__('yaml')
                elif dep == 'github':
                    __import__('github')
                elif dep == 'git':
                    __import__('git')
                else:
                    __import__(dep)
            except ImportError:
                failed_imports.append(dep)
        
        if failed_imports:
            self.fail(f"Failed to import core dependencies: {failed_imports}")


if __name__ == '__main__':
    unittest.main()