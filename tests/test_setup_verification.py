#!/usr/bin/env python3
"""
Setup verification tests for 2DO
Tests to verify that 2DO setup has been successfully completed
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from twodo.config import ConfigManager
from twodo.ai_router import AIRouter
from twodo.github_integration import GitHubIntegration


class TestSetupVerification(unittest.TestCase):
    """Test suite to verify 2DO setup completion"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_dir = Path(self.temp_dir) / "test_config"
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_file_creation(self):
        """Test that configuration file is created properly"""
        config = ConfigManager(self.temp_dir)
        
        # Verify config file exists
        self.assertTrue(config.config_file.exists())
        
        # Verify config structure
        self.assertIn("api_keys", config.config)
        self.assertIn("preferences", config.config)
        self.assertIn("mcp_servers", config.config)
    
    def test_api_key_configuration(self):
        """Test API key configuration and verification"""
        config = ConfigManager(self.temp_dir)
        
        # Test setting API keys
        config.set_api_key("openai", "test-openai-key")
        config.set_api_key("anthropic", "test-anthropic-key")
        config.set_api_key("github", "test-github-token")
        
        # Verify API keys are stored
        self.assertEqual(config.get_api_key("openai"), "test-openai-key")
        self.assertEqual(config.get_api_key("anthropic"), "test-anthropic-key")
        self.assertEqual(config.get_api_key("github"), "test-github-token")
        
        # Test has_api_keys method
        self.assertTrue(config.has_api_keys())
    
    def test_missing_api_keys_detection(self):
        """Test detection of missing API keys"""
        # Use a fresh temp directory for each test
        temp_config_dir = Path(self.temp_dir) / "fresh_config"
        config = ConfigManager(str(temp_config_dir))
        
        # Initially no API keys should be configured in fresh config
        self.assertEqual(len(config.config["api_keys"]), 0)
        self.assertFalse(config.has_api_keys())
        
        # Add only one API key
        config.set_api_key("openai", "test-key")
        self.assertTrue(config.has_api_keys())  # Should return True if any key exists
    
    def test_setup_completeness_check(self):
        """Test comprehensive setup completeness check"""
        # Use a fresh temp directory for each test
        temp_config_dir = Path(self.temp_dir) / "completeness_config"
        config = ConfigManager(str(temp_config_dir))
        
        # Get setup status
        setup_status = self.get_setup_status(config)
        
        # Initially nothing should be configured
        self.assertFalse(setup_status["openai_configured"])
        self.assertFalse(setup_status["anthropic_configured"])
        self.assertFalse(setup_status["github_configured"])
        self.assertFalse(setup_status["is_fully_configured"])
        
        # Configure OpenAI
        config.set_api_key("openai", "test-openai-key")
        setup_status = self.get_setup_status(config)
        self.assertTrue(setup_status["openai_configured"])
        self.assertFalse(setup_status["is_fully_configured"])
        
        # Configure all services
        config.set_api_key("anthropic", "test-anthropic-key")
        config.set_api_key("github", "test-github-token")
        setup_status = self.get_setup_status(config)
        self.assertTrue(setup_status["is_fully_configured"])
    
    def get_setup_status(self, config):
        """Helper method to get comprehensive setup status"""
        return {
            "openai_configured": bool(config.get_api_key("openai") and config.get_api_key("openai").strip()),
            "anthropic_configured": bool(config.get_api_key("anthropic") and config.get_api_key("anthropic").strip()),
            "github_configured": bool(config.get_api_key("github") and config.get_api_key("github").strip()),
            "config_file_exists": config.config_file.exists(),
            "is_fully_configured": all([
                config.get_api_key("openai") and config.get_api_key("openai").strip(),
                config.get_api_key("anthropic") and config.get_api_key("anthropic").strip(),
                config.get_api_key("github") and config.get_api_key("github").strip()
            ])
        }
    
    def test_ai_router_initialization(self):
        """Test that AI router can be initialized with valid config"""
        config = ConfigManager(self.temp_dir)
        config.set_api_key("openai", "test-openai-key")
        config.set_api_key("anthropic", "test-anthropic-key")
        
        # Test AI router initialization
        try:
            ai_router = AIRouter(config)
            self.assertIsNotNone(ai_router)
        except Exception as e:
            self.fail(f"AI Router initialization failed: {e}")
    
    def test_github_integration_initialization(self):
        """Test GitHub integration initialization"""
        # Test without token
        github_integration = GitHubIntegration(None)
        self.assertIsNone(github_integration.github)
        
        # Test with token (don't actually try to connect)
        github_integration = GitHubIntegration("test-token")
        # Just verify it doesn't crash during initialization
        self.assertIsNotNone(github_integration)
    
    def test_local_vs_global_config(self):
        """Test local 2DO folder vs global config detection"""
        # Test non-git directory (should use global config)
        non_git_dir = Path(self.temp_dir) / "non_git"
        non_git_dir.mkdir()
        config1 = ConfigManager(str(non_git_dir))
        self.assertFalse(config1.is_local_project)
        
        # Test git directory (should use local 2DO folder)
        git_dir = Path(self.temp_dir) / "git_repo"
        git_dir.mkdir()
        (git_dir / ".git").mkdir()
        config2 = ConfigManager(str(git_dir))
        self.assertTrue(config2.is_local_project)
        self.assertTrue(str(config2.config_dir).endswith("2DO"))
    
    def test_configuration_migration(self):
        """Test configuration file format migration"""
        config = ConfigManager(self.temp_dir)
        
        # Test that old config formats are handled gracefully
        # (This is future-proofing for configuration changes)
        original_config = config.config.copy()
        
        # Simulate adding new configuration options
        config.config["new_feature"] = {"enabled": True}
        config._save_config()
        
        # Reload config
        config._load_config()
        self.assertIn("new_feature", config.config)
        
        # Verify old config is preserved
        self.assertEqual(config.config["api_keys"], original_config["api_keys"])
        self.assertEqual(config.config["preferences"], original_config["preferences"])
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = ConfigManager(self.temp_dir)
        
        # Test invalid API key formats (if validation exists)
        # This is a placeholder for future validation logic
        config.set_api_key("openai", "")
        self.assertEqual(config.get_api_key("openai"), "")
        
        # Test setting None values
        config.set_api_key("anthropic", None)
        self.assertIsNone(config.get_api_key("anthropic"))
    
    @patch('twodo.ai_router.openai.OpenAI')
    @patch('twodo.ai_router.anthropic.Anthropic')
    def test_ai_models_connectivity(self, mock_anthropic, mock_openai):
        """Test AI models connectivity (mocked)"""
        config = ConfigManager(self.temp_dir)
        config.set_api_key("openai", "test-openai-key")
        config.set_api_key("anthropic", "test-anthropic-key")
        
        # Mock successful API responses
        mock_openai_client = MagicMock()
        mock_anthropic_client = MagicMock()
        mock_openai.return_value = mock_openai_client
        mock_anthropic.return_value = mock_anthropic_client
        
        ai_router = AIRouter(config)
        
        # Verify clients were initialized
        mock_openai.assert_called_once()
        mock_anthropic.assert_called_once()
    
    def test_directory_permissions(self):
        """Test that config directories can be created with proper permissions"""
        # Test in a new directory
        new_config_dir = Path(self.temp_dir) / "new_config_test"
        config = ConfigManager(str(new_config_dir))
        
        # Verify directory was created
        self.assertTrue(config.config_dir.exists())
        self.assertTrue(config.config_dir.is_dir())
        
        # Verify config file can be written
        self.assertTrue(config.config_file.exists())


