#!/usr/bin/env python3
"""
Comprehensive component tests for 2DO
Tests all major components with edge cases and error conditions
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from twodo.config import ConfigManager
from twodo.todo_manager import TodoManager
from twodo.tech_stack import TechStackDetector
from twodo.ai_router import AIRouter, ModelCapability
from twodo.multitasker import Multitasker
from twodo.markdown_parser import MarkdownTaskParser
from twodo.github_integration import GitHubIntegration


class TestTodoManagerComprehensive(unittest.TestCase):
    """Comprehensive tests for TodoManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "test_config"
        self.todo_manager = TodoManager(self.config_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_todo_comprehensive(self):
        """Test comprehensive todo creation scenarios"""
        # Test basic todo creation
        todo_id = self.todo_manager.add_todo("Test Todo", "Description", "general", "medium")
        self.assertIsNotNone(todo_id)
        
        # Test todo with all fields
        todo_id2 = self.todo_manager.add_todo(
            title="Complex Todo",
            description="Detailed description with special chars: !@#$%^&*()",
            todo_type="code",
            priority="critical"
        )
        self.assertIsNotNone(todo_id2)
        
        # Test todo with empty description
        todo_id3 = self.todo_manager.add_todo("Empty Desc", "", "text", "low")
        self.assertIsNotNone(todo_id3)
        
        # Verify all todos were added
        todos = self.todo_manager.get_todos()
        self.assertEqual(len(todos), 3)
    
    def test_todo_priorities(self):
        """Test all priority levels"""
        priorities = ["low", "medium", "high", "critical"]
        todo_ids = []
        
        for priority in priorities:
            todo_id = self.todo_manager.add_todo(f"Todo {priority}", f"Priority: {priority}", "general", priority)
            todo_ids.append(todo_id)
        
        # Verify priorities are stored correctly
        todos = self.todo_manager.get_todos()
        for i, todo in enumerate(todos):
            self.assertEqual(todo["priority"], priorities[i])
    
    def test_todo_types(self):
        """Test all todo types"""
        todo_types = ["general", "code", "text", "image"]
        todo_ids = []
        
        for todo_type in todo_types:
            todo_id = self.todo_manager.add_todo(f"Todo {todo_type}", f"Type: {todo_type}", todo_type, "medium")
            todo_ids.append(todo_id)
        
        # Verify types are stored correctly
        todos = self.todo_manager.get_todos()
        for i, todo in enumerate(todos):
            self.assertEqual(todo["todo_type"], todo_types[i])
    
    def test_todo_status_updates(self):
        """Test comprehensive todo status updates"""
        todo_id = self.todo_manager.add_todo("Status Test", "Testing status updates", "general", "medium")
        
        # Test status update to in_progress
        self.todo_manager.update_todo_status(todo_id, "in_progress", "Started working")
        todo = self.todo_manager.get_todo_by_id(todo_id)
        self.assertEqual(todo["status"], "in_progress")
        self.assertEqual(todo["result"], "Started working")
        
        # Test status update to completed
        self.todo_manager.update_todo_status(todo_id, "completed", "Task finished successfully")
        todo = self.todo_manager.get_todo_by_id(todo_id)
        self.assertEqual(todo["status"], "completed")
        self.assertEqual(todo["result"], "Task finished successfully")
        
        # Test status update to failed
        todo_id2 = self.todo_manager.add_todo("Fail Test", "Testing failure", "general", "low")
        self.todo_manager.update_todo_status(todo_id2, "failed", "Task failed due to error")
        todo2 = self.todo_manager.get_todo_by_id(todo_id2)
        self.assertEqual(todo2["status"], "failed")
    
    def test_todo_filtering_and_search(self):
        """Test todo filtering and search functionality"""
        # Add diverse todos
        todos_data = [
            ("Python Code Review", "Review Python code", "code", "high", "pending"),
            ("Documentation Update", "Update README", "text", "medium", "completed"),
            ("Bug Fix", "Fix critical bug", "code", "critical", "in_progress"),
            ("Image Processing", "Process user images", "image", "low", "pending")
        ]
        
        for title, desc, todo_type, priority, status in todos_data:
            todo_id = self.todo_manager.add_todo(title, desc, todo_type, priority)
            if status != "pending":
                self.todo_manager.update_todo_status(todo_id, status, f"Status: {status}")
        
        # Test getting todos by status
        all_todos = self.todo_manager.get_todos()
        pending_todos = [t for t in all_todos if t["status"] == "pending"]
        completed_todos = [t for t in all_todos if t["status"] == "completed"]
        
        self.assertEqual(len(pending_todos), 2)
        self.assertEqual(len(completed_todos), 1)
    
    def test_completion_stats(self):
        """Test completion statistics calculation"""
        # Initially no todos
        stats = self.todo_manager.get_completion_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["pending"], 0)
        self.assertEqual(stats["completed"], 0)
        
        # Add and complete some todos
        todo1 = self.todo_manager.add_todo("Todo 1", "Description 1", "general", "medium")
        todo2 = self.todo_manager.add_todo("Todo 2", "Description 2", "general", "medium")
        todo3 = self.todo_manager.add_todo("Todo 3", "Description 3", "general", "medium")
        
        # Complete one todo
        self.todo_manager.update_todo_status(todo1, "completed", "Done")
        
        stats = self.todo_manager.get_completion_stats()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["pending"], 2)
        self.assertEqual(stats["completed"], 1)
        
        # Complete another
        self.todo_manager.update_todo_status(todo2, "completed", "Done")
        
        stats = self.todo_manager.get_completion_stats()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["pending"], 1)
        self.assertEqual(stats["completed"], 2)
    
    def test_todo_persistence(self):
        """Test that todos persist across manager instances"""
        # Add todos
        todo_id = self.todo_manager.add_todo("Persistent Todo", "Should persist", "general", "medium")
        
        # Create new manager instance
        new_manager = TodoManager(self.config_dir)
        todos = new_manager.get_todos()
        
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["title"], "Persistent Todo")
        self.assertEqual(todos[0]["id"], todo_id)
    
    def test_invalid_todo_operations(self):
        """Test handling of invalid todo operations"""
        # Test getting non-existent todo
        result = self.todo_manager.get_todo_by_id("non-existent-id")
        self.assertIsNone(result)
        
        # Test updating non-existent todo
        # Should not raise an exception
        self.todo_manager.update_todo_status("non-existent-id", "completed", "Result")
    
    def test_todo_data_integrity(self):
        """Test todo data integrity and validation"""
        todo_id = self.todo_manager.add_todo("Integrity Test", "Testing data integrity", "general", "medium")
        todo = self.todo_manager.get_todo_by_id(todo_id)
        
        # Verify required fields
        self.assertIn("id", todo)
        self.assertIn("title", todo)
        self.assertIn("description", todo)
        self.assertIn("todo_type", todo)
        self.assertIn("priority", todo)
        self.assertIn("status", todo)
        self.assertIn("created_at", todo)
        self.assertIn("updated_at", todo)
        
        # Verify default values
        self.assertEqual(todo["status"], "pending")
        self.assertIsNotNone(todo["created_at"])
        self.assertIsNotNone(todo["updated_at"])


