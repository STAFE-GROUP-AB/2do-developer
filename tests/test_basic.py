#!/usr/bin/env python3
"""
Basic tests for AI Redirector functionality
"""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image, ImageDraw

from ai_redirector.config import ConfigManager
from ai_redirector.todo_manager import TodoManager
from ai_redirector.tech_stack import TechStackDetector
from ai_redirector.image_handler import ImageHandler

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
        # Create a todo manager with a temporary directory to avoid conflicts
        original_home = os.environ.get('HOME')
        with tempfile.TemporaryDirectory() as temp_home:
            os.environ['HOME'] = temp_home
            
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
            
            # Restore original HOME
            if original_home:
                os.environ['HOME'] = original_home
            elif 'HOME' in os.environ:
                del os.environ['HOME']
    
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
    
    def test_image_handler(self):
        """Test image handling functionality"""
        handler = ImageHandler()
        
        # Create a test image
        test_image = Image.new('RGB', (100, 50), color=(255, 0, 0))
        draw = ImageDraw.Draw(test_image)
        draw.text((10, 20), "Test", fill=(255, 255, 255))
        
        # Test ASCII preview creation
        ascii_preview = handler.create_ascii_preview(test_image, 20, 5)
        self.assertIsInstance(ascii_preview, str)
        self.assertGreater(len(ascii_preview), 0)
        
        # Test temporary image saving
        temp_path = handler.save_image_temporarily(test_image, "test")
        self.assertTrue(os.path.exists(temp_path))
        self.assertTrue(temp_path.endswith('.png'))
        
        # Test saved image can be loaded
        saved_image = Image.open(temp_path)
        self.assertEqual(saved_image.size, test_image.size)
        
        # Test clipboard detection (will return None since no image in clipboard)
        clipboard_image = handler.check_clipboard_for_image()
        # This should return None in test environment
        self.assertIsNone(clipboard_image)
        
        # Test file path detection
        self.assertTrue(handler._is_image_file_path(temp_path))
        self.assertFalse(handler._is_image_file_path("not_an_image.txt"))
        self.assertFalse(handler._is_image_file_path("/nonexistent/path.jpg"))
        
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()