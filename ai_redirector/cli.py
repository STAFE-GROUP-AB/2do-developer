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
from .markdown_parser import MarkdownTaskParser

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
    
    # Determine the working directory
    working_dir = repo if repo else os.getcwd()
    
    # Check if we're in a git repository
    config_manager = ConfigManager(working_dir)
    if config_manager.is_local_project:
        console.print(f"📁 Using local 2DO folder in git repository: {working_dir}")
    else:
        console.print("🏠 Using global configuration")
    
    if not config_manager.has_api_keys():
        console.print("❌ No API keys configured. Please run 'airedirector setup' first.")
        return
    
    ai_router = AIRouter(config_manager)
    todo_manager = TodoManager(config_manager.config_dir)
    multitasker = Multitasker(ai_router)
    tech_detector = TechStackDetector(config_manager.config_dir)
    
    if repo or config_manager.is_local_project:
        analysis_path = repo if repo else working_dir
        console.print(f"📁 Analyzing repository: {analysis_path}")
        tech_stack = tech_detector.analyze_repo(analysis_path)
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
            choices=["add-todo", "list-todos", "start-multitask", "parse-markdown", "chat", "quit"],
            default="chat"
        )
        
        if action == "quit":
            break
        elif action == "add-todo":
            handle_add_todo(todo_manager)
        elif action == "list-todos":
            handle_list_todos(todo_manager)
        elif action == "start-multitask":
            handle_multitask(multitasker, todo_manager)
        elif action == "parse-markdown":
            handle_parse_markdown(todo_manager, working_dir)
        elif action == "chat":
            handle_chat(ai_router)

def handle_add_todo(todo_manager):
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

def handle_chat(ai_router):
    """Handle interactive chat with AI routing"""
    console.print("💬 Chat mode - AI Redirector will choose the best model for your prompt")
    console.print("Type 'exit' to return to main menu")
    console.print("Type 'image:path/to/file' to include an image in your prompt\n")
    
    while True:
        prompt = Prompt.ask("You")
        if prompt.lower() == 'exit':
            break
        
        # Check if prompt contains image reference
        image_path = None
        if prompt.startswith('image:'):
            parts = prompt.split(':', 1)
            if len(parts) == 2:
                image_path = parts[1].strip()
                if not os.path.exists(image_path):
                    console.print(f"❌ Image file not found: {image_path}")
                    continue
                prompt = Prompt.ask("Enter your prompt about the image")
        
        # Route to best AI model
        if image_path:
            response = ai_router.route_and_process_with_image(prompt, image_path)
        else:
            response = ai_router.route_and_process(prompt)
        console.print(f"\n🤖 AI: {response}\n")

def handle_parse_markdown(todo_manager, working_dir):
    """Handle parsing markdown files for tasks"""
    parser = MarkdownTaskParser()
    
    # Ask for file or directory
    target = Prompt.ask(
        "Parse markdown file or directory?", 
        choices=["file", "directory", "current"],
        default="current"
    )
    
    if target == "file":
        file_path = Prompt.ask("Enter path to markdown file")
        if not os.path.isabs(file_path):
            file_path = os.path.join(working_dir, file_path)
        tasks = parser.parse_file(file_path)
    elif target == "directory":
        dir_path = Prompt.ask("Enter directory path", default=working_dir)
        if not os.path.isabs(dir_path):
            dir_path = os.path.join(working_dir, dir_path)
        tasks = parser.parse_directory(dir_path)
    else:  # current
        tasks = parser.parse_directory(working_dir)
    
    if not tasks:
        console.print("📝 No tasks found in markdown files")
        return
    
    # Show summary
    summary = parser.get_task_summary(tasks)
    console.print(f"\n📊 Found {summary['total_tasks']} tasks:")
    console.print(f"   ✅ {summary['completed_tasks']} completed")
    console.print(f"   ⏳ {summary['pending_tasks']} pending")
    console.print(f"   📄 {summary['files_with_tasks']} files with tasks")
    
    # Show first few tasks as preview
    console.print("\n📋 Preview of tasks:")
    for i, task in enumerate(tasks[:5]):
        status_icon = "✅" if task['status'] == 'completed' else "⏳"
        console.print(f"   {status_icon} {task['title'][:60]}...")
    
    if len(tasks) > 5:
        console.print(f"   ... and {len(tasks) - 5} more tasks")
    
    # Ask if user wants to create todos from pending tasks
    pending_tasks = [t for t in tasks if t['status'] == 'pending']
    if pending_tasks and Confirm.ask(f"\nCreate {len(pending_tasks)} todos from pending tasks?"):
        priority = Prompt.ask(
            "Priority for created todos",
            choices=["low", "medium", "high", "critical"],
            default="medium"
        )
        
        todo_ids = parser.create_todos_from_tasks(tasks, todo_manager, priority)
        console.print(f"✅ Created {len(todo_ids)} todos from markdown tasks")

def main():
    """Main entry point"""
    cli()

if __name__ == "__main__":
    main()