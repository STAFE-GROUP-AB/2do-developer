#!/usr/bin/env python3
"""
AI Redirector CLI - Main command line interface
"""

import click
import os
import yaml
import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .config import ConfigManager
from .ai_router import AIRouter
from .todo_manager import TodoManager
from .multitasker import Multitasker
from .tech_stack import TechStackDetector
from .image_handler import ImageHandler

console = Console()

@click.group()
@click.version_option()
def cli():
    """AI Redirector - Intelligent AI model routing and multitasking CLI tool"""
    pass

@cli.command()
def setup():
    """Initial setup - configure AI model API keys"""
    console.print(Panel.fit("🚀 Welcome to AI Redirector Setup", style="bold blue"))
    
    config_manager = ConfigManager()
    
    # Get AI model preferences
    console.print("\n📋 Let's configure your AI models:")
    
    # OpenAI
    if Confirm.ask("Do you want to use OpenAI models?"):
        api_key = Prompt.ask("Enter your OpenAI API key", password=True)
        config_manager.set_api_key("openai", api_key)
        console.print("✅ OpenAI configured")
    
    # Anthropic
    if Confirm.ask("Do you want to use Anthropic Claude models?"):
        api_key = Prompt.ask("Enter your Anthropic API key", password=True)
        config_manager.set_api_key("anthropic", api_key)
        console.print("✅ Anthropic configured")
    
    # Add more AI providers as needed
    
    console.print("\n🎉 Setup complete! You can now use 'airedirector start' to begin.")

@cli.command()
@click.option('--repo', '-r', help='GitHub repository or local path to analyze')
def start(repo):
    """Start the AI Redirector interactive session"""
    console.print(Panel.fit("🤖 AI Redirector Starting...", style="bold green"))
    
    config_manager = ConfigManager()
    if not config_manager.has_api_keys():
        console.print("❌ No API keys configured. Please run 'airedirector setup' first.")
        return
    
    ai_router = AIRouter(config_manager)
    todo_manager = TodoManager()
    multitasker = Multitasker(ai_router)
    tech_detector = TechStackDetector()
    image_handler = ImageHandler()
    
    if repo:
        console.print(f"📁 Analyzing repository: {repo}")
        tech_stack = tech_detector.analyze_repo(repo)
        console.print(f"🔍 Detected tech stack: {', '.join(tech_stack)}")
        
        # Create memory files for tech stack
        if Confirm.ask(f"Create memory files for {', '.join(tech_stack)}?"):
            tech_detector.create_memory_files(tech_stack)
            console.print("💾 Memory files created")
    
    # Interactive session
    while True:
        console.print("\n" + "="*50)
        action = Prompt.ask(
            "What would you like to do?",
            choices=["add-todo", "list-todos", "start-multitask", "chat", "quit"],
            default="chat"
        )
        
        if action == "quit":
            break
        elif action == "add-todo":
            handle_add_todo(todo_manager, image_handler)
        elif action == "list-todos":
            handle_list_todos(todo_manager)
        elif action == "start-multitask":
            handle_multitask(multitasker, todo_manager)
        elif action == "chat":
            handle_chat(ai_router, image_handler)

def handle_add_todo(todo_manager, image_handler):
    """Handle adding a new todo item"""
    title = Prompt.ask("Todo title")
    description = Prompt.ask("Description (optional)", default="")
    
    todo_type = Prompt.ask(
        "Todo type",
        choices=["code", "text", "image", "general"],
        default="general"
    )
    
    priority = Prompt.ask(
        "Priority",
        choices=["low", "medium", "high", "critical"],
        default="medium"
    )
    
    # Handle file/content input based on type
    content = None
    if todo_type in ["code", "text"]:
        if Confirm.ask("Do you want to paste content now?"):
            console.print("Enter content (Ctrl+D to finish):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                content = "\n".join(lines)
    elif todo_type == "image":
        # Check for clipboard image first
        clipboard_image_path = image_handler.prompt_for_clipboard_image()
        if clipboard_image_path:
            content = clipboard_image_path
        else:
            file_path = Prompt.ask("Enter path to image file (optional)", default="")
            if file_path and os.path.exists(file_path):
                content = file_path
    
    todo_manager.add_todo(title, description, todo_type, priority, content)
    console.print("✅ Todo added successfully!")

def handle_list_todos(todo_manager):
    """Display all todos in a nice table"""
    todos = todo_manager.get_todos()
    
    if not todos:
        console.print("📝 No todos found. Add some with 'add-todo'!")
        return
    
    table = Table(title="Your Todos")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Priority", style="red")
    table.add_column("Status", style="blue")
    
    for todo in todos:
        table.add_row(
            str(todo["id"]),
            todo["title"],
            todo["type"],
            todo["priority"],
            todo["status"]
        )
    
    console.print(table)

def handle_multitask(multitasker, todo_manager):
    """Start multitasking on todos"""
    todos = todo_manager.get_pending_todos()
    
    if not todos:
        console.print("📝 No pending todos to process!")
        return
    
    console.print(f"🚀 Starting multitask processing for {len(todos)} todos...")
    
    if Confirm.ask("Proceed with multitasking?"):
        multitasker.start_multitask(todos)
        console.print("✅ Multitasking completed!")

def handle_chat(ai_router, image_handler):
    """Handle interactive chat with AI routing"""
    console.print("💬 Chat mode - AI Redirector will choose the best model for your prompt")
    console.print("🖼️  You can paste images from clipboard - they will be detected automatically")
    console.print("📸 Or type 'image' to load an image file manually")
    console.print("Type 'exit' to return to main menu\n")
    
    # Clean up old temporary files
    image_handler.cleanup_old_temp_files()
    
    while True:
        prompt = Prompt.ask("You")
        if prompt.lower() == 'exit':
            break
        
        # Check if user wants to work with images
        clipboard_image_path = None
        if prompt.lower() == 'image':
            clipboard_image_path = image_handler.prompt_for_clipboard_image()
            if clipboard_image_path:
                prompt = Prompt.ask("What would you like to know about this image?")
            else:
                continue
        else:
            # Check for clipboard image automatically (non-intrusive)
            try:
                image = image_handler.check_clipboard_for_image()
                if image is not None:
                    console.print("🖼️  Image detected in clipboard!")
                    from rich.prompt import Confirm
                    if Confirm.ask("Include this image with your prompt?"):
                        image_handler.display_image_info(image)
                        clipboard_image_path = image_handler.save_image_temporarily(image)
                        console.print(f"✅ Image attached")
            except Exception:
                pass  # Silently ignore clipboard errors
        
        # If we have a clipboard image, include it in the context
        if clipboard_image_path:
            prompt_with_image = f"{prompt}\n\n[Image attached: {clipboard_image_path}]"
            console.print(f"🖼️  Including attached image in your request...")
        else:
            prompt_with_image = prompt
        
        # Route to best AI model
        response = ai_router.route_and_process(prompt_with_image)
        console.print(f"\n🤖 AI: {response}\n")

def main():
    """Main entry point"""
    cli()

if __name__ == "__main__":
    main()