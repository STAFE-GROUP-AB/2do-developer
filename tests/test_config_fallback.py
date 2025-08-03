#!/usr/bin/env python3
"""
Test script for config fallback functionality
"""
import unittest
import tempfile
import shutil
from pathlib import Path
import yaml
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/runner/work/2do-developer/2do-developer')

from twodo.config import ConfigManager


class TestConfigFallback(unittest.TestCase):
    """Test configuration fallback functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_config_fallback_functionality(self):
        """Test that local config gets global values when empty"""
        # Create a git repository
        git_repo = Path(self.temp_dir) / "test_repo"
        git_repo.mkdir()
        (git_repo / ".git").mkdir()
        
        # Create a fake global config with API keys
        global_config_dir = Path(self.temp_dir) / "fake_global"
        global_config_dir.mkdir()
        global_config_file = global_config_dir / "config.yaml"
        
        global_config = {
            "api_keys": {
                "openai": "sk-test-openai-key",
                "anthropic": "test-anthropic-key",
                "github": "ghp-test-github-token"
            },
            "preferences": {
                "default_model": "auto",
                "max_parallel_tasks": 5,
                "memory_enabled": True
            },
            "mcp_servers": []
        }
        
        with open(global_config_file, 'w') as f:
            yaml.dump(global_config, f)
        
        # Create config manager for the git repo (suppress prompts)
        config_manager = ConfigManager(str(git_repo), suppress_prompts=True)
        
        # Override the global config file path for testing
        config_manager.global_config_file = global_config_file
        
        # Initially, local config should be empty
        self.assertFalse(config_manager._config_has_api_keys(config_manager.config))
        
        # Test loading global config
        global_config_loaded = config_manager._load_global_config()
        self.assertIsNotNone(global_config_loaded)
        self.assertTrue(config_manager._config_has_api_keys(global_config_loaded))
        
        # Test manual copying of global config to local
        config_manager._copy_global_to_local(global_config_loaded)
        
        # After copying, local config should have the keys
        self.assertTrue(config_manager._config_has_api_keys(config_manager.config))
        
        # Test that all expected keys are available
        expected_providers = ['openai', 'anthropic', 'github']
        actual_providers = config_manager.get_available_providers()
        
        for provider in expected_providers:
            self.assertIn(provider, actual_providers)
            self.assertIsNotNone(config_manager.get_api_key(provider))
            self.assertNotEqual(config_manager.get_api_key(provider), "")
        
        # Verify the local config file was actually written
        self.assertTrue(config_manager.config_file.exists())
        
        with open(config_manager.config_file, 'r') as f:
            local_config = yaml.safe_load(f)
        
        # Check that the local file contains the copied keys
        for provider in expected_providers:
            self.assertIn(provider, local_config['api_keys'])
            self.assertEqual(
                local_config['api_keys'][provider], 
                global_config['api_keys'][provider]
            )
    
    def test_config_has_api_keys(self):
        """Test the _config_has_api_keys method"""
        config_manager = ConfigManager(suppress_prompts=True)
        
        # Test empty config
        empty_config = {"api_keys": {}}
        self.assertFalse(config_manager._config_has_api_keys(empty_config))
        
        # Test config with null/empty values
        null_config = {
            "api_keys": {
                "openai": None,
                "anthropic": "",
                "github": "null"
            }
        }
        self.assertFalse(config_manager._config_has_api_keys(null_config))
        
        # Test config with valid keys
        valid_config = {
            "api_keys": {
                "openai": "sk-valid-key",
                "anthropic": None,  # This one is null but others are valid
                "github": "ghp-valid-token"
            }
        }
        self.assertTrue(config_manager._config_has_api_keys(valid_config))
    
    def test_non_git_repo_no_fallback(self):
        """Test that non-git repos don't trigger fallback"""
        # Create a non-git directory
        non_git_dir = Path(self.temp_dir) / "non_git"
        non_git_dir.mkdir()
        
        # Create config manager for non-git directory
        config_manager = ConfigManager(str(non_git_dir), suppress_prompts=True)
        
        # Should not be a local project
        self.assertFalse(config_manager.is_local_project)
        
        # Should use global config directory
        expected_global_dir = Path.home() / ".2do"
        self.assertEqual(config_manager.config_dir, expected_global_dir)


if __name__ == '__main__':
    unittest.main()