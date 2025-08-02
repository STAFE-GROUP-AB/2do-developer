#!/usr/bin/env python3
"""
Basic tests for AI Redirector functionality
"""

import unittest
import tempfile
import os
from pathlib import Path

from ai_redirector.config import ConfigManager
from ai_redirector.todo_manager import TodoManager
from ai_redirector.tech_stack import TechStackDetector

class TestAIRedirector(unittest.TestCase):
    """Basic tests for core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_config_manager(self):
        """Test configuration management"""
        config = ConfigManager()
        
        # Test setting and getting API keys
        config.set_api_key("test_provider", "test_key")
        self.assertEqual(config.get_api_key("test_provider"), "test_key")
        
        # Test preferences
        config.set_preference("test_pref", "test_value")
        self.assertEqual(config.get_preference("test_pref"), "test_value")
    
    def test_todo_manager(self):
        """Test todo management functionality"""
        todo_manager = TodoManager()
        
        # Test adding a todo
        todo_id = todo_manager.add_todo(
            "Test Todo",
            "Test Description",
            "general",
            "medium"
        )
        
        self.assertIsNotNone(todo_id)
        
        # Test retrieving todos
        todos = todo_manager.get_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["title"], "Test Todo")
        
        # Test updating todo status
        todo_manager.update_todo_status(todo_id, "completed", "Test result")
        updated_todo = todo_manager.get_todo_by_id(todo_id)
        self.assertEqual(updated_todo["status"], "completed")
        self.assertEqual(updated_todo["result"], "Test result")
    
    def test_tech_stack_detection(self):
        """Test technology stack detection"""
        detector = TechStackDetector()
        
        # Create a temporary repository with Python files
        test_repo = Path(self.temp_dir) / "test_repo"
        test_repo.mkdir()
        
        # Create some test files
        (test_repo / "app.py").write_text("print('Hello, World!')")
        (test_repo / "requirements.txt").write_text("flask>=2.0.0")
        (test_repo / "package.json").write_text('{"dependencies": {"react": "^18.0.0"}}')
        
        # Test detection
        tech_stack = detector.analyze_repo(str(test_repo))
        
        self.assertIn("python", tech_stack)
        self.assertIn("javascript", tech_stack)
        self.assertIn("react", tech_stack)
    
    def test_memory_file_creation(self):
        """Test memory file creation for tech stack"""
        detector = TechStackDetector()
        
        # Test memory context retrieval
        python_context = detector.get_memory_context("python")
        
        self.assertIn("description", python_context)
        self.assertIn("best_practices", python_context)
        self.assertIn("common_libraries", python_context)

if __name__ == '__main__':
    unittest.main()