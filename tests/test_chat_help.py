#!/usr/bin/env python3
"""
Test chat help functionality for issue #31
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from twodo.cli import show_chat_help, handle_chat


class TestChatHelpFunctionality(unittest.TestCase):
    """Test the simplified chat interface and help command"""
    
    def setUp(self):
        """Set up test environment"""
        self.console_output = StringIO()
    
    @patch('twodo.cli.console')
    def test_show_chat_help_displays_correct_content(self, mock_console):
        """Test that show_chat_help displays the expected help content"""
        show_chat_help()
        
        # Verify that console.print was called multiple times
        self.assertTrue(mock_console.print.called)
        
        # Get all the print calls - handle both args and keyword args
        print_calls = []
        for call in mock_console.print.call_args_list:
            if call.args:
                print_calls.append(str(call.args[0]))
            elif call.kwargs:
                # If no args, might be in kwargs or just empty print()
                print_calls.append("")
        
        print_content = ' '.join(print_calls)
        
        # Check for key elements of the help
        self.assertIn("Chat Help - Available Commands", print_content)
        self.assertIn("?", print_content)
        self.assertIn("exit", print_content)
        self.assertIn("image", print_content)
        self.assertIn("AI Features", print_content)
        self.assertIn("Tips", print_content)
    
    @patch('twodo.cli.console')
    @patch('twodo.cli.Prompt')
    @patch('twodo.cli.show_chat_help')
    def test_chat_help_command_triggers_help(self, mock_show_help, mock_prompt, mock_console):
        """Test that typing '?' in chat triggers the help function"""
        # Mock the image handler
        mock_image_handler = MagicMock()
        mock_image_handler.cleanup_old_temp_files = MagicMock()
        
        # Mock the AI router  
        mock_ai_router = MagicMock()
        
        # Simulate user typing '?' then 'exit'
        mock_prompt.ask.side_effect = ['?', 'exit']
        
        # Call the handle_chat function
        handle_chat(mock_ai_router, mock_image_handler)
        
        # Verify that show_chat_help was called once
        mock_show_help.assert_called_once()
        
        # Verify that Prompt.ask was called twice (once for '?', once for 'exit')
        self.assertEqual(mock_prompt.ask.call_count, 2)
    
    @patch('twodo.cli.console')
    @patch('twodo.cli.Prompt')
    def test_chat_startup_shows_minimal_message(self, mock_prompt, mock_console):
        """Test that chat startup shows only minimal message"""
        # Mock the image handler
        mock_image_handler = MagicMock()
        mock_image_handler.cleanup_old_temp_files = MagicMock()
        
        # Mock the AI router
        mock_ai_router = MagicMock()
        
        # Simulate user typing 'exit' immediately
        mock_prompt.ask.return_value = 'exit'
        
        # Call the handle_chat function
        handle_chat(mock_ai_router, mock_image_handler)
        
        # Get all console print calls during startup
        startup_calls = [call.args[0] for call in mock_console.print.call_args_list[:2]]
        startup_content = ' '.join(startup_calls)
        
        # Verify minimal startup message
        self.assertIn("💬 Chat", startup_content)
        self.assertIn("Type '?' for help", startup_content)
        
        # Verify old verbose messages are NOT shown at startup
        self.assertNotIn("2DO will choose the best model", startup_content)
        self.assertNotIn("paste images from clipboard", startup_content)
        self.assertNotIn("type 'image' to load", startup_content)
    
    @patch('twodo.cli.console')
    @patch('twodo.cli.Prompt')  
    def test_question_mark_with_whitespace_triggers_help(self, mock_prompt, mock_console):
        """Test that '?' with whitespace still triggers help"""
        # Mock the image handler
        mock_image_handler = MagicMock()
        mock_image_handler.cleanup_old_temp_files = MagicMock()
        
        # Mock the AI router
        mock_ai_router = MagicMock()
        
        # Test various whitespace scenarios
        test_inputs = [' ? ', '?', '  ?  ', 'exit']
        mock_prompt.ask.side_effect = test_inputs
        
        with patch('twodo.cli.show_chat_help') as mock_show_help:
            handle_chat(mock_ai_router, mock_image_handler)
            
            # Should call help for first 3 inputs (all variations of '?')
            self.assertEqual(mock_show_help.call_count, 3)


if __name__ == '__main__':
    unittest.main()