class TestSetupGuidance(unittest.TestCase):
    """Test setup guidance system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        # Ensure we always get a completely fresh config
        self.test_counter = 0
    
    def get_fresh_config_dir(self):
        """Get a fresh config directory for each test"""
        self.test_counter += 1
        fresh_dir = Path(self.temp_dir) / f"test_config_{self.test_counter}"
        return str(fresh_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_missing_components_detection(self):
        """Test detection of missing setup components"""
        # Use a fresh config directory
        config = ConfigManager(self.get_fresh_config_dir())
        
        missing_components = self.get_missing_setup_components(config)
        
        # Initially all components should be missing
        self.assertIn("openai_api_key", missing_components)
        self.assertIn("anthropic_api_key", missing_components)
        self.assertIn("github_token", missing_components)
    
    def test_setup_progress_tracking(self):
        """Test tracking of setup progress"""
        # Use a fresh config directory
        config = ConfigManager(self.get_fresh_config_dir())
        
        # Initially 0% complete
        progress = self.calculate_setup_progress(config)
        self.assertEqual(progress["percentage"], 0)
        
        # Add one component
        config.set_api_key("openai", "test-key")
        progress = self.calculate_setup_progress(config)
        self.assertGreater(progress["percentage"], 0)
        self.assertLess(progress["percentage"], 100)
        
        # Complete setup
        config.set_api_key("anthropic", "test-key")
        config.set_api_key("github", "test-token")
        progress = self.calculate_setup_progress(config)
        self.assertEqual(progress["percentage"], 100)
    
    def get_missing_setup_components(self, config):
        """Helper to identify missing setup components"""
        missing = []
        
        if not (config.get_api_key("openai") and config.get_api_key("openai").strip()):
            missing.append("openai_api_key")
        if not (config.get_api_key("anthropic") and config.get_api_key("anthropic").strip()):
            missing.append("anthropic_api_key")
        if not (config.get_api_key("github") and config.get_api_key("github").strip()):
            missing.append("github_token")
        
        return missing
    
    def calculate_setup_progress(self, config):
        """Helper to calculate setup completion percentage"""
        total_components = 3  # OpenAI, Anthropic, GitHub
        configured_components = 0
        
        if config.get_api_key("openai") and config.get_api_key("openai").strip():
            configured_components += 1
        if config.get_api_key("anthropic") and config.get_api_key("anthropic").strip():
            configured_components += 1
        if config.get_api_key("github") and config.get_api_key("github").strip():
            configured_components += 1
        
        percentage = (configured_components / total_components) * 100
        
        return {
            "percentage": percentage,
            "configured_components": configured_components,
            "total_components": total_components,
            "missing_components": self.get_missing_setup_components(config)
        }


if __name__ == '__main__':
    unittest.main()