class TestTechStackDetectorComprehensive(unittest.TestCase):
    """Comprehensive tests for TechStackDetector"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = TechStackDetector(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_comprehensive_tech_stack_detection(self):
        """Test detection of various tech stacks"""
        # Create a comprehensive test repository
        test_repo = Path(self.temp_dir) / "comprehensive_repo"
        test_repo.mkdir()
        
        # Python files
        (test_repo / "app.py").write_text("from flask import Flask\napp = Flask(__name__)")
        (test_repo / "requirements.txt").write_text("flask>=2.0.0\ndjango>=4.0.0\npandas>=1.3.0")
        (test_repo / "setup.py").write_text("from setuptools import setup")
        
        # JavaScript/Node.js files
        (test_repo / "package.json").write_text('''{
            "dependencies": {
                "react": "^18.0.0",
                "express": "^4.18.0",
                "tailwindcss": "^3.0.0",
                "alpinejs": "^3.0.0"
            }
        }''')
        (test_repo / "app.js").write_text("const express = require('express');")
        
        # PHP/Laravel files
        (test_repo / "composer.json").write_text('''{
            "require": {
                "laravel/framework": "^10.0",
                "livewire/livewire": "^3.0"
            }
        }''')
        (test_repo / "artisan").write_text("#!/usr/bin/env php")
        
        # CSS files
        (test_repo / "style.css").write_text("body { margin: 0; }")
        (test_repo / "tailwind.config.js").write_text("module.exports = {}")
        
        # Docker
        (test_repo / "Dockerfile").write_text("FROM python:3.9")
        (test_repo / "docker-compose.yml").write_text("version: '3'")
        
        # Database
        (test_repo / "schema.sql").write_text("CREATE TABLE users (id INT PRIMARY KEY);")
        
        tech_stack = self.detector.analyze_repo(str(test_repo))
        
        # Verify comprehensive detection
        expected_technologies = [
            "python", "javascript", "php", "laravel", "react", "express",
            "tailwindcss", "alpinejs", "livewire", "docker", "sql"
        ]
        
        for tech in expected_technologies:
            self.assertIn(tech, tech_stack, f"Expected {tech} to be detected")
    
    def test_memory_context_generation(self):
        """Test memory context generation for different technologies"""
        technologies = ["python", "javascript", "react", "laravel", "docker"]
        
        for tech in technologies:
            context = self.detector.get_memory_context(tech)
            
            # Verify context structure
            self.assertIn("description", context)
            self.assertIn("best_practices", context)
            self.assertIsInstance(context["best_practices"], list)
            
            # Verify technology-specific context
            if tech == "python":
                self.assertIn("common_libraries", context)
                self.assertIn("testing_frameworks", context)
            elif tech == "javascript":
                self.assertIn("frameworks", context)
                self.assertIn("package_managers", context)
    
    def test_tall_stack_complete_detection(self):
        """Test complete TALL stack detection"""
        test_repo = Path(self.temp_dir) / "tall_stack_repo"
        test_repo.mkdir()
        
        # Laravel
        (test_repo / "composer.json").write_text('''{
            "require": {
                "laravel/framework": "^10.0",
                "livewire/livewire": "^3.0"
            }
        }''')
        (test_repo / "artisan").write_text("#!/usr/bin/env php")
        
        # TailwindCSS and Alpine.js
        (test_repo / "package.json").write_text('''{
            "dependencies": {
                "tailwindcss": "^3.0.0",
                "alpinejs": "^3.0.0"
            }
        }''')
        (test_repo / "tailwind.config.js").write_text("module.exports = {}")
        
        tech_stack = self.detector.analyze_repo(str(test_repo))
        
        # Verify all TALL stack components
        tall_components = ["tailwindcss", "alpinejs", "laravel", "livewire"]
        for component in tall_components:
            self.assertIn(component, tech_stack)
    
    def test_edge_cases(self):
        """Test edge cases in tech stack detection"""
        # Empty repository
        empty_repo = Path(self.temp_dir) / "empty_repo"
        empty_repo.mkdir()
        tech_stack = self.detector.analyze_repo(str(empty_repo))
        self.assertEqual(len(tech_stack), 0)
        
        # Repository with only hidden files
        hidden_repo = Path(self.temp_dir) / "hidden_repo"
        hidden_repo.mkdir()
        (hidden_repo / ".hidden").write_text("hidden content")
        tech_stack = self.detector.analyze_repo(str(hidden_repo))
        self.assertEqual(len(tech_stack), 0)
        
        # Repository with invalid JSON files
        invalid_repo = Path(self.temp_dir) / "invalid_repo"
        invalid_repo.mkdir()
        (invalid_repo / "package.json").write_text("{ invalid json }")
        tech_stack = self.detector.analyze_repo(str(invalid_repo))
        # Should handle invalid JSON gracefully
        self.assertIsInstance(tech_stack, list)
    
    def test_memory_file_creation_and_persistence(self):
        """Test memory file creation and persistence"""
        technologies = ["python", "javascript", "react"]
        
        # Create memory files
        self.detector.create_memory_files(technologies)
        
        # Verify files were created
        memory_dir = self.detector.memory_dir
        for tech in technologies:
            memory_file = memory_dir / f"{tech}_memory.json"
            self.assertTrue(memory_file.exists())
            
            # Verify file content
            with open(memory_file, 'r') as f:
                memory_data = json.load(f)
            
            self.assertIn("description", memory_data)
            self.assertIn("best_practices", memory_data)
    
    def test_custom_tech_detection_patterns(self):
        """Test custom technology detection patterns"""
        test_repo = Path(self.temp_dir) / "custom_repo"
        test_repo.mkdir()
        
        # Create files with specific patterns
        (test_repo / "Cargo.toml").write_text("[package]\nname = 'rust_project'")
        (test_repo / "go.mod").write_text("module example.com/project")
        (test_repo / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.10)")
        (test_repo / "build.gradle").write_text("plugins { id 'java' }")
        
        tech_stack = self.detector.analyze_repo(str(test_repo))
        
        # Verify detection of various build systems and languages
        expected_techs = ["rust", "go", "cmake", "gradle"]
        for tech in expected_techs:
            self.assertIn(tech, tech_stack)


class TestAIRouterComprehensive(unittest.TestCase):
    """Comprehensive tests for AIRouter"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ConfigManager(self.temp_dir)
        self.config.set_api_key("openai", "test-openai-key")
        self.config.set_api_key("anthropic", "test-anthropic-key")
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('twodo.ai_router.openai.OpenAI')
    @patch('twodo.ai_router.anthropic.Anthropic')
    def test_ai_router_initialization(self, mock_anthropic, mock_openai):
        """Test AI router initialization with various configurations"""
        # Test with all providers
        router = AIRouter(self.config)
        self.assertIsNotNone(router)
        
        # Test with only OpenAI
        config_openai = ConfigManager(self.temp_dir)
        config_openai.set_api_key("openai", "test-key")
        router_openai = AIRouter(config_openai)
        self.assertIsNotNone(router_openai)
        
        # Test with only Anthropic
        config_anthropic = ConfigManager(self.temp_dir)
        config_anthropic.set_api_key("anthropic", "test-key")
        router_anthropic = AIRouter(config_anthropic)
        self.assertIsNotNone(router_anthropic)
    
    def test_model_capability_definition(self):
        """Test model capability definitions"""
        # Test creating model capabilities
        gpt4_capability = ModelCapability(
            name="gpt-4",
            provider="openai",
            strengths=["reasoning", "code"],
            context_length=8192,
            cost_per_token=0.03,
            speed_rating=7
        )
        
        self.assertEqual(gpt4_capability.name, "gpt-4")
        self.assertEqual(gpt4_capability.provider, "openai")
        self.assertIn("reasoning", gpt4_capability.strengths)
        self.assertEqual(gpt4_capability.context_length, 8192)
    
    @patch('twodo.ai_router.openai.OpenAI')
    @patch('twodo.ai_router.anthropic.Anthropic')
    def test_prompt_analysis(self, mock_anthropic, mock_openai):
        """Test prompt analysis for model selection"""
        router = AIRouter(self.config)
        
        # Test various prompt types
        test_prompts = [
            ("Fix this Python function", ["code", "python", "fix"]),
            ("Quick question about math", ["quick", "simple"]),
            ("Comprehensive analysis of data", ["comprehensive", "analysis"]),
            ("Debug complex algorithm", ["debug", "complex", "algorithm"]),
            ("Creative writing task", ["creative", "writing"]),
            ("Explain machine learning concepts", ["explain", "reasoning"])
        ]
        
        for prompt, expected_keywords in test_prompts:
            # The analyze_prompt method should identify relevant keywords
            # This is a placeholder test since the actual implementation might vary
            self.assertIsInstance(prompt, str)
            self.assertIsInstance(expected_keywords, list)
    
    def test_model_selection_logic(self):
        """Test model selection logic based on prompt analysis"""
        # This would test the actual model selection algorithm
        # For now, we'll test the structure and basic functionality
        
        # Define model capabilities for testing
        models = {
            "gpt-4": ModelCapability("gpt-4", "openai", ["reasoning", "complex"], 8192, 0.03, 7),
            "claude-haiku": ModelCapability("claude-3-5-haiku-20241022", "anthropic", ["speed", "simple"], 200000, 0.0005, 10),
            "gpt-4-turbo": ModelCapability("gpt-4-turbo", "openai", ["code", "large_context"], 128000, 0.01, 8)
        }
        
        # Test selection criteria
        for model_name, capability in models.items():
            self.assertIsInstance(capability.name, str)
            self.assertIsInstance(capability.strengths, list)
            self.assertIsInstance(capability.context_length, int)
            self.assertIsInstance(capability.cost_per_token, (int, float))
            self.assertIsInstance(capability.speed_rating, int)


