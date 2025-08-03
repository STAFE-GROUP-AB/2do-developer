"""
Test cases for sub-task functionality
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from twodo.todo_manager import TodoManager


class TestSubTaskFunctionality(unittest.TestCase):
    """Test sub-task creation and management"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.todo_manager = TodoManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_todo_size_analysis_small(self):
        """Test that small todos are not marked as large"""
        todo_id = self.todo_manager.add_todo(
            "Fix bug",
            "Simple bug fix",
            "code",
            "medium",
            "Quick fix"
        )
        
        todo = self.todo_manager.get_todo_by_id(todo_id)
        self.assertIsNotNone(todo)
        self.assertFalse(self.todo_manager.is_todo_too_large(todo))
    
    def test_todo_size_analysis_large_content(self):
        """Test that todos with large content are marked as large"""
        large_content = "This is a very long content " * 50  # Over 500 chars
        
        todo_id = self.todo_manager.add_todo(
            "Large task",
            "Task with large content",
            "code",
            "medium",
            large_content
        )
        
        todo = self.todo_manager.get_todo_by_id(todo_id)
        self.assertIsNotNone(todo)
        self.assertTrue(self.todo_manager.is_todo_too_large(todo))
    
    def test_todo_size_analysis_complex_keywords(self):
        """Test that todos with complexity keywords are marked as large"""
        todo_id = self.todo_manager.add_todo(
            "Comprehensive system implementation",
            "Implement complete comprehensive system architecture framework",
            "code",
            "high",
            "Design and build entire platform infrastructure"
        )
        
        todo = self.todo_manager.get_todo_by_id(todo_id)
        self.assertIsNotNone(todo)
        self.assertTrue(self.todo_manager.is_todo_too_large(todo))
    
    def test_subtask_creation_simple(self):
        """Test creating sub-tasks without AI"""
        todo_id = self.todo_manager.add_todo(
            "Build web application",
            "Create comprehensive web application",
            "code",
            "high",
            "Complex project requiring multiple components and comprehensive implementation"
        )
        
        # Verify it's marked as large
        todo = self.todo_manager.get_todo_by_id(todo_id)
        self.assertTrue(self.todo_manager.is_todo_too_large(todo))
        
        # Create sub-tasks
        sub_task_ids = self.todo_manager.create_sub_tasks_from_todo(todo_id)
        
        # Verify sub-tasks were created
        self.assertGreater(len(sub_task_ids), 0)
        self.assertLessEqual(len(sub_task_ids), 5)  # Should create 3-5 sub-tasks
        
        # Verify parent-child relationships
        updated_todo = self.todo_manager.get_todo_by_id(todo_id)
        self.assertEqual(len(updated_todo["sub_task_ids"]), len(sub_task_ids))
        
        for sub_id in sub_task_ids:
            sub_task = self.todo_manager.get_todo_by_id(sub_id)
            self.assertIsNotNone(sub_task)
            self.assertEqual(sub_task["parent_id"], todo_id)
    
    def test_subtask_relationship_queries(self):
        """Test querying sub-task relationships"""
        # Create parent todo
        parent_id = self.todo_manager.add_todo(
            "Parent task",
            "Task with sub-tasks",
            "code",
            "high",
            "This is a comprehensive task that needs breaking down into multiple components"
        )
        
        # Create sub-tasks
        sub_task_ids = self.todo_manager.create_sub_tasks_from_todo(parent_id)
        
        # Test get_sub_tasks
        sub_tasks = self.todo_manager.get_sub_tasks(parent_id)
        self.assertEqual(len(sub_tasks), len(sub_task_ids))
        
        # Test get_parent_todo
        if sub_tasks:
            parent = self.todo_manager.get_parent_todo(sub_tasks[0]["id"])
            self.assertIsNotNone(parent)
            self.assertEqual(parent["id"], parent_id)
    
    def test_no_subtasks_for_small_todo(self):
        """Test that small todos don't create sub-tasks"""
        todo_id = self.todo_manager.add_todo(
            "Small task",
            "Simple task",
            "general",
            "low",
            "Easy work"
        )
        
        # Should not create sub-tasks for small todo
        sub_task_ids = self.todo_manager.create_sub_tasks_from_todo(todo_id)
        self.assertEqual(len(sub_task_ids), 0)
    
    def test_todo_structure_integrity(self):
        """Test that new fields don't break existing functionality"""
        # Create a todo and verify all expected fields exist
        todo_id = self.todo_manager.add_todo(
            "Test todo",
            "Test description",
            "general",
            "medium",
            "Test content"
        )
        
        todo = self.todo_manager.get_todo_by_id(todo_id)
        
        # Verify all original fields exist
        expected_fields = [
            "id", "title", "description", "todo_type", "priority", "status",
            "content", "created_at", "updated_at", "assigned_model", "result"
        ]
        for field in expected_fields:
            self.assertIn(field, todo)
        
        # Verify new fields exist and have correct defaults
        self.assertIn("parent_id", todo)
        self.assertIn("sub_task_ids", todo)
        self.assertIsNone(todo["parent_id"])
        self.assertEqual(todo["sub_task_ids"], [])


if __name__ == "__main__":
    unittest.main()