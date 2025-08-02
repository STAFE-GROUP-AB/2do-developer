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
        # Use temporary directory to avoid test interference
        temp_config_dir = Path(self.temp_dir) / "test_config"
        todo_manager = TodoManager(temp_config_dir)
        
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
        # Use temporary directory for testing
        temp_config_dir = Path(self.temp_dir) / "test_memory"
        detector = TechStackDetector(temp_config_dir)
        
        # Test memory context retrieval
        python_context = detector.get_memory_context("python")
        
        self.assertIn("description", python_context)
        self.assertIn("best_practices", python_context)
        self.assertIn("common_libraries", python_context)
    
    def test_tall_stack_detection(self):
        """Test TALL stack technology detection"""
        detector = TechStackDetector()
        
        # Create a temporary repository with TALL stack files
        test_repo = Path(self.temp_dir) / "tall_repo"
        test_repo.mkdir()
        
        # Create Laravel composer.json
        (test_repo / "composer.json").write_text('''{
            "require": {
                "laravel/framework": "^10.0",
                "livewire/livewire": "^3.0"
            }
        }''')
        
        # Create package.json with TailwindCSS and Alpine.js
        (test_repo / "package.json").write_text('''{
            "dependencies": {
                "tailwindcss": "^3.0.0",
                "alpinejs": "^3.0.0"
            }
        }''')
        
        # Create artisan file
        (test_repo / "artisan").write_text("#!/usr/bin/env php")
        
        # Test detection
        tech_stack = detector.analyze_repo(str(test_repo))
        
        self.assertIn("laravel", tech_stack)
        self.assertIn("livewire", tech_stack)
        self.assertIn("tailwindcss", tech_stack)
        self.assertIn("alpinejs", tech_stack)
    
    def test_local_2do_config(self):
        """Test local 2DO folder configuration for git repositories"""
        # Create a mock git repository
        git_repo = Path(self.temp_dir) / "git_test"
        git_repo.mkdir()
        (git_repo / ".git").mkdir()
        
        # Test ConfigManager with git repo
        config = ConfigManager(str(git_repo))
        self.assertTrue(config.is_local_project)
        self.assertTrue(str(config.config_dir).endswith("2DO"))
        
        # Test ConfigManager without git repo
        non_git_repo = Path(self.temp_dir) / "non_git"
        non_git_repo.mkdir()
        
        config2 = ConfigManager(str(non_git_repo))
        self.assertFalse(config2.is_local_project)
        self.assertFalse(str(config2.config_dir).endswith("2DO"))
    
    def test_markdown_task_parsing(self):
        """Test markdown task parsing functionality"""
        from ai_redirector.markdown_parser import MarkdownTaskParser
        
        # Create a test markdown file
        test_md = Path(self.temp_dir) / "test_tasks.md"
        test_md.write_text("""# Project Tasks

## Development
- [ ] Implement user authentication
- [x] Set up database schema
- TODO: Write unit tests

## Documentation
* [ ] Update README
* [x] Create API documentation

### Bugs
+ [ ] Fix login redirect issue
""")
        
        parser = MarkdownTaskParser()
        tasks = parser.parse_file(str(test_md))
        
        # Should find 6 tasks total
        self.assertEqual(len(tasks), 6)
        
        # Check task content
        task_titles = [task['title'] for task in tasks]
        self.assertIn('Implement user authentication', task_titles)
        self.assertIn('Write unit tests', task_titles)
        self.assertIn('Update README', task_titles)
        
        # Check status
        completed_tasks = [task for task in tasks if task['status'] == 'completed']
        pending_tasks = [task for task in tasks if task['status'] == 'pending']
        
        self.assertEqual(len(completed_tasks), 2)  # Set up database schema, Create API documentation
        self.assertEqual(len(pending_tasks), 4)   # Remaining tasks
        
        # Test summary
        summary = parser.get_task_summary(tasks)
        self.assertEqual(summary['total_tasks'], 6)
        self.assertEqual(summary['pending_tasks'], 4)
        self.assertEqual(summary['completed_tasks'], 2)

if __name__ == '__main__':
    unittest.main()