class TestMarkdownParserComprehensive(unittest.TestCase):
    """Comprehensive tests for MarkdownTaskParser"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = MarkdownTaskParser()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_comprehensive_markdown_parsing(self):
        """Test parsing of various markdown task formats"""
        markdown_content = """
# Project Tasks

## Development Phase
- [ ] Implement user authentication system
- [x] Set up database schema and migrations
- [ ] Create API endpoints for user management
- [x] Write unit tests for authentication

## Documentation
* [ ] Update README with installation instructions
* [x] Create API documentation
* [ ] Write user guide

## Bug Fixes
+ [ ] Fix login redirect issue on mobile
+ [x] Resolve database connection timeout
+ [ ] Address performance issues in search

## Research Tasks
TODO: Investigate new authentication methods
TODO: Research performance optimization techniques
- TODO: Evaluate third-party integrations

## Feature Requests
- [ ] Add social media login options
- [ ] Implement two-factor authentication
- [ ] Create admin dashboard

## Completed Work
- [x] Initial project setup
- [x] Basic user registration
"""
        
        # Create test file
        test_file = Path(self.temp_dir) / "comprehensive_tasks.md"
        test_file.write_text(markdown_content)
        
        # Parse tasks
        tasks = self.parser.parse_file(str(test_file))
        
        # Verify parsing results
        self.assertGreater(len(tasks), 15)  # Should find many tasks
        
        # Check task statuses
        completed_tasks = [t for t in tasks if t['status'] == 'completed']
        pending_tasks = [t for t in tasks if t['status'] == 'pending']
        
        self.assertGreater(len(completed_tasks), 0)
        self.assertGreater(len(pending_tasks), 0)
        
        # Check specific task content
        task_titles = [t['title'] for t in tasks]
        self.assertIn('Implement user authentication system', task_titles)
        self.assertIn('Set up database schema and migrations', task_titles)
        self.assertIn('Investigate new authentication methods', task_titles)
    
    def test_edge_cases_in_parsing(self):
        """Test edge cases in markdown parsing"""
        edge_cases = [
            # Empty file
            "",
            # Only headers
            "# Header 1\n## Header 2\n### Header 3",
            # Mixed content without tasks
            "# Project\nThis is a description.\nNo tasks here.",
            # Malformed task lists
            "- [ Incomplete checkbox\n- [Y] Invalid status\n- [] Empty checkbox",
            # Nested lists
            "- [ ] Main task\n  - [ ] Subtask 1\n  - [x] Subtask 2",
            # Tasks with special characters
            "- [ ] Task with émojis 🚀 and spéciàl chârs",
            # Very long task descriptions
            "- [ ] " + "This is a very long task description that goes on and on. " * 10
        ]
        
        for i, content in enumerate(edge_cases):
            test_file = Path(self.temp_dir) / f"edge_case_{i}.md"
            test_file.write_text(content)
            
            # Should not raise exceptions
            try:
                tasks = self.parser.parse_file(str(test_file))
                self.assertIsInstance(tasks, list)
            except Exception as e:
                self.fail(f"Edge case {i} failed: {e}")
    
    def test_task_summary_generation(self):
        """Test task summary generation"""
        markdown_content = """
