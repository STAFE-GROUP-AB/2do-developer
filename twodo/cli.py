#!/usr/bin/env python3
"""
2DO CLI - Main command line interface
"""

# Suppress urllib3 SSL warnings that can appear on macOS with LibreSSL
# Must be done before importing any packages that use urllib3
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
except (ImportError, AttributeError):
    # If urllib3 not available or warning type doesn't exist, ignore
    pass

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
from .github_integration import GitHubIntegration
from .browser_integration import BrowserIntegration
from .image_handler import ImageHandler

from .setup_guide import SetupGuide
from .mcp_manager import MCPServerManager


console = Console()

def _is_terminal_interactive():
    """Check if we're in an interactive terminal"""
    import sys
    return sys.stdin.isatty() and sys.stdout.isatty()

def _safe_confirm(message, default=False):
    """Safely ask for confirmation with fallback"""
    try:
        return Confirm.ask(message, default=default)
    except (KeyboardInterrupt, EOFError):
        raise
    except Exception:
        # If prompt fails, return default
        console.print(f"⚠️ Could not get input for: {message}")
        return default

def _safe_prompt(message, password=False, default=""):
    """Safely prompt for input with fallback"""
    try:
        result = Prompt.ask(message, password=password, default=default)
        return result.strip() if result else ""
    except (KeyboardInterrupt, EOFError):
        raise
    except Exception:
        # If prompt fails, return default
        console.print(f"⚠️ Could not get input for: {message}")
        return default

def _get_safe_working_directory():
    """Get current working directory with fallback"""
    try:
        return os.getcwd()
    except (OSError, FileNotFoundError):
        # If we can't get current directory, fall back to home directory
        return str(Path.home())

def _show_manual_setup_instructions(config_manager):
    """Show manual setup instructions"""
    console.print(Panel(
        f"📖 Manual Setup Instructions:\n\n"
        f"2DO configuration file location:\n"
        f"  {config_manager.config_file}\n\n"
        f"You can manually edit this file with your API keys:\n\n"
        f"```yaml\n"
        f"api_keys:\n"
        f"  openai: 'your-openai-api-key-here'\n"
        f"  anthropic: 'your-anthropic-api-key-here'\n"
        f"  github: 'your-github-token-here'\n"
        f"preferences:\n"
        f"  default_model: auto\n"
        f"  max_parallel_tasks: 5\n"
        f"  memory_enabled: true\n"
        f"```\n\n"
        f"Or run '2do setup' again from a stable directory.",
        title="Manual Configuration",
        style="cyan"
    ))

@click.group()
@click.version_option(package_name="2do")
def cli():
    """2DO - Intelligent AI model routing and multitasking CLI tool"""
    pass

@cli.command()
@click.option('--non-interactive', is_flag=True, help='Skip interactive prompts and show manual setup instructions')
def setup(non_interactive):
    """Initial setup - configure AI model API keys"""
    console.print(Panel.fit("🚀 Welcome to 2DO Setup", style="bold blue"))
    
    try:
        config_manager = ConfigManager()
    except Exception as e:
        console.print(f"❌ Error initializing configuration: {e}")
        console.print("💡 Try running this command from your home directory or a stable directory")
        return
    
    # Handle non-interactive mode or terminal issues
    if non_interactive or not _is_terminal_interactive():
        _show_manual_setup_instructions(config_manager)
        return
    
    # Get AI model preferences
    console.print("\n📋 Let's configure your AI models:")
    
    try:
        # OpenAI
        if _safe_confirm("Do you want to use OpenAI models?"):
            api_key = _safe_prompt("Enter your OpenAI API key", password=True)
            if api_key:
                config_manager.set_api_key("openai", api_key)
                console.print("✅ OpenAI configured")
        
        # Anthropic
        if _safe_confirm("Do you want to use Anthropic Claude models?"):
            api_key = _safe_prompt("Enter your Anthropic API key", password=True)
            if api_key:
                config_manager.set_api_key("anthropic", api_key)
                console.print("✅ Anthropic configured")
        
        # Google AI (optional)
        if _safe_confirm("Do you want to use Google Gemini models? (optional)"):
            api_key = _safe_prompt("Enter your Google AI API key", password=True)
            if api_key:
                config_manager.set_api_key("google", api_key)
                console.print("✅ Google AI configured")
        
        # GitHub
        if _safe_confirm("Do you want to configure GitHub integration?"):
            github_token = _safe_prompt("Enter your GitHub personal access token", password=True)
            if github_token:
                config_manager.set_api_key("github", github_token)
                console.print("✅ GitHub configured")
        
        # Optional MCP server setup
        console.print("\n🔌 MCP Server Setup (Optional)")
        if _safe_confirm("Would you like to configure MCP servers for enhanced development capabilities?", default=True):
            try:
                tech_stack_detector = TechStackDetector(config_manager.config_dir)
                mcp_manager = MCPServerManager(config_manager, tech_stack_detector)
                
                # Run analysis and setup
                success = mcp_manager.setup_mcp_servers_interactive()
                if success:
                    console.print("✅ MCP servers configured successfully")
                else:
                    console.print("⚠️ MCP server setup skipped")
            except Exception as mcp_error:
                console.print(f"⚠️ MCP server setup failed: {mcp_error}")
                console.print("💡 You can set up MCP servers later with: 2do mcp")
        
        console.print("\n🎉 Setup complete! You can now use '2do start' to begin.")
        console.print("💡 Use '2do mcp' to manage MCP servers anytime.")
        
    except (KeyboardInterrupt, EOFError):
        console.print("\n⚠️ Setup interrupted by user")
        _show_manual_setup_instructions(config_manager)
    except Exception as e:
        console.print(f"\n❌ Setup failed: {e}")
        console.print("💡 You can configure 2DO manually by editing the config file")
        _show_manual_setup_instructions(config_manager)

