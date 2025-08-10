#!/usr/bin/env python3
"""
Demo script showing the new human colleague behavior in 2DO
This demonstrates the key improvements requested in the issue.
"""

import tempfile
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from twodo.todo_manager import TodoManager
from twodo.intent_router import IntentRouter
from twodo.ai_router import AIRouter
from twodo.config import ConfigManager
from rich.console import Console
from rich.panel import Panel

console = Console()

def demo_human_colleague_behavior():
    """Demonstrate the new human colleague behavior"""
    
    console.print(Panel.fit("🤖 2DO Human Colleague Behavior Demo", style="bold cyan"))
    console.print("This demo shows how 2DO now acts more like a friendly developer colleague!\n")
    
    # Demo 1: Friendly Intent Recognition
    console.print(Panel("📋 Demo 1: Human-like Communication", style="bold green"))
    
    intent_router = IntentRouter()
    
    demo_conversations = [
        {
            "user": "I need to implement user authentication",
            "description": "Task creation with friendly confirmation"
        },
        {
            "user": "Show me what I'm working on",
            "description": "Task listing with encouraging tone"
        },
        {
            "user": "Let's work on multiple tasks at once",
            "description": "Multitasking with enthusiasm"
        },
        {
            "user": "Break down this complex task",
            "description": "Sub-task creation with helpfulness"
        }
    ]
    
    for convo in demo_conversations:
        intent_match = intent_router.analyze_intent(convo["user"])
        confirmation = intent_router.get_friendly_confirmation(intent_match.intent, intent_match.extracted_params)
        
        console.print(f"[bold blue]Developer:[/bold blue] \"{convo['user']}\"")
        console.print(f"[bold green]2DO AI:[/bold green] {confirmation}")
        console.print(f"[dim]({convo['description']})[/dim]\n")
    
    # Demo 2: Task Confirmation Workflow
    console.print(Panel("🤝 Demo 2: Task Confirmation Workflow (Default: No)", style="bold green"))
    
    console.print("[bold blue]Developer:[/bold blue] \"I want to fix the login bug\"")
    console.print("[bold green]2DO AI:[/bold green] 🎯 Got it! Looks like you want to track a new task.")
    console.print("[bold green]2DO AI:[/bold green] 🤔 I understand what you want to work on!")
    console.print("[bold green]2DO AI:[/bold green] 📝 This looks like a new task to track.")
    console.print("[bold green]2DO AI:[/bold green] 💭 Would you like me to work on this task right now, or should I just add it to your todo list for later?")
    console.print("[bold yellow]Prompt:[/bold yellow] [bold cyan]Work on this now?[/bold cyan] (y/[bold]N[/bold]) [dim]← Default is No as requested[/dim]")
    console.print("[bold green]2DO AI:[/bold green] 👍 Got it! I'll add this to your list and you can tackle it later when you're ready.\n")
    
    # Demo 3: Automatic Sub-task Creation
    console.print(Panel("🧩 Demo 3: Smart Sub-task Creation", style="bold green"))
    
    with tempfile.TemporaryDirectory() as temp_dir:
        todo_manager = TodoManager(temp_dir)
        
        # Create a complex task
        complex_task = {
            'id': 'demo-task',
            'title': "Build a comprehensive user authentication system with OAuth integration, role-based permissions, and comprehensive testing",
            'description': "This system needs login, registration, password reset, OAuth with Google/GitHub, 2FA, RBAC, and full test coverage",
            'todo_type': 'code',
            'priority': 'high',
            'content': "Additional requirements: secure, scalable, user-friendly with documentation and deployment"
        }
        
        is_large = todo_manager.is_todo_too_large(complex_task)
        
        console.print("[bold blue]Developer:[/bold blue] Creates a complex task...")
        console.print(f"[bold yellow]Task:[/bold yellow] \"{complex_task['title'][:60]}...\"")
        console.print(f"[bold green]2DO AI:[/bold green] 🔍 You know what? This task looks pretty substantial!")
        console.print(f"[bold green]2DO AI:[/bold green] 🎯 Want me to break it down into smaller, more manageable pieces?")
        console.print(f"[dim]AI Detection: Large/Complex = {is_large}[/dim]")
        
        if is_large:
            console.print("\n[bold green]2DO AI:[/bold green] 🎉 Great! I've created 4 smaller tasks to help you tackle this step by step!")
            console.print("[bold green]2DO AI:[/bold green] 💡 Just ask to 'show me my tasks' to see the breakdown.")
            
            # Show example sub-tasks
            example_subtasks = [
                "1. Plan and design the architecture - Start by sketching out the overall approach",
                "2. Implement core functionality - Build the main features step by step", 
                "3. Add comprehensive testing - Ensure everything works reliably",
                "4. Document and polish - Add docs and final touches"
            ]
            
            console.print("\n[bold cyan]Generated Sub-tasks:[/bold cyan]")
            for subtask in example_subtasks:
                console.print(f"  📌 {subtask}")
        
        console.print()
    
    # Demo 4: Developer-Focused Personality
    console.print(Panel("🤖 Demo 4: Developer-Focused AI Personality", style="bold green"))
    
    developer_context = intent_router.get_developer_context_prompt()
    
    console.print("[bold green]AI Personality Traits:[/bold green]")
    console.print("  ✨ Passionate developer who loves helping other developers")
    console.print("  😊 Polite, encouraging, with touches of humor")
    console.print("  🧠 Understands developer workflows and coding challenges") 
    console.print("  💪 Always supportive and positive - never mean or unhelpful")
    console.print("  🚀 Makes developers feel like they have the best coding buddy")
    
    console.print("\n[bold green]AI Mission:[/bold green]")
    console.print("  📋 Help manage todos and tasks efficiently")
    console.print("  📊 Keep developers organized with their work")
    console.print("  🐙 Navigate GitHub issues and project management")
    console.print("  ⚡ Help code faster and smarter")
    console.print("  🎯 Provide motivation and support in the development journey")
    
    console.print()
    
    # Demo 5: MCP Memory Enhancement
    console.print(Panel("🧠 Demo 5: Enhanced Project Memory", style="bold green"))
    
    console.print("[bold green]2DO AI:[/bold green] 😊 Hey! I'm going to analyze your project and suggest some MCP servers that'll make your development workflow much smoother.")
    console.print("[bold green]2DO AI:[/bold green] 💡 Think of these as power-ups for our AI collaboration!")
    console.print("[bold green]2DO AI:[/bold green] 🎯 Based on your project, I found 5 servers that could really help!")
    console.print("[bold green]2DO AI:[/bold green] 🤝 Now, let's pick which ones you'd like me to set up.")
    console.print("[bold green]2DO AI:[/bold green] 💭 I recommend starting with the essential ones - they're like having a super-powered assistant!")
    console.print("[bold green]2DO AI:[/bold green] 🎉 Perfect! Your development environment is now supercharged!")
    console.print("[bold green]2DO AI:[/bold green] 🧠 I'll remember your preferences and project context across sessions now!")
    
    console.print()

