#!/usr/bin/env python3
"""
Test enhanced progress display functionality
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twodo.multitasker import Multitasker
from twodo.ai_router import AIRouter

class TestEnhancedProgress(unittest.TestCase):
    """Test enhanced progress display features"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock AI router
        self.mock_ai_router = MagicMock()
        self.mock_ai_router.route_and_process.return_value = "Mock AI response"
        
        # Create multitasker with mock
        self.multitasker = Multitasker(self.mock_ai_router)
        
        # Sample test todos
        self.test_todos = [
            {
                "id": 1,
                "title": "Test todo 1",
                "description": "First test todo",
                "todo_type": "code",
                "priority": "high",
                "status": "pending",
                "content": "Test content",
                "parent_id": None,
                "sub_task_ids": []
            },
            {
                "id": 2,
                "title": "Test todo 2 with a very long title that should be truncated",
                "description": "Second test todo",
                "todo_type": "text",
                "priority": "medium",
                "status": "pending",
                "content": "More test content",
                "parent_id": None,
                "sub_task_ids": []
            }
        ]
    
    def test_todo_context_passed_to_ai_router(self):
        """Test that todo context is properly passed to AI router"""
        async def run_test():
            # Process a single todo
            result = await self.multitasker.process_todo_async(self.test_todos[0])
            
            # Verify the AI router was called with todo context
            self.mock_ai_router.route_and_process.assert_called_once()
            call_args = self.mock_ai_router.route_and_process.call_args
            
            # Check that todo_context was passed
            self.assertIn('todo_context', call_args.kwargs)
            self.assertEqual(call_args.kwargs['todo_context'], 'Test todo 1')
            
            # Check that result is properly formatted
            self.assertEqual(result['status'], 'completed')
            self.assertEqual(result['result'], 'Mock AI response')
        
        # Run the async test
        asyncio.run(run_test())
    
    def test_long_title_truncation(self):
        """Test that long todo titles are properly truncated"""
        async def run_test():
            # Process todo with long title
            result = await self.multitasker.process_todo_async(self.test_todos[1])
            
            # Verify the context was truncated
            call_args = self.mock_ai_router.route_and_process.call_args
            context = call_args.kwargs['todo_context']
            
            # Should be truncated to 50 chars + "..."
            self.assertTrue(len(context) <= 53)  # 50 + "..."
            self.assertTrue(context.endswith("..."))
        
        asyncio.run(run_test())
    
    @patch('twodo.multitasker.console')
    def test_progress_messages_displayed(self, mock_console):
        """Test that progress messages are properly displayed"""
        async def run_test():
            # Process a todo
            await self.multitasker.process_todo_async(self.test_todos[0])
            
            # Check that progress messages were printed
            print_calls = [str(call) for call in mock_console.print.call_args_list]
            
            # Should see starting work message
            starting_calls = [call for call in print_calls if "Starting work on" in call]
            self.assertTrue(len(starting_calls) > 0, "Starting work message should be displayed")
            
            # Should see analyzing requirements message
            analyzing_calls = [call for call in print_calls if "Analyzing task requirements" in call]
            self.assertTrue(len(analyzing_calls) > 0, "Analyzing requirements message should be displayed")
            
            # Should see completion message
            completed_calls = [call for call in print_calls if "Completed" in call]
            self.assertTrue(len(completed_calls) > 0, "Completion message should be displayed")
        
        asyncio.run(run_test())
    
    @patch('twodo.multitasker.console')
    def test_parallel_processing_overview(self, mock_console):
        """Test that parallel processing shows todo overview"""
        async def run_test():
            # Process multiple todos
            await self.multitasker._process_todos_parallel(self.test_todos)
            
            # Check that overview was printed
            print_calls = [str(call) for call in mock_console.print.call_args_list]
            
            # Should see overview message
            overview_calls = [call for call in print_calls if "About to process" in call]
            self.assertTrue(len(overview_calls) > 0, "Overview message should be displayed")
            
            # Should see todo list
            todo_list_calls = [call for call in print_calls if "Test todo 1" in call]
            self.assertTrue(len(todo_list_calls) > 0, "Todo list should be displayed")
        
        asyncio.run(run_test())
    
    def test_error_handling_with_context(self):
        """Test error handling includes todo context"""
        # Set up AI router to raise an exception
        self.mock_ai_router.route_and_process.side_effect = Exception("Test error")
        
        async def run_test():
            # Process a todo that will fail
            result = await self.multitasker.process_todo_async(self.test_todos[0])
            
            # Check that error was handled properly
            self.assertEqual(result['status'], 'failed')
            self.assertIn('Error: Test error', result['result'])
        
        asyncio.run(run_test())

class TestAIRouterEnhancements(unittest.TestCase):
    """Test AI router enhancements for todo context"""
    
    def test_select_best_model_with_context(self):
        """Test that select_best_model accepts todo context parameter"""
        # Create a mock config manager
        mock_config = MagicMock()
        mock_config.get_api_key.return_value = None  # No API keys for test
        
        # Create AI router
        ai_router = AIRouter(mock_config)
        
        # Override models to avoid API requirements
        ai_router.models = {
            "test-model": MagicMock(
                strengths=["reasoning"],
                speed_rating=8,
                cost_per_token=0.001,
                context_length=32000
            )
        }
        
        # Mock console to capture output
        with patch('twodo.ai_router.console') as mock_console:
            try:
                # This should work without error even with context
                model = ai_router.select_best_model("test prompt", "test todo")
                self.assertEqual(model, "test-model")
                
                # Check that context was included in output
                print_calls = [str(call) for call in mock_console.print.call_args_list]
                context_calls = [call for call in print_calls if "test todo" in call]
                self.assertTrue(len(context_calls) > 0, "Todo context should appear in model selection")
                
            except ValueError:
                # Expected when no models are configured, but method signature should work
                pass

if __name__ == '__main__':
    unittest.main()