@cli.command()
@click.option('--project', '-p', help='Project directory to verify (default: current directory)')
def verify(project):
    """Verify 2DO setup and guide through missing components"""
    console.print(Panel.fit("🔍 2DO Setup Verification", style="bold cyan"))
    
    project_dir = project if project else os.getcwd()
    
    # Run comprehensive setup verification
    guide = SetupGuide(console)
    setup_status = guide.run_complete_setup_check(project_dir)
    
    # Return appropriate exit code
    if setup_status.get("is_fully_configured", False):
        console.print("\n✅ Verification complete: 2DO is ready to use!")
        return True
    else:
        console.print("\n⚠️ Verification complete: Some components need configuration")
        return False

@cli.command()
@click.option('--repo', '-r', help='GitHub repository or local path to analyze')
def start(repo):
    """Start the 2DO interactive session"""
    console.print(Panel.fit("🤖 2DO Starting...", style="bold green"))
    
    # Determine the working directory with error handling
    working_dir = repo if repo else _get_safe_working_directory()
    
    # Check if we're in a git repository
    try:
        config_manager = ConfigManager(working_dir)
    except Exception as e:
        console.print(f"❌ Error initializing configuration: {e}")
        console.print("💡 Falling back to global configuration")
        try:
            config_manager = ConfigManager()
        except Exception as e2:
            console.print(f"❌ Critical error: {e2}")
            console.print("💡 Please run '2do setup' from your home directory")
            return
    
    if config_manager.is_local_project:
        console.print(f"📁 Using local 2DO folder in git repository: {working_dir}")
    else:
        console.print("🏠 Using global configuration")
    
    if not config_manager.has_api_keys():
        console.print("❌ No API keys configured. Please run '2do setup' first.")
        return
    
    ai_router = AIRouter(config_manager)
    todo_manager = TodoManager(config_manager.config_dir)
    multitasker = Multitasker(ai_router)
    tech_detector = TechStackDetector(config_manager.config_dir)
    github_integration = GitHubIntegration(config_manager.get_api_key("github"))
    browser_integration = BrowserIntegration(working_dir)
    image_handler = ImageHandler()
    
    # Get repository info if we're in a git repo
    repo_info = None
    if config_manager.is_local_project:
        repo_info = github_integration.get_repository_info(working_dir)
        if repo_info:
            console.print(f"📁 GitHub repository detected: {repo_info['full_name']}")
            console.print(f"🌿 Current branch: {repo_info['current_branch']}")
    
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
        choices = ["add-todo", "list-todos", "create-subtasks", "start-multitask", "parse-markdown", "manage-mcp", "chat", "quit"]
        
        # Add browser options
        browser_status = browser_integration.get_status()
        if browser_status["active"]:
            choices.insert(-2, "refresh-browser")  # Before chat and quit
            choices.insert(-2, "stop-browser")
        else:
            choices.insert(-2, "start-browser")
        
        # Add GitHub options if we have repository info
        if repo_info and github_integration.github:
            choices.insert(-3, "github-issues")  # Before browser and chat/quit
            choices.insert(-3, "create-github-issue")
            choices.insert(-3, "export-todos-to-github")
        
        action = Prompt.ask(
            "What would you like to do?",
            choices=choices,
            default="chat"
        )
        
        if action == "quit":
            # Clean up browser integration before quitting
            if browser_integration.is_active:
                browser_integration.stop_browser_mode()
            break
        elif action == "add-todo":
            handle_add_todo(todo_manager, ai_router, image_handler)
        elif action == "list-todos":
            handle_list_todos(todo_manager)
        elif action == "create-subtasks":
            handle_create_subtasks(todo_manager, ai_router)
        elif action == "start-multitask":
            handle_multitask(multitasker, todo_manager, browser_integration)
        elif action == "parse-markdown":
            handle_parse_markdown(todo_manager, working_dir)
        elif action == "manage-mcp":
            handle_manage_mcp(config_manager, working_dir)
        elif action == "start-browser":
            handle_start_browser(browser_integration)
        elif action == "refresh-browser":
            handle_refresh_browser(browser_integration)
        elif action == "stop-browser":
            handle_stop_browser(browser_integration)
        elif action == "github-issues":
            handle_github_issues(github_integration, todo_manager, repo_info, working_dir)
        elif action == "create-github-issue":
            handle_create_github_issue(github_integration, repo_info)
        elif action == "export-todos-to-github":
            if repo_info and github_integration.github:
                handle_export_todos_to_github(github_integration, todo_manager, repo_info)
        elif action == "chat":
            handle_chat(ai_router, image_handler)

