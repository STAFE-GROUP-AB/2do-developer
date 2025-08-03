#!/usr/bin/env python3
"""
Interactive guidance and setup tests for 2DO
Tests the interactive setup guidance system and user workflows
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from twodo.setup_guide import SetupGuide
from twodo.config import ConfigManager


class TestSetupGuidanceSystem(unittest.TestCase):
    """Test the interactive setup guidance system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.console_output = StringIO()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_setup_guide_initialization(self):
        """Test SetupGuide initialization"""
        guide = SetupGuide()
        self.assertIsNotNone(guide)
        self.assertIsNotNone(guide.console)
    
    def test_comprehensive_setup_status_detection(self):
        """Test comprehensive setup status detection"""
        # Create a config with partial setup
        config = ConfigManager(self.temp_dir)
        config.set_api_key("openai", "test-key")
        
        guide = SetupGuide()
        guide.config = config
        
        status = guide.get_comprehensive_setup_status()
        
        # Verify status structure
        required_keys = [
            "config_file_exists", "config_directory_exists", "is_local_project",
            "openai_configured", "anthropic_configured", "github_configured",
            "has_any_api_keys", "memory_enabled", "max_parallel_tasks",
            "configuration_percentage", "is_fully_configured"
        ]
        
        for key in required_keys:
            self.assertIn(key, status)
        
        # Verify partial configuration
        self.assertTrue(status["openai_configured"])
        self.assertFalse(status["anthropic_configured"])
        self.assertFalse(status["github_configured"])
        self.assertFalse(status["is_fully_configured"])
        self.assertGreater(status["configuration_percentage"], 0)
        self.assertLess(status["configuration_percentage"], 100)
    
    def test_missing_components_detection(self):
        """Test detection of missing setup components"""
        config = ConfigManager(self.temp_dir)
        
        guide = SetupGuide()
        guide.config = config
        
        status = guide.get_comprehensive_setup_status()
        
        # All components should be missing initially
        self.assertFalse(status["openai_configured"])
        self.assertFalse(status["anthropic_configured"])
        self.assertFalse(status["github_configured"])
        self.assertEqual(status["configuration_percentage"], 0)
        
        # Add one component
        config.set_api_key("openai", "test-key")
        status = guide.get_comprehensive_setup_status()
        
        self.assertTrue(status["openai_configured"])
        self.assertFalse(status["anthropic_configured"])
        self.assertFalse(status["github_configured"])
        self.assertAlmostEqual(status["configuration_percentage"], 33.33, places=1)
    
    def test_project_setup_verification(self):
        """Test project-specific setup verification"""
        # Create a git repository structure
        git_repo = Path(self.temp_dir) / "test_repo"
        git_repo.mkdir()
        (git_repo / ".git").mkdir()
        
        guide = SetupGuide()
        
        # This should not raise an exception
        try:
            status = guide.verify_project_setup(str(git_repo))
            self.assertIsInstance(status, dict)
        except Exception as e:
            self.fail(f"Project setup verification failed: {e}")
    
    def test_setup_progress_calculation(self):
        """Test setup progress calculation"""
        config = ConfigManager(self.temp_dir)
        guide = SetupGuide()
        guide.config = config
        
        # 0% initially
        status = guide.get_comprehensive_setup_status()
        self.assertEqual(status["configuration_percentage"], 0)
        
        # 33.33% with one component
        config.set_api_key("openai", "test-key")
        status = guide.get_comprehensive_setup_status()
        self.assertAlmostEqual(status["configuration_percentage"], 33.33, places=1)
        
        # 66.67% with two components
        config.set_api_key("anthropic", "test-key")
        status = guide.get_comprehensive_setup_status()
        self.assertAlmostEqual(status["configuration_percentage"], 66.67, places=1)
        
        # 100% with all components
        config.set_api_key("github", "test-token")
        status = guide.get_comprehensive_setup_status()
        self.assertEqual(status["configuration_percentage"], 100)
        self.assertTrue(status["is_fully_configured"])
    
    @patch('twodo.setup_guide.Confirm.ask')
    @patch('twodo.setup_guide.Prompt.ask')
    def test_interactive_configuration_flow(self, mock_prompt, mock_confirm):
        """Test interactive configuration flow"""
        # Mock user inputs
        mock_confirm.return_value = True
        mock_prompt.return_value = "test-api-key"
        
        config = ConfigManager(self.temp_dir)
        guide = SetupGuide()
        guide.config = config
        
        # Test individual configuration methods
        guide.configure_openai()
        self.assertEqual(config.get_api_key("openai"), "test-api-key")
        
        guide.configure_anthropic()
        self.assertEqual(config.get_api_key("anthropic"), "test-api-key")
        
        guide.configure_github()
        self.assertEqual(config.get_api_key("github"), "test-api-key")
    
    @patch('twodo.setup_guide.Confirm.ask')
    def test_user_decline_configuration(self, mock_confirm):
        """Test when user declines configuration"""
        mock_confirm.return_value = False
        
        config = ConfigManager(self.temp_dir)
        guide = SetupGuide()
        guide.config = config
        
        # User declines configuration
        guide.configure_openai()
        self.assertIsNone(config.get_api_key("openai"))
        
        guide.configure_anthropic()
        self.assertIsNone(config.get_api_key("anthropic"))
        
        guide.configure_github()
        self.assertIsNone(config.get_api_key("github"))
    
    def test_connectivity_test_structure(self):
        """Test connectivity test structure"""
        config = ConfigManager(self.temp_dir)
        config.set_api_key("openai", "sk-test-key")
        config.set_api_key("anthropic", "test-anthropic-key")
        config.set_api_key("github", "ghp_test_token")
        
        guide = SetupGuide()
        guide.config = config
        
        # This should run without errors (even if connectivity fails)
        try:
            guide.run_connectivity_tests()
        except Exception as e:
            self.fail(f"Connectivity tests should not raise exceptions: {e}")
    
    def test_local_vs_global_project_detection(self):
        """Test local vs global project detection"""
        # Test non-git directory
        non_git_dir = Path(self.temp_dir) / "non_git"
        non_git_dir.mkdir()
        
        guide = SetupGuide()
        status = guide.run_complete_setup_check(str(non_git_dir))
        self.assertFalse(status["is_local_project"])
        
        # Test git directory
        git_dir = Path(self.temp_dir) / "git_repo"
        git_dir.mkdir()
        (git_dir / ".git").mkdir()
        
        status = guide.run_complete_setup_check(str(git_dir))
        self.assertTrue(status["is_local_project"])


