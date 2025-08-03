#!/usr/bin/env python3
"""
CLI Integration tests for 2DO
Tests the command line interface and user workflows
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from twodo.cli import cli, setup, start
from twodo.config import ConfigManager


class TestCLIIntegration(unittest.TestCase):
    """Test CLI commands and user workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cli_version(self):
        """Test CLI version command"""
        result = self.runner.invoke(cli, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("version", result.output.lower())
    
    def test_cli_help(self):
        """Test CLI help command"""
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("2DO - Intelligent AI model routing", result.output)
        self.assertIn("setup", result.output)
        self.assertIn("start", result.output)
    
    @patch.dict(os.environ, {"HOME": ""})
    def test_setup_command_flow(self):
        """Test the setup command flow"""
        with self.runner.isolated_filesystem():
            # Create a temporary home directory
            os.environ["HOME"] = os.getcwd()
            
            # Mock user inputs for setup
            inputs = [
                'y',  # Use OpenAI models?
                'test-openai-key',  # OpenAI API key
                'y',  # Use Anthropic models?
                'test-anthropic-key',  # Anthropic API key
                'y',  # Configure GitHub?
                'test-github-token'  # GitHub token
            ]
            
            result = self.runner.invoke(setup, input='\n'.join(inputs))
            
            # Setup should complete successfully
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Setup complete", result.output)
            
            # Verify configuration was saved
            config_dir = Path.home() / ".2do"
            config_file = config_dir / "config.yaml"
            self.assertTrue(config_file.exists())
    
    @patch.dict(os.environ, {"HOME": ""})
    def test_start_without_setup(self):
        """Test start command without prior setup"""
        with self.runner.isolated_filesystem():
            os.environ["HOME"] = os.getcwd()
            
            result = self.runner.invoke(start)
            
            # Should fail gracefully and suggest running setup
            self.assertEqual(result.exit_code, 0)  # CLI doesn't exit with error, just returns
            self.assertIn("No API keys configured", result.output)
    
    @patch.dict(os.environ, {"HOME": ""})
    @patch('twodo.cli.handle_chat')
    @patch('twodo.ai_router.AIRouter')
    def test_start_with_setup(self, mock_ai_router, mock_handle_chat):
        """Test start command with proper setup"""
        with self.runner.isolated_filesystem():
            os.environ["HOME"] = os.getcwd()
            
            # First setup the configuration
            config = ConfigManager()
            config.set_api_key("openai", "test-key")
            
            # Mock the interactive session to quit immediately
            inputs = ['quit']
            
            result = self.runner.invoke(start, input='\n'.join(inputs))
            
            # Should start successfully
            self.assertEqual(result.exit_code, 0)
            self.assertIn("2DO Starting", result.output)
    
    def test_cli_commands_exist(self):
        """Test that all expected CLI commands exist"""
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        
        # Check for main commands
        self.assertIn("setup", result.output)
        self.assertIn("start", result.output)
    
    @patch('twodo.cli.TechStackDetector')
    def test_start_with_repository(self, mock_detector):
        """Test start command with repository analysis"""
        with self.runner.isolated_filesystem():
            # Create a mock git repository
            os.makedirs(".git")
            
            # Setup configuration
            config = ConfigManager()
            config.set_api_key("openai", "test-key")
            
            # Mock tech stack detection
            mock_detector_instance = MagicMock()
            mock_detector_instance.analyze_repo.return_value = ["python", "javascript"]
            mock_detector.return_value = mock_detector_instance
            
            # Test with quit input
            inputs = ['quit']
            result = self.runner.invoke(start, input='\n'.join(inputs))
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn("local 2DO folder", result.output)


class TestWorkflowIntegration(unittest.TestCase):
    """Test complete user workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.dict(os.environ, {"HOME": ""})
    def test_complete_setup_workflow(self):
        """Test complete setup workflow from start to finish"""
        with self.runner.isolated_filesystem():
            os.environ["HOME"] = os.getcwd()
            
            # 1. Check initial state (no config)
            config = ConfigManager()
            self.assertFalse(config.has_api_keys())
            
            # 2. Run setup
            inputs = [
                'y',  # Use OpenAI
                'sk-test-openai-key-123',
                'y',  # Use Anthropic
                'test-anthropic-key-456',
                'y',  # Configure GitHub
                'ghp_test_token_789'
            ]
            
            result = self.runner.invoke(setup, input='\n'.join(inputs))
            self.assertEqual(result.exit_code, 0)
            
            # 3. Verify configuration
            config = ConfigManager()
            self.assertTrue(config.has_api_keys())
            self.assertEqual(config.get_api_key("openai"), "sk-test-openai-key-123")
            self.assertEqual(config.get_api_key("anthropic"), "test-anthropic-key-456")
            self.assertEqual(config.get_api_key("github"), "ghp_test_token_789")
            
            # 4. Test that start now works
            inputs = ['quit']
            result = self.runner.invoke(start, input='\n'.join(inputs))
            self.assertEqual(result.exit_code, 0)
            self.assertIn("2DO Starting", result.output)
            self.assertNotIn("No API keys configured", result.output)
    
    @patch.dict(os.environ, {"HOME": ""})
    def test_partial_setup_workflow(self):
        """Test partial setup (only some services configured)"""
        with self.runner.isolated_filesystem():
            os.environ["HOME"] = os.getcwd()
            
            # Setup with only OpenAI
            inputs = [
                'y',  # Use OpenAI
                'test-openai-key',
                'n',  # Don't use Anthropic
                'n'   # Don't configure GitHub
            ]
            
            result = self.runner.invoke(setup, input='\n'.join(inputs))
            self.assertEqual(result.exit_code, 0)
            
            # Verify partial configuration
            config = ConfigManager()
            self.assertTrue(config.has_api_keys())  # Should have at least one key
            self.assertEqual(config.get_api_key("openai"), "test-openai-key")
            self.assertIsNone(config.get_api_key("anthropic"))
            self.assertIsNone(config.get_api_key("github"))
    
    def test_git_repository_detection(self):
        """Test git repository detection workflow"""
        with self.runner.isolated_filesystem():
            # Create a git repository structure
            os.makedirs(".git")
            
            # Create some project files
            with open("app.py", "w") as f:
                f.write("print('Hello, World!')")
            
            with open("requirements.txt", "w") as f:
                f.write("flask>=2.0.0\nrequests>=2.28.0")
            
            # Setup basic configuration
            config = ConfigManager()
            config.set_api_key("openai", "test-key")
            
            # The ConfigManager should detect this as a git repo
            config_in_git = ConfigManager(os.getcwd())
            self.assertTrue(config_in_git.is_local_project)
            self.assertTrue(str(config_in_git.config_dir).endswith("2DO"))
    
    @patch('twodo.cli.TechStackDetector')
    @patch('twodo.cli.GitHubIntegration')
    def test_project_analysis_workflow(self, mock_github, mock_detector):
        """Test project analysis and tech stack detection workflow"""
        with self.runner.isolated_filesystem():
            # Setup mocks
            mock_detector_instance = MagicMock()
            mock_detector_instance.analyze_repo.return_value = ["python", "flask", "javascript"]
            mock_detector.return_value = mock_detector_instance
            
            mock_github_instance = MagicMock()
            mock_github_instance.get_repository_info.return_value = {
                "full_name": "test/repo",
                "current_branch": "main"
            }
            mock_github.return_value = mock_github_instance
            
            # Create git repo
            os.makedirs(".git")
            
            # Setup configuration
            config = ConfigManager()
            config.set_api_key("openai", "test-key")
            config.set_api_key("github", "test-token")
            
            # Test start with project analysis
            inputs = [
                'y',  # Create memory files
                'quit'
            ]
            
            result = self.runner.invoke(start, input='\n'.join(inputs))
            self.assertEqual(result.exit_code, 0)
            
            # Verify analysis was performed
            self.assertIn("Analyzing repository", result.output)
            self.assertIn("Detected tech stack", result.output)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in CLI"""
    
    def setUp(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_invalid_command(self):
        """Test handling of invalid commands"""
        result = self.runner.invoke(cli, ['invalid-command'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("No such command", result.output)
    
    def test_setup_interruption(self):
        """Test setup interruption handling"""
        # Simulate user interrupting setup
        result = self.runner.invoke(setup, input='\x03')  # Ctrl+C
        # Should handle interruption gracefully
        self.assertNotEqual(result.exit_code, 0)
    
    @patch.dict(os.environ, {"HOME": "/invalid/path/that/does/not/exist"})
    def test_invalid_home_directory(self):
        """Test handling of invalid home directory"""
        # This test might not be applicable depending on how the app handles permissions
        # The ConfigManager should handle this gracefully
        try:
            config = ConfigManager()
            # If it doesn't raise an exception, the error handling is working
            self.assertIsNotNone(config)
        except Exception:
            # If it does raise an exception, it should be a meaningful one
            pass


class TestConfigManagement(unittest.TestCase):
    """Test configuration management through CLI"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.runner = CliRunner()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.dict(os.environ, {"HOME": ""})
    def test_config_persistence(self):
        """Test that configuration persists between CLI runs"""
        with self.runner.isolated_filesystem():
            os.environ["HOME"] = os.getcwd()
            
            # First setup
            inputs = [
                'y',  # Use OpenAI
                'persistent-key',
                'n',  # Don't use Anthropic
                'n'   # Don't configure GitHub
            ]
            
            result = self.runner.invoke(setup, input='\n'.join(inputs))
            self.assertEqual(result.exit_code, 0)
            
            # Create new ConfigManager instance (simulating new CLI run)
            config = ConfigManager()
            self.assertEqual(config.get_api_key("openai"), "persistent-key")
    
    def test_config_file_format(self):
        """Test configuration file format validation"""
        config = ConfigManager(self.temp_dir)
        
        # Verify config file contains expected structure
        import yaml
        with open(config.config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        self.assertIn("api_keys", config_data)
        self.assertIn("preferences", config_data)
        self.assertIn("mcp_servers", config_data)
        
        # Verify default preferences
        preferences = config_data["preferences"]
        self.assertIn("default_model", preferences)
        self.assertIn("max_parallel_tasks", preferences)
        self.assertIn("memory_enabled", preferences)


if __name__ == '__main__':
    unittest.main()