@cli.command()
@click.option('--project', '-p', help='Project directory to analyze (default: current directory)')
@click.option('--list', 'list_servers', is_flag=True, help='List currently configured MCP servers')
@click.option('--recommend', is_flag=True, help='Show recommendations without configuring')
def mcp(project, list_servers, recommend):
    """Manage MCP (Model Context Protocol) servers"""
    console.print(Panel.fit("🔌 MCP Server Management", style="bold blue"))
    
    try:
        # Determine working directory
        working_dir = project if project else os.getcwd()
        
        # Initialize managers
        config_manager = ConfigManager(working_dir)
        tech_stack_detector = TechStackDetector(config_manager.config_dir)
        mcp_manager = MCPServerManager(config_manager, tech_stack_detector)
        
        if list_servers:
            # List currently configured servers
            mcp_manager.list_configured_servers()
            return
        
        if recommend:
            # Show recommendations only
            recommended_servers = mcp_manager.run_tech_stack_analysis_and_recommend(working_dir)
            mcp_manager.display_recommended_servers(recommended_servers)
            return
        
        # Run full interactive setup
        success = mcp_manager.setup_mcp_servers_interactive(working_dir)
        
        if success:
            console.print("\n✅ MCP servers setup completed successfully!")
            console.print("💡 You can view configured servers with: 2do mcp --list")
        else:
            console.print("\n⚠️ MCP server setup was not completed")
            
    except Exception as e:
        console.print(f"❌ Error during MCP server management: {e}")
        console.print("💡 Try running '2do setup' first to ensure proper configuration")

