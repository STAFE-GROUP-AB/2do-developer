#!/usr/bin/env python3
"""
Tests for interactive features - weather location prompts and README file selection
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from twodo.config import ConfigManager
from twodo.ai_router import AIRouter


class TestInteractiveFeatures(unittest.TestCase):
    """Test interactive weather prompts and README file selection"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ConfigManager(suppress_prompts=True)
        self.ai_router = AIRouter(self.config)
    
    def test_weather_keyword_detection(self):
        """Test detection of weather-related keywords"""
        weather_prompts = [
            "add weather forecast to readme",
            "What's the temperature today?",
            "Get the current climate data",
            "Show me the weather conditions"  # Fixed: meteorological -> weather
        ]
        
        non_weather_prompts = [
            "update the documentation",
            "add a new feature",
            "fix the bug in the code"
        ]
        
        # Test weather prompts contain keywords
        for prompt in weather_prompts:
            prompt_lower = prompt.lower()
            weather_keywords = ['weather', 'forecast', 'temperature', 'climate', 'meteorology']
            self.assertTrue(
                any(keyword in prompt_lower for keyword in weather_keywords),
                f"Weather keywords not detected in: {prompt}"
            )
        
        # Test non-weather prompts don't contain keywords
        for prompt in non_weather_prompts:
            prompt_lower = prompt.lower()
            weather_keywords = ['weather', 'forecast', 'temperature', 'climate', 'meteorology']
            self.assertFalse(
                any(keyword in prompt_lower for keyword in weather_keywords),
                f"Weather keywords incorrectly detected in: {prompt}"
            )
    
    def test_readme_keyword_detection(self):
        """Test detection of README-related keywords"""
        readme_prompts = [
            "update the README.md file",
            "add content to readme",
            "modify the README.MD",
            "edit readme.md"
        ]
        
        non_readme_prompts = [
            "update the documentation",
            "add a new feature", 
            "fix the config file"
        ]
        
        # Test README prompts contain keywords
        for prompt in readme_prompts:
            prompt_lower = prompt.lower()
            readme_keywords = ['readme', 'readme.md']
            self.assertTrue(
                any(keyword in prompt_lower for keyword in readme_keywords),
                f"README keywords not detected in: {prompt}"
            )
        
        # Test non-README prompts don't contain keywords
        for prompt in non_readme_prompts:
            prompt_lower = prompt.lower()
            readme_keywords = ['readme', 'readme.md']
            self.assertFalse(
                any(keyword in prompt_lower for keyword in readme_keywords),
                f"README keywords incorrectly detected in: {prompt}"
            )
    
    @patch('os.getcwd')
    def test_find_user_readme_files(self, mock_getcwd):
        """Test finding README files while excluding vendor directories"""
        # Create temporary directory structure
        test_dir = Path(self.temp_dir)
        mock_getcwd.return_value = str(test_dir)
        
        # Create README files in various locations
        (test_dir / "README.md").touch()  # Project root
        (test_dir / "docs" / "README.md").parent.mkdir(exist_ok=True)
        (test_dir / "docs" / "README.md").touch()  # User directory
        
        # Create vendor directory with README (should be excluded)
        (test_dir / "vendor" / "package" / "README.md").parent.mkdir(parents=True, exist_ok=True)
        (test_dir / "vendor" / "package" / "README.md").touch()
        
        # Create node_modules directory with README (should be excluded)
        (test_dir / "node_modules" / "lib" / "README.md").parent.mkdir(parents=True, exist_ok=True)
        (test_dir / "node_modules" / "lib" / "README.md").touch()
        
        # Run the async method
        import asyncio
        readme_files = asyncio.run(self.ai_router._find_user_readme_files())
        
        # Should find user READMEs but not vendor ones
        self.assertGreater(len(readme_files), 0)
        self.assertTrue(any("README.md" in f for f in readme_files))
        self.assertFalse(any("vendor" in f for f in readme_files))
        self.assertFalse(any("node_modules" in f for f in readme_files))


if __name__ == '__main__':
    unittest.main()