#!/usr/bin/env python3
"""
Demonstration of Claude Opus 4 Model Prioritization
This script shows how Claude Opus 4 is now the premier model for coding tasks.
"""

import tempfile
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from twodo.config import ConfigManager
from twodo.ai_router import AIRouter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def demo_opus_4_prioritization():
    """Demonstrate Claude Opus 4 prioritization for coding tasks"""
    
    # Set up test environment  
    temp_dir = tempfile.mkdtemp()
    config = ConfigManager(temp_dir)
    config.set_api_key('anthropic', 'demo_key')
    config.set_api_key('openai', 'demo_key')
    config.set_preference('load_only_free_models', False)
    
    # Create router
    router = AIRouter(config)
    
    # Test various types of prompts
    test_cases = [
        ("Coding", [
            "Write a Python function to calculate fibonacci numbers",
            "Debug this React component that won't render",
            "Refactor this Laravel controller for better performance", 
            "Create unit tests for this JavaScript module",
            "Implement a binary search algorithm in Java"
        ]),
        ("Technical Architecture", [
            "Design a microservices architecture for an e-commerce platform",
            "Create a database schema for a social media app",
            "Design patterns for a real-time messaging system"
        ]),
        ("TALL Stack Development", [
            "Build a Laravel Livewire component with TailwindCSS",
            "Create a PHP Blade template with Alpine.js interactions",
            "Develop a Laravel API with Eloquent relationships"
        ]),
        ("General Tasks", [
            "Write a creative story about space exploration",
            "Translate this text from English to French", 
            "Summarize this research paper"
        ])
    ]
    
    console.print(Panel.fit(
        "🏆 Claude Opus 4 Model Prioritization Demo",
        style="bold cyan"
    ))
    
    for category, prompts in test_cases:
        console.print(f"\n📋 [bold yellow]{category} Tasks:[/bold yellow]")
        
        table = Table()
        table.add_column("Prompt", style="cyan", width=50)
        table.add_column("Selected Model", style="green")
        table.add_column("Claude Opus 4?", style="yellow")
        
        for prompt in prompts:
            # Silence the model selection output for demo
            selected_model = router.select_best_model(prompt, todo_context=None)
            is_opus_4 = "claude-opus-4" in selected_model
            status = "✅ Yes" if is_opus_4 else "❌ No"
            
            # Truncate long prompts for display
            display_prompt = prompt[:47] + "..." if len(prompt) > 50 else prompt
            
            table.add_row(display_prompt, selected_model, status)
        
        console.print(table)
    
    # Summary
    console.print(f"\n🎯 [bold green]Summary:[/bold green]")
    console.print("✅ Claude Opus 4 is now the premier model for coding tasks")
    console.print("✅ Maintains flexibility for non-coding tasks")
    console.print("✅ Developers can still choose other models if needed")
    console.print("✅ Automatic intelligent routing based on task type")
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    demo_opus_4_prioritization()