def handle_add_todo(todo_manager, ai_router, image_handler):
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
    
    todo_id = todo_manager.add_todo(title, description, todo_type, priority, content)
    console.print("✅ Todo added successfully!")
    
    # Check if todo should be broken down into sub-tasks
    todo = todo_manager.get_todo_by_id(todo_id)
    if todo and todo_manager.is_todo_too_large(todo):
        console.print("🔍 This todo appears to be quite large and complex.")
        if Confirm.ask("Would you like to automatically break it down into sub-tasks?"):
            sub_task_ids = todo_manager.create_sub_tasks_from_todo(todo_id, ai_router)
            if sub_task_ids:
                console.print(f"✅ Created {len(sub_task_ids)} sub-tasks!")
                console.print("💡 Use 'list-todos' to see the sub-tasks.")

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
    table.add_column("Relation", style="magenta")
    
    # Sort todos to show parent tasks first, then their sub-tasks
    parent_todos = [todo for todo in todos if not todo.get("parent_id")]
    sub_todos = [todo for todo in todos if todo.get("parent_id")]
    
    for todo in parent_todos:
        # Show parent todo
        relation = ""
        if todo.get("sub_task_ids") and len(todo.get("sub_task_ids", [])) > 0:
            relation = f"📁 {len(todo['sub_task_ids'])} sub-tasks"
        
        table.add_row(
            str(todo["id"]),
            todo["title"],
            todo["todo_type"],
            todo["priority"],
            todo["status"],
            relation
        )
        
        # Show its sub-tasks right after
        for sub_todo in sub_todos:
            if sub_todo.get("parent_id") == todo["id"]:
                table.add_row(
                    str(sub_todo["id"]),
                    f"  ├─ {sub_todo['title']}",  # Indent sub-tasks
                    sub_todo["todo_type"],
                    sub_todo["priority"],
                    sub_todo["status"],
                    "📎 sub-task"
                )
    
    # Show any orphaned sub-tasks (shouldn't happen but just in case)
    orphaned_subs = [todo for todo in sub_todos if not any(p["id"] == todo.get("parent_id") for p in parent_todos)]
    for todo in orphaned_subs:
        table.add_row(
            str(todo["id"]),
            todo["title"],
            todo["todo_type"],
            todo["priority"],
            todo["status"],
            "⚠️ orphaned"
        )
    
    console.print(table)

def handle_multitask(multitasker, todo_manager, browser_integration):
    """Start multitasking on todos"""
    todos = todo_manager.get_pending_todos()
    
    if not todos:
        console.print("📝 No pending todos to process!")
        return
    
    console.print(f"🚀 Starting multitask processing for {len(todos)} todos...")
    
    if Confirm.ask("Proceed with multitasking?"):
        multitasker.start_multitask(todos)
        console.print("✅ Multitasking completed!")
        
        # Auto-refresh browser if active
        if browser_integration.is_active:
            console.print("🔄 Auto-refreshing browser...")
            browser_integration.refresh_browser()

def show_chat_help():
    """Display help information for chat commands"""
    console.print("\n📖 Chat Help - Available Commands:")
    console.print("=" * 50)
    
    # Chat-specific commands
    console.print("\n🎯 Chat Commands:")
    console.print("   ?        - Show this help")
    console.print("   exit     - Return to main menu")
    console.print("   image    - Load an image file manually")
    
    # AI and functionality info
    console.print("\n🤖 AI Features:")
    console.print("   • 2DO automatically chooses the best AI model for your prompt")
    console.print("   • Supports image analysis - paste images from clipboard automatically")
    console.print("   • Intelligent routing based on prompt complexity and type")
    
    # Tips
    console.print("\n💡 Tips:")
    console.print("   • Just type your question or request naturally")
    console.print("   • Images from clipboard are detected automatically")
    console.print("   • For image files, type 'image' to browse and select")
    console.print("   • Use 'exit' to return to the main 2DO menu")
    console.print("=" * 50)
    console.print()

def handle_chat(ai_router, image_handler):
    """Handle interactive chat with AI routing"""
    console.print("💬 Chat")
    console.print("💡 Type '?' for help or 'exit' to return to main menu\n")
    
    # Clean up old temporary files
    image_handler.cleanup_old_temp_files()
    
    while True:
        prompt = Prompt.ask("You")
        if prompt.lower() == 'exit':
            break
        elif prompt.strip() == '?':
            show_chat_help()
            continue
        
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
        
        # Check if prompt contains legacy image reference format
        image_path = None
        if prompt.startswith('image:'):
            parts = prompt.split(':', 1)
            if len(parts) == 2:
                image_path = parts[1].strip()
                if not os.path.exists(image_path):
                    console.print(f"❌ Image file not found: {image_path}")
                    continue
                prompt = Prompt.ask("Enter your prompt about the image")
        
        # If we have a clipboard image, include it in the context
        if clipboard_image_path:
            prompt_with_image = f"{prompt}\n\n[Image attached: {clipboard_image_path}]"
            console.print(f"🖼️  Including attached image in your request...")
        else:
            prompt_with_image = prompt
        
        # Route to best AI model
        if image_path:
            # Legacy format support
            if hasattr(ai_router, 'route_and_process_with_image'):
                response = ai_router.route_and_process_with_image(prompt, image_path)
            else:
                response = ai_router.route_and_process(f"{prompt}\n\n[Image: {image_path}]")
        else:
            response = ai_router.route_and_process(prompt_with_image)
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