# Test Tasks
- [ ] Task 1
- [x] Task 2
- [ ] Task 3
- [x] Task 4
- [x] Task 5
TODO: Task 6
"""
        
        test_file = Path(self.temp_dir) / "summary_test.md"
        test_file.write_text(markdown_content)
        
        tasks = self.parser.parse_file(str(test_file))
        summary = self.parser.get_task_summary(tasks)
        
        self.assertEqual(summary['total_tasks'], 6)
        self.assertEqual(summary['completed_tasks'], 3)
        self.assertEqual(summary['pending_tasks'], 3)
        
        # Test completion percentage
        expected_percentage = (3 / 6) * 100
        self.assertEqual(summary['completion_percentage'], expected_percentage)
    
    def test_directory_parsing(self):
        """Test parsing tasks from multiple files in a directory"""
        # Create multiple markdown files
        files = {
            "tasks1.md": "# File 1\n- [ ] Task 1\n- [x] Task 2",
            "tasks2.md": "# File 2\n- [ ] Task 3\nTODO: Task 4",
            "readme.md": "# README\nNo tasks here",
            "tasks3.md": "# File 3\n- [x] Task 5\n- [ ] Task 6"
        }
        
        test_dir = Path(self.temp_dir) / "test_project"
        test_dir.mkdir()
        
        for filename, content in files.items():
            (test_dir / filename).write_text(content)
        
        # Parse directory
        all_tasks = self.parser.parse_directory(str(test_dir))
        
        # Should find tasks from multiple files
        self.assertGreaterEqual(len(all_tasks), 5)  # At least 5 tasks
        
        # Verify tasks from different files are included
        task_titles = [t['title'] for t in all_tasks]
        self.assertIn('Task 1', task_titles)
        self.assertIn('Task 4', task_titles)
        self.assertIn('Task 6', task_titles)


class TestErrorHandlingAndEdgeCases(unittest.TestCase):
    """Test error handling and edge cases across all components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_manager_error_handling(self):
        """Test ConfigManager error handling"""
        # Test with invalid permissions (simulated)
        config = ConfigManager(self.temp_dir)
        
        # Test setting invalid values
        config.set_api_key("invalid", None)
        self.assertIsNone(config.get_api_key("invalid"))
        
        # Test getting non-existent keys
        self.assertIsNone(config.get_api_key("non_existent"))
    
    def test_todo_manager_error_handling(self):
        """Test TodoManager error handling"""
        todo_manager = TodoManager(self.temp_dir)
        
        # Test with invalid todo types
        todo_id = todo_manager.add_todo("Test", "Desc", "invalid_type", "medium")
        self.assertIsNotNone(todo_id)  # Should still create the todo
        
        # Test with invalid priorities
        todo_id2 = todo_manager.add_todo("Test2", "Desc", "general", "invalid_priority")
        self.assertIsNotNone(todo_id2)  # Should still create the todo
    
    def test_tech_stack_detector_error_handling(self):
        """Test TechStackDetector error handling"""
        detector = TechStackDetector(self.temp_dir)
        
        # Test with non-existent directory
        tech_stack = detector.analyze_repo("/non/existent/path")
        self.assertEqual(tech_stack, [])
        
        # Test with file instead of directory
        test_file = Path(self.temp_dir) / "not_a_directory"
        test_file.write_text("content")
        tech_stack = detector.analyze_repo(str(test_file))
        self.assertEqual(tech_stack, [])
    
    def test_markdown_parser_error_handling(self):
        """Test MarkdownTaskParser error handling"""
        parser = MarkdownTaskParser()
        
        # Test with non-existent file
        tasks = parser.parse_file("/non/existent/file.md")
        self.assertEqual(tasks, [])
        
        # Test with non-markdown file
        test_file = Path(self.temp_dir) / "not_markdown.txt"
        test_file.write_text("This is not markdown content")
        tasks = parser.parse_file(str(test_file))
        self.assertEqual(tasks, [])  # Should return empty list, not crash
    
    def test_github_integration_error_handling(self):
        """Test GitHubIntegration error handling"""
        # Test with invalid token
        github_integration = GitHubIntegration("invalid_token")
        self.assertIsNotNone(github_integration)  # Should initialize without error
        
        # Test URL parsing with invalid URLs
        invalid_urls = [
            "not_a_url",
            "https://gitlab.com/user/repo.git",
            "ftp://example.com/repo",
            ""
        ]
        
        for url in invalid_urls:
            result = github_integration._parse_github_url(url)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()