def demo_before_and_after():
    """Show before and after comparison"""
    
    console.print(Panel.fit("⚖️ Before vs After Comparison", style="bold magenta"))
    
    console.print("[bold red]❌ BEFORE (Cold & Robotic):[/bold red]")
    console.print("  🤖 \"Todo title:\"")
    console.print("  🤖 \"Todo added successfully!\"") 
    console.print("  🤖 \"Run multitask? (y/n)\"")
    console.print("  🤖 \"Analysis complete.\"")
    
    console.print("\n[bold green]✅ AFTER (Warm & Colleague-like):[/bold green]")
    console.print("  😊 \"📝 What should I call this task?\"")
    console.print("  🎉 \"Perfect! I've added this to your task list.\"")
    console.print("  🤔 \"Want me to work on this right now, or add it to your list for later? (y/[bold]N[/bold])\"")
    console.print("  🚀 \"Awesome! Your development environment is now supercharged!\"")
    
    console.print()

def main():
    """Run the complete demo"""
    console.print("🎭 2DO Human Colleague Behavior Demo", style="bold cyan")
    console.print("=" * 60)
    console.print("This demonstrates all the improvements requested in the GitHub issue.\n")
    
    demo_human_colleague_behavior()
    demo_before_and_after()
    
    console.print(Panel.fit("🎯 Key Improvements Summary", style="bold blue"))
    console.print("✅ [bold]Task Confirmation:[/bold] Default 'No' with friendly prompts")
    console.print("✅ [bold]Sub-task Creation:[/bold] AI automatically breaks down complex tasks")
    console.print("✅ [bold]Human Language:[/bold] Encouraging, colleague-like communication")
    console.print("✅ [bold]Multitasking:[/bold] Up to 5 simultaneous AI agents (existing feature)")
    console.print("✅ [bold]MCP Memory:[/bold] Enhanced project-specific context and learning")
    console.print("✅ [bold]Developer Focus:[/bold] AI understands coding workflows and challenges")
    
    console.print("\n🚀 [bold green]2DO is now your friendliest AI development colleague![/bold green]")

if __name__ == "__main__":
    main()