def handle_manage_mcp(config_manager, working_dir):
    """Handle MCP server management in interactive mode"""
    try:
        console.print("\n🔌 MCP Server Management")
        
        # Initialize MCP manager
        tech_stack_detector = TechStackDetector(config_manager.config_dir)
        mcp_manager = MCPServerManager(config_manager, tech_stack_detector)
        
        # Show options
        action = Prompt.ask(
            "What would you like to do?",
            choices=["recommend", "configure", "list", "back"],
            default="recommend"
        )
        
        if action == "back":
            return
        elif action == "recommend":
            # Show recommendations only
            recommended_servers = mcp_manager.run_tech_stack_analysis_and_recommend(working_dir)
            if recommended_servers:
                mcp_manager.display_recommended_servers(recommended_servers)
            else:
                console.print("No recommendations available.")
        elif action == "configure":
            # Run full interactive setup
            success = mcp_manager.setup_mcp_servers_interactive(working_dir)
            if success:
                console.print("✅ MCP servers configured successfully!")
            else:
                console.print("⚠️ MCP server configuration cancelled or failed")
        elif action == "list":
            # List configured servers
            mcp_manager.list_configured_servers()
            
    except Exception as e:
        console.print(f"❌ Error in MCP management: {e}")
        console.print("💡 You may need to run '2do setup' first")

def handle_github_issues(github_integration, todo_manager, repo_info, working_dir):
    """Handle GitHub issues operations"""
    if not repo_info:
        console.print("❌ No GitHub repository information available")
        return
    
    action = Prompt.ask(
        "GitHub Issues action",
        choices=["list", "work-on", "create-todos", "finish-work"],
        default="list"
    )
    
    owner = repo_info['owner']
    repo_name = repo_info['repo_name']
    
    if action == "list":
        issues = github_integration.get_repository_issues(owner, repo_name)
        if not issues:
            console.print("📝 No open issues found")
            return
        
        console.print(f"\n📋 Open issues in {repo_info['full_name']}:")
        for issue in issues[:10]:  # Show first 10 issues
            labels_str = f" [{', '.join(issue['labels'])}]" if issue['labels'] else ""
            console.print(f"   #{issue['number']}: {issue['title']}{labels_str}")
        
        if len(issues) > 10:
            console.print(f"   ... and {len(issues) - 10} more issues")
    
    elif action == "work-on":
        issues = github_integration.get_repository_issues(owner, repo_name)
        if not issues:
            console.print("📝 No open issues found")
            return
        
        console.print("📋 Available issues:")
        for issue in issues[:10]:
            console.print(f"   #{issue['number']}: {issue['title']}")
        
        try:
            issue_num = int(Prompt.ask("Enter issue number to work on"))
            github_integration.work_on_issue(working_dir, owner, repo_name, issue_num)
        except ValueError:
            console.print("❌ Invalid issue number")
    
    elif action == "create-todos":
        priority = Prompt.ask(
            "Priority for issue todos",
            choices=["low", "medium", "high", "critical"],
            default="medium"
        )
        
        todo_ids = github_integration.create_todos_from_issues(
            owner, repo_name, todo_manager, priority=priority
        )
        if todo_ids:
            console.print(f"✅ Created {len(todo_ids)} todos from GitHub issues")
    
    elif action == "finish-work":
        commit_message = Prompt.ask("Enter commit message for your work")
        try:
            issue_num = int(Prompt.ask("Enter issue number you worked on"))
            pr_info = github_integration.finish_issue_work(
                working_dir, owner, repo_name, issue_num, commit_message
            )
            if pr_info:
                console.print(f"🎉 Work completed! Pull request: {pr_info['url']}")
        except ValueError:
            console.print("❌ Invalid issue number")

def handle_create_github_issue(github_integration, repo_info):
    """Handle creating a new GitHub issue"""
    if not repo_info:
        console.print("❌ No GitHub repository information available")
        return
    
    title = Prompt.ask("Issue title")
    body = Prompt.ask("Issue description (optional)", default="")
    
    # Ask for labels
    labels_input = Prompt.ask("Labels (comma-separated, optional)", default="")
    labels = [label.strip() for label in labels_input.split(",") if label.strip()]
    
    issue_info = github_integration.create_issue(
        repo_info['owner'], repo_info['repo_name'], title, body, labels
    )
    
    if issue_info:
        console.print(f"✅ Created issue #{issue_info['number']}: {issue_info['url']}")
    else:
        console.print("❌ Failed to create issue")

def handle_export_todos_to_github(github_integration, todo_manager, repo_info):
    """Export todos as GitHub issues with sub-task support"""
    pending_todos = todo_manager.get_pending_todos()
    
    if not pending_todos:
        console.print("📝 No pending todos to export")
        return
    
    # Separate parent todos from sub-tasks for better organization
    parent_todos = [todo for todo in pending_todos if not todo.get("parent_id")]
    sub_todos = [todo for todo in pending_todos if todo.get("parent_id")]
    
    console.print(f"📋 Found {len(pending_todos)} pending todos:")
    console.print(f"   📁 {len(parent_todos)} parent todos")
    console.print(f"   📎 {len(sub_todos)} sub-tasks")
    
    # Show preview
    for i, todo in enumerate(parent_todos[:5], 1):
        sub_count = len(todo.get("sub_task_ids", []))
        sub_info = f" (with {sub_count} sub-tasks)" if sub_count > 0 else ""
        console.print(f"   {i}. {todo['title']}{sub_info}")
    
    if len(parent_todos) > 5:
        console.print(f"   ... and {len(parent_todos) - 5} more parent todos")
    
    # Ask user preference for handling sub-tasks
    export_option = "parent-only"
    if any(len(todo.get("sub_task_ids", [])) > 0 for todo in parent_todos):
        export_option = Prompt.ask(
            "How would you like to handle todos with sub-tasks?",
            choices=["parent-only", "with-subtasks", "subtasks-as-issues"],
            default="with-subtasks"
        )
    
    if not Confirm.ask(f"Export {len(parent_todos)} parent todos as GitHub issues?"):
        return
    
    # Export todos
    created_issues = []
    total_issues_created = 0
    
    for todo in parent_todos:
        if export_option == "subtasks-as-issues" and len(todo.get("sub_task_ids", [])) > 0:
            # Use the new sub-task aware export function
            result = github_integration.export_todo_with_subtasks_to_github(
                repo_info['owner'], 
                repo_info['repo_name'], 
                todo, 
                todo_manager
            )
            
            if result['success']:
                created_issues.append(result['parent_issue'])
                total_issues_created += 1 + len(result['sub_issues'])
                
                # Update parent todo status
                todo_manager.update_todo_status(
                    todo['id'], 
                    "completed", 
                    f"Exported as GitHub issue #{result['parent_issue']['number']}: {result['parent_issue']['url']}"
                )
                
                # Update sub-task statuses
                for sub_issue in result['sub_issues']:
                    todo_manager.update_todo_status(
                        sub_issue['todo_id'],
                        "completed",
                        f"Exported as GitHub issue #{sub_issue['issue_number']}: {sub_issue['issue_url']}"
                    )
        else:
            # Traditional export (with or without sub-task info in description)
            body = f"{todo['description']}\n\n"
            if todo['content']:
                body += f"**Details:**\n{todo['content']}\n\n"
            
            # Include sub-task information if requested
            if export_option == "with-subtasks":
                sub_tasks = todo_manager.get_sub_tasks(todo['id'])
                if sub_tasks:
                    body += f"**Sub-tasks ({len(sub_tasks)} items):**\n"
                    for i, sub_task in enumerate(sub_tasks, 1):
                        body += f"{i}. {sub_task['title']} - {sub_task['description']}\n"
                    body += "\n"
            
            body += f"**Priority:** {todo['priority']}\n"
            body += f"**Type:** {todo['todo_type']}\n"
            body += f"**Created:** {todo['created_at']}"
            
            # Create labels based on todo type and priority
            labels = [f"priority-{todo['priority']}", f"type-{todo['todo_type']}"]
            if len(todo.get("sub_task_ids", [])) > 0:
                labels.append("has-subtasks")
            
            issue_info = github_integration.create_issue(
                repo_info['owner'], 
                repo_info['repo_name'], 
                todo['title'], 
                body, 
                labels
            )
            
            if issue_info:
                created_issues.append(issue_info)
                total_issues_created += 1
                # Update todo with GitHub issue reference
                todo_manager.update_todo_status(
                    todo['id'], 
                    "completed", 
                    f"Exported as GitHub issue #{issue_info['number']}: {issue_info['url']}"
                )
                console.print(f"✅ Created issue #{issue_info['number']}: {todo['title']}")
            else:
                console.print(f"❌ Failed to create issue for: {todo['title']}")
    
    if created_issues:
        console.print(f"\n🎉 Successfully exported {len(parent_todos)} todos as {total_issues_created} GitHub issues!")
        issue_numbers = [f"#{issue['number']}" for issue in created_issues if isinstance(issue, dict)]
        console.print(f"📋 Parent issues created: {', '.join(issue_numbers)}")
    else:
        console.print("❌ No issues were created")


def handle_start_browser(browser_integration):
    """Handle starting browser integration mode"""
    if browser_integration.is_active:
        console.print("🌐 Browser integration is already active!")
        return
    
    console.print("🚀 Starting browser integration mode...")
    
    if browser_integration.start_browser_mode():
        console.print("✅ Browser integration started successfully!")
        console.print("💡 Your development server is now running and browser is open")
        console.print("🔄 The browser will auto-refresh after completing tasks")
    else:
        console.print("❌ Failed to start browser integration")

def handle_refresh_browser(browser_integration):
    """Handle manual browser refresh"""
    if not browser_integration.is_active:
        console.print("❌ Browser integration is not active. Start it first.")
        return
    
    console.print("🔄 Refreshing browser...")
    browser_integration.refresh_browser()
    console.print("✅ Browser refresh signal sent")

def handle_stop_browser(browser_integration):
    """Handle stopping browser integration mode"""
    if not browser_integration.is_active:
        console.print("❌ Browser integration is not currently active")
        return
    
    if Confirm.ask("Stop browser integration mode?"):
        browser_integration.stop_browser_mode()
        console.print("✅ Browser integration stopped")

def handle_create_subtasks(todo_manager, ai_router):
    """Handle manual sub-task creation for existing todos"""
    todos = todo_manager.get_todos()
    
    # Filter to show only parent todos (no sub-tasks) that don't already have sub-tasks
    candidate_todos = [
        todo for todo in todos 
        if not todo.get("parent_id") and len(todo.get("sub_task_ids", [])) == 0
    ]
    
    if not candidate_todos:
        console.print("📝 No eligible todos found for sub-task creation.")
        console.print("💡 Eligible todos are those without existing sub-tasks.")
        return
    
    console.print("\n📋 Todos that can be broken down into sub-tasks:")
    table = Table()
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Size Analysis", style="yellow")
    
    for todo in candidate_todos:
        is_large = todo_manager.is_todo_too_large(todo)
        size_status = "🔍 Large/Complex" if is_large else "📏 Normal size"
        table.add_row(str(todo["id"]), todo["title"][:50] + "..." if len(todo["title"]) > 50 else todo["title"], size_status)
    
    console.print(table)
    
    todo_id = Prompt.ask("\nEnter the ID of the todo to break down")
    
    selected_todo = todo_manager.get_todo_by_id(todo_id)
    if not selected_todo:
        console.print("❌ Todo not found")
        return
    
    if selected_todo.get("parent_id"):
        console.print("❌ Cannot create sub-tasks for a sub-task")
        return
    
    if len(selected_todo.get("sub_task_ids", [])) > 0:
        console.print("❌ This todo already has sub-tasks")
        return
    
    console.print(f"\n📝 Breaking down: {selected_todo['title']}")
    
    # Create sub-tasks
    sub_task_ids = todo_manager.create_sub_tasks_from_todo(todo_id, ai_router)
    
    if sub_task_ids:
        console.print(f"✅ Created {len(sub_task_ids)} sub-tasks!")
        console.print("💡 Use 'list-todos' to see the sub-tasks.")
        
        # Show the created sub-tasks
        sub_tasks = todo_manager.get_sub_tasks(todo_id)
        if sub_tasks:
            console.print("\n📋 Created sub-tasks:")
            for i, sub_task in enumerate(sub_tasks, 1):
                console.print(f"   {i}. {sub_task['title']}")
    else:
        console.print("❌ Failed to create sub-tasks")


def main():
    """Main entry point"""
    cli()

if __name__ == "__main__":
    main()