class TestInteractiveWorkflows(unittest.TestCase):
    """Test complete interactive workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('twodo.setup_guide.Confirm.ask')
    @patch('twodo.setup_guide.Prompt.ask')
    def test_complete_setup_workflow(self, mock_prompt, mock_confirm):
        """Test complete setup workflow from start to finish"""
        # Mock user responses for complete setup
        mock_confirm.side_effect = [True, True, True]  # Yes to all configurations
        mock_prompt.side_effect = [
            "sk-test-openai-key",
            "test-anthropic-key", 
            "ghp_test_github_token"
        ]
        
        guide = SetupGuide()
        
        # Run complete setup
        status = guide.run_complete_setup_check(self.temp_dir)
        
        # Verify complete setup
        self.assertTrue(status["is_fully_configured"])
        self.assertEqual(status["configuration_percentage"], 100)
        self.assertTrue(status["openai_configured"])
        self.assertTrue(status["anthropic_configured"])
        self.assertTrue(status["github_configured"])
    
    @patch('twodo.setup_guide.Confirm.ask')
    @patch('twodo.setup_guide.Prompt.ask')
    def test_partial_setup_workflow(self, mock_prompt, mock_confirm):
        """Test partial setup workflow"""
        # Mock user responses for partial setup
        mock_confirm.side_effect = [True, False, False, False]  # Only configure OpenAI
        mock_prompt.side_effect = ["sk-test-openai-key"]
        
        guide = SetupGuide()
        
        # Run setup
        status = guide.run_complete_setup_check(self.temp_dir)
        
        # Verify partial setup
        self.assertFalse(status["is_fully_configured"])
        self.assertAlmostEqual(status["configuration_percentage"], 33.33, places=1)
        self.assertTrue(status["openai_configured"])
        self.assertFalse(status["anthropic_configured"])
        self.assertFalse(status["github_configured"])
    
    @patch('twodo.setup_guide.Confirm.ask')
    def test_user_skips_all_configuration(self, mock_confirm):
        """Test when user skips all configuration"""
        mock_confirm.return_value = False  # No to everything
        
        guide = SetupGuide()
        
        # Run setup
        status = guide.run_complete_setup_check(self.temp_dir)
        
        # Verify no configuration
        self.assertFalse(status["is_fully_configured"])
        self.assertEqual(status["configuration_percentage"], 0)
        self.assertFalse(status["openai_configured"])
        self.assertFalse(status["anthropic_configured"])
        self.assertFalse(status["github_configured"])
    
    def test_existing_configuration_detection(self):
        """Test detection of existing configuration"""
        # Pre-configure some settings
        config = ConfigManager(self.temp_dir)
        config.set_api_key("openai", "existing-key")
        config.set_api_key("github", "existing-token")
        
        guide = SetupGuide()
        
        # Run setup check
        status = guide.run_complete_setup_check(self.temp_dir)
        
        # Should detect existing configuration
        self.assertTrue(status["openai_configured"])
        self.assertTrue(status["github_configured"])
        self.assertFalse(status["anthropic_configured"])
        self.assertAlmostEqual(status["configuration_percentage"], 66.67, places=1)


class TestSetupGuidanceEdgeCases(unittest.TestCase):
    """Test edge cases in setup guidance"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_api_key_handling(self):
        """Test handling of empty API keys"""
        config = ConfigManager(self.temp_dir)
        guide = SetupGuide()
        guide.config = config
        
        # Set empty API keys
        config.set_api_key("openai", "")
        config.set_api_key("anthropic", None)
        
        status = guide.get_comprehensive_setup_status()
        
        # Empty keys should be treated as not configured
        self.assertFalse(status["openai_configured"])
        self.assertFalse(status["anthropic_configured"])
    
    def test_invalid_directory_handling(self):
        """Test handling of invalid directories"""
        guide = SetupGuide()
        
        # Test with non-existent directory
        try:
            status = guide.run_complete_setup_check("/non/existent/directory")
            # Should handle gracefully and create config in default location
            self.assertIsInstance(status, dict)
        except Exception as e:
            self.fail(f"Should handle invalid directories gracefully: {e}")
    
    def test_permission_error_handling(self):
        """Test handling of permission errors"""
        # This test is platform-dependent and might not work on all systems
        # It's included for completeness but might be skipped
        guide = SetupGuide()
        
        try:
            # Try to use a directory that might have permission issues
            restricted_dir = "/root" if os.path.exists("/root") else self.temp_dir
            status = guide.run_complete_setup_check(restricted_dir)
            self.assertIsInstance(status, dict)
        except PermissionError:
            # This is expected and acceptable
            pass
        except Exception as e:
            # Other exceptions should be handled gracefully
            self.fail(f"Unexpected exception in permission test: {e}")
    
    def test_corrupted_config_handling(self):
        """Test handling of corrupted configuration files"""
        # Create a corrupted config file
        config_dir = Path(self.temp_dir) / "corrupted_config"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        
        # Write invalid YAML
        config_file.write_text("invalid: yaml: content: [")
        
        guide = SetupGuide()
        
        # Should handle corrupted config gracefully
        try:
            status = guide.run_complete_setup_check(str(config_dir))
            self.assertIsInstance(status, dict)
        except Exception as e:
            self.fail(f"Should handle corrupted config gracefully: {e}")


class TestSetupValidation(unittest.TestCase):
    """Test setup validation and verification"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_api_key_format_validation(self):
        """Test API key format validation"""
        guide = SetupGuide()
        
        # Test OpenAI key format
        config = ConfigManager(self.temp_dir)
        guide.config = config
        
        # Valid OpenAI key format
        config.set_api_key("openai", "sk-1234567890abcdef")
        status = guide.get_comprehensive_setup_status()
        self.assertTrue(status["openai_configured"])
        
        # Invalid format (but still should be considered configured)
        config.set_api_key("openai", "invalid-key")
        status = guide.get_comprehensive_setup_status()
        self.assertTrue(status["openai_configured"])  # We don't validate format strictly
    
    def test_configuration_completeness_check(self):
        """Test configuration completeness checking"""
        config = ConfigManager(self.temp_dir)
        guide = SetupGuide()
        guide.config = config
        
        # Check completeness at different stages
        status = guide.get_comprehensive_setup_status()
        self.assertFalse(status["is_fully_configured"])
        
        config.set_api_key("openai", "test")
        status = guide.get_comprehensive_setup_status()
        self.assertFalse(status["is_fully_configured"])
        
        config.set_api_key("anthropic", "test")
        status = guide.get_comprehensive_setup_status()
        self.assertFalse(status["is_fully_configured"])
        
        config.set_api_key("github", "test")
        status = guide.get_comprehensive_setup_status()
        self.assertTrue(status["is_fully_configured"])
    
    def test_preference_validation(self):
        """Test preference validation"""
        config = ConfigManager(self.temp_dir)
        guide = SetupGuide()
        guide.config = config
        
        status = guide.get_comprehensive_setup_status()
        
        # Check default preferences
        self.assertTrue(status["memory_enabled"])
        self.assertEqual(status["max_parallel_tasks"], 5)
        
        # Modify preferences
        config.set_preference("memory_enabled", False)
        config.set_preference("max_parallel_tasks", 10)
        
        status = guide.get_comprehensive_setup_status()
        self.assertFalse(status["memory_enabled"])
        self.assertEqual(status["max_parallel_tasks"], 10)


if __name__ == '__main__':
    unittest.main()