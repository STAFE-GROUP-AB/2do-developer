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

import asyncio
import click
import os
import yaml
import json
import time
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
from .intent_router import IntentRouter
from .permission_manager import PermissionManager, diagnose_permissions, get_session_permission_manager
from .enhanced_file_handler import get_enhanced_file_handler
from .automation_engine import AutomationEngine

from .setup_guide import SetupGuide
from .mcp_manager import MCPServerManager
from .updater import UpdateManager
from .smart_code_analyzer import SmartCodeAnalyzer
from .automation_engine import EnhancedAutomationEngine
from .scheduler import Scheduler
from .escape_handler import escape_listener, check_escape_interrupt, EscapeInterrupt, raise_if_interrupted


console = Console()

def _get_colleague_task_confirmation(action: str, user_input: str) -> bool:
    """
    Get confirmation from user in a human colleague-like manner.
    Returns True if user wants to run the task immediately, False to add to list.
    Default is False (add to list) as requested in the issue.
    """
    console.print("🤔 I understand what you want to work on!")
    
    if action == "add-todo":
        message = "Would you like me to work on this task right now, or should I just add it to your todo list for later?"
        console.print("📝 This looks like a new task to track.")
    elif action == "multitask":
        message = "Should I start processing your pending tasks in parallel right now, or wait until later?"
        console.print("⚡ I can work on multiple tasks simultaneously.")
    elif action == "run-all":
        message = "Ready to tackle all your pending todos with multiple AI agents? Or should I wait?"
        console.print("🚀 This will process all your pending work with up to 5 AI agents working in parallel.")
    else:
        message = "Want me to work on this right now, or add it to your list for later?"
    
    console.print(f"💭 {message}")
    
    # Use Rich Confirm with default=False as requested in the issue
    return Confirm.ask(
        "[bold yellow]Work on this now?[/bold yellow]", 
        default=False
    )

def _is_terminal_interactive():
    """Enhanced terminal interactivity detection (handles curl | bash correctly)"""
    import sys
    
    # Check if stdout and stderr are terminals (even if stdin is piped)
    if os.isatty(1) and os.isatty(2):
        # Check if we're NOT in a CI environment
        if not any(env in os.environ for env in ['CI', 'GITHUB_ACTIONS', 'JENKINS_URL', 'GITLAB_CI']):
            # Try to access controlling terminal directly
            try:
                return os.path.exists('/dev/tty')
            except:
                pass
    
    return sys.stdin.isatty() and sys.stdout.isatty()

def _read_from_terminal(prompt_text: str, password: bool = False) -> str:
    """Read input from controlling terminal (works with curl | bash)"""
    if _is_terminal_interactive():
        try:
            # Try to read from controlling terminal
            with open('/dev/tty', 'r') as tty_in:
                # Write prompt to stderr (which should be connected to terminal)
                import sys
                sys.stderr.write(prompt_text)
                sys.stderr.flush()
                
                if password:
                    import getpass
                    return getpass.getpass("", stream=tty_in)
                else:
                    return tty_in.readline().strip()
        except:
            pass
    
    # Fallback to regular prompt
    if password:
        import getpass
        return getpass.getpass(prompt_text)
    else:
        return input(prompt_text).strip()

def _safe_confirm(message, default=False):
    """Enhanced confirmation with better terminal detection"""
    try:
        if _is_terminal_interactive():
            return Confirm.ask(message, default=default)
        else:
            # In non-interactive mode, return default
            console.print(f"⚠️ Non-interactive mode: {message} [default: {default}]")
            return default
    except (KeyboardInterrupt, EOFError):
        raise
    except Exception:
        # If prompt fails, return default
        console.print(f"⚠️ Could not get input for: {message}")
        return default

def _safe_prompt(message, password=False, default=""):
    """Enhanced prompting with better terminal detection"""
    try:
        if _is_terminal_interactive():
            if password:
                result = _read_from_terminal(f"{message}: ", password=True)
            else:
                result = Prompt.ask(message, default=default)
            return result.strip() if result else default
        else:
            # In non-interactive mode, return default
            console.print(f"⚠️ Non-interactive mode: {message} [default: {default}]")
            return default
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
@click.option('--repo', help='Path to local repository to analyze')
@click.option('--force-analyze', is_flag=True, help='Force re-analysis of the repository')
def start(repo, force_analyze):
    """Start an interactive 2DO session with natural language interface"""
    console.print(Panel("🤖 2DO Starting...", style="bold cyan"))
    
    # Run the interactive session directly without escape handler for normal operation
    _start_interactive_session(repo, force_analyze)

def _start_interactive_session(repo, force_analyze):
    """Internal method for the interactive session logic"""
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
    
    # Simplified project detection - only show if not in a git repo
    if not config_manager.is_local_project:
        console.print("🏠 Using global configuration")
    
    if not config_manager.has_api_keys():
        console.print("❌ No API keys configured. Please run '2do setup' first.")
        return
    
    # Initialize GitHub connection (silent unless there's an issue)
    github_integration = GitHubIntegration(config_manager.get_api_key("github"))
    
    ai_router = AIRouter(config_manager)
    
    # Initialize MCP filesystem server (silent initialization)
    try:
        import asyncio
        filesystem_success = asyncio.run(ai_router.initialize_filesystem(working_dir))
        if not filesystem_success:
            console.print("⚠️ File operations limited - install Node.js for full functionality")
    except Exception as e:
        console.print("⚠️ File operations limited - install Node.js for full functionality")
    
    todo_manager = TodoManager(config_manager.config_dir)
    multitasker = Multitasker(ai_router, todo_manager)
    tech_detector = TechStackDetector(config_manager.config_dir)
    browser_integration = BrowserIntegration(working_dir)
    image_handler = ImageHandler()
    intent_router = IntentRouter()
    
    # Initialize the automation engine with smart todo parsing and GitHub Pro mode
    automation_engine = AutomationEngine(todo_manager, multitasker, github_integration)
    
    # Get repository info if we're in a git repo
    repo_info = None
    if config_manager.is_local_project:
        repo_info = github_integration.get_repository_info(working_dir)
        if repo_info:
            console.print(f"📁 {repo_info['full_name']} ({repo_info['current_branch']})")

    # Handle repository analysis with memory
    tech_stack = []
    if repo or config_manager.is_local_project:
        analysis_path = repo if repo else working_dir
        
        # Check if we should skip analysis
        should_skip = config_manager.should_skip_analysis(force_analyze)
        
        if should_skip and not force_analyze:
            # Use existing analysis
            last_analysis = config_manager.get_last_analysis()
            tech_stack = last_analysis.get("tech_stack", [])
            
            if tech_stack:
                console.print(f"🔍 Tech stack: {', '.join(tech_stack)}")
            else:
                # Fallback to checking existing memory files
                tech_stack = tech_detector.get_existing_analysis()
                if tech_stack:
                    console.print(f"🔍 Tech stack: {', '.join(tech_stack)}")
                    config_manager.save_analysis_results(tech_stack, memory_files_created=True)
        
        if not tech_stack or force_analyze:
            # Run fresh analysis
            console.print("🔍 Analyzing repository...")
            tech_stack = tech_detector.analyze_repo(analysis_path, force_reanalyze=force_analyze)
            console.print(f"🔍 Tech stack: {', '.join(tech_stack)}")
            
            # Create memory files for tech stack
            memory_files_created = False
            if tech_stack and Confirm.ask(f"Create memory files for {', '.join(tech_stack)}?"):
                tech_detector.create_memory_files(tech_stack)
                memory_files_created = True
            
            # Save analysis results
            config_manager.save_analysis_results(tech_stack, memory_files_created)
    
    # Interactive session with natural language interface
    console.print("\n🤖 Welcome to 2DO - Your AI-powered development companion!")
    console.print("💡 I'm here to help you like a colleague. Just tell me what you'd like to work on!")
    console.print("   I'll ask for confirmation before running tasks and can break down complex work into smaller pieces.")
    
    # Add developer-focused context to AI router
    ai_router.set_developer_context(intent_router.get_developer_context_prompt())
    
    while True:
        console.print("\n" + "="*50)
        
        # Natural language prompt with more human-like tone
        user_input = Prompt.ask(
            "[bold cyan]Hey! What can I help you with today?[/bold cyan]",
            default=""
        )
        
        if not user_input.strip():
            console.print("😊 No worries! Let me know what you're working on whenever you're ready.")
            show_natural_language_help()
            continue
        
        # Handle special commands
        if user_input.lower().strip() in ["help", "?", "commands"]:
            show_natural_language_help()
            continue
        
        # Analyze intent
        intent_match = intent_router.analyze_intent(user_input)
        action = intent_match.intent
        
        # Show friendly confirmation with human colleague tone
        confirmation = intent_router.get_friendly_confirmation(action, intent_match.extracted_params)
        console.print(f"\n{confirmation}")
        
        # Human colleague-like task confirmation workflow
        if action in ["add-todo", "multitask", "run-all"]:
            should_run_now = _get_colleague_task_confirmation(action, user_input)
            if not should_run_now:
                console.print("👍 Got it! I'll add this to your list and you can tackle it later when you're ready.")
                # Continue with adding to list but don't execute
                if action == "add-todo":
                    handle_add_todo_natural(todo_manager, ai_router, image_handler, user_input, intent_match.extracted_params, execute_immediately=False, multitasker=multitasker)
                continue
        
        if action == "quit":
            console.print("👋 Take care! Feel free to come back whenever you need help with your work.")
            # Clean up browser integration before quitting
            if browser_integration.is_active:
                browser_integration.stop_browser_mode()
            break
        elif action == "add-todo":
            # Try smart todo parsing first
            smart_todo_handled = asyncio.run(automation_engine.handle_smart_todo_creation(user_input))
            if not smart_todo_handled:
                # Fallback to traditional todo creation
                handle_add_todo_natural(todo_manager, ai_router, image_handler, user_input, intent_match.extracted_params, multitasker=multitasker)
        elif action == "list-todos":
            handle_list_todos(todo_manager)
        elif action == "remove-todo":
            handle_remove_todo(todo_manager)
        elif action == "remove-completed-todos":
            handle_remove_completed_todos(todo_manager)
        elif action == "create-subtasks":
            handle_create_subtasks(todo_manager, ai_router)
        elif action == "multitask":
            console.print("🔥 Great! Let me process your pending tasks with multiple AI agents working in parallel.")
            handle_multitask(multitasker, todo_manager, browser_integration)
        elif action == "run-all":
            # The ultimate shortcut - run all todos at once!
            console.print("🚀 Awesome! I'll get all your pending work done with up to 5 AI agents. This is going to be efficient!")
            # CRITICAL FIX: Pass working directory to ensure correct file operations
            automation_engine.run_all_todos_sync(working_dir)
        elif action == "parse-markdown":
            handle_parse_markdown(todo_manager, working_dir)
        elif action == "mcp-management":
            handle_manage_mcp(config_manager, working_dir)
        elif action == "browser-integration":
            handle_browser_integration_natural(browser_integration, user_input)
        elif action == "github-issues":
            handle_github_issues(github_integration, todo_manager, repo_info, working_dir)
        elif action == "create-github-issue":
            handle_create_github_issue_natural(github_integration, repo_info, user_input, intent_match.extracted_params)
        elif action == "export-todos-to-github":
            if repo_info and github_integration.github:
                handle_export_todos_to_github(github_integration, todo_manager, repo_info)
        elif action == "chat":
            handle_chat_natural(ai_router, image_handler, user_input)
        else:
            # Fallback to chat for unrecognized intents - more human-like
            console.print("🤔 Hmm, I'm not quite sure what you're asking for, but let me try to help anyway!")
            handle_chat_natural(ai_router, image_handler, user_input)

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

@cli.command()
@click.option('--project', '-p', help='Project directory to analyze (default: current directory)')
@click.option('--force', is_flag=True, help='Force re-analysis even if already analyzed')
def analyze(project, force):
    """Analyze repository technology stack and create memory files"""
    console.print(Panel.fit("🔍 Repository Analysis", style="bold cyan"))
    
    # Determine working directory
    working_dir = project if project else _get_safe_working_directory()
    
    try:
        config_manager = ConfigManager(working_dir)
        tech_detector = TechStackDetector(config_manager.config_dir)
        
        # Check if already analyzed
        if not force and config_manager.has_been_analyzed():
            last_analysis = config_manager.get_last_analysis()
            existing_tech_stack = last_analysis.get("tech_stack", [])
            
            console.print(f"📁 Repository was already analyzed")
            if existing_tech_stack:
                console.print(f"🔍 Previous tech stack: {', '.join(existing_tech_stack)}")
            
            if not _safe_confirm("Re-analyze anyway?", default=False):
                console.print("⏭️ Analysis skipped")
                return
        
        # Run analysis
        console.print(f"📁 Analyzing repository: {working_dir}")
        tech_stack = tech_detector.analyze_repo(working_dir, force_reanalyze=True)
        
        if not tech_stack:
            console.print("⚠️ No technologies detected")
            return
            
        console.print(f"🔍 Detected tech stack: {', '.join(tech_stack)}")
        
        # Create memory files
        memory_files_created = False
        if _safe_confirm(f"Create memory files for {', '.join(tech_stack)}?", default=True):
            tech_detector.create_memory_files(tech_stack)
            console.print("💾 Memory files created")
            memory_files_created = True
        
        # Save analysis results
        config_manager.save_analysis_results(tech_stack, memory_files_created)
        console.print("✅ Analysis complete and saved")
        
    except Exception as e:
        console.print(f"❌ Error during analysis: {e}")

@cli.command()
@click.option('--check-only', is_flag=True, help='Only check for updates without installing')
@click.option('--force', is_flag=True, help='Force update even if already up to date')
def update(check_only, force):
    """Check for and install 2DO updates"""
    try:
        updater = UpdateManager()
        
        if check_only:
            updater.check_only()
        else:
            success = updater.run_update_process(force=force)
            if not success:
                # Exit with error code if update failed
                raise click.ClickException("Update failed")
    except Exception as e:
        console.print(f"❌ Update error: {e}")
        raise click.ClickException("Update process failed")

@cli.command()
@click.option('--interactive', is_flag=True, default=True, help='Interactive configuration mode')
@click.option('--list', 'list_servers', is_flag=True, help='List configured MCP servers')
def mcp(interactive, list_servers):
    """Configure advanced MCP servers for enhanced AI capabilities"""
    from .config import ConfigManager
    from rich.table import Table
    
    config_manager = ConfigManager()
    
    if list_servers:
        # List configured servers
        servers = config_manager.get_mcp_servers()
        
        if not servers:
            console.print("💭 No MCP servers configured")
            return
        
        table = Table(title="🚀 Configured MCP Servers")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Description", style="white")
        
        for server in servers:
            status = "✅ Enabled" if server.get('enabled', True) else "❌ Disabled"
            table.add_row(
                server.get('name', 'Unknown'),
                server.get('type', 'Unknown'),
                status,
                server.get('description', 'No description')
            )
        
        console.print(table)
        return
    
    if interactive:
        # Interactive configuration
        console.print("🎆 [bold blue]Advanced MCP Server Configuration[/bold blue]")
        console.print("Enhance your 2do with powerful AI capabilities:\n")
        
        console.print("📡 [bold]Web Fetch MCP[/bold] - Research web content, APIs, and documentation")
        console.print("🧠 [bold]Memory MCP[/bold] - Persistent context and memory across sessions")
        console.print("🗄️ [bold]Database MCP[/bold] - Direct database operations and queries")
        console.print("🎨 [bold]Figma MCP[/bold] - Design system integration and component access")
        console.print("🐙 [bold]GitHub MCP[/bold] - Enhanced repository operations with tokens\n")
        
        try:
            config_manager.configure_advanced_mcp_servers()
        except KeyboardInterrupt:
            console.print("\n⏹️ Configuration cancelled")
        except Exception as e:
            console.print(f"\n❌ Configuration error: {e}")
    else:
        console.print("💡 Use --interactive flag for guided setup or --list to view configured servers")

@cli.command("add-ai")
@click.option('--provider', help='AI provider name (e.g., openai, anthropic, google)')
@click.option('--model', help='Model name (e.g., claude-opus-4, gpt-4, claude-3-opus)')
@click.option('--api-key', help='API key for the provider')
@click.option('--list-supported', is_flag=True, help='Show supported models from built-in list')
def add_ai(provider, model, api_key, list_supported):
    """Add AI models and providers with your own API keys"""
    console.print(Panel.fit("🤖 Add AI Models", style="bold blue"))
    
    # Initialize config manager
    working_dir = os.getcwd()
    config_manager = ConfigManager(working_dir)
    
    if list_supported:
        _show_supported_models()
        return
    
    # Interactive mode if no options provided
    if not provider and not model and not api_key:
        _interactive_add_ai(config_manager)
    else:
        _direct_add_ai(config_manager, provider, model, api_key)


@cli.command("ai-list")
@click.option('--show-free', is_flag=True, help='Show only free models')
@click.option('--show-configured', is_flag=True, help='Show only configured models')
def ai_list(show_free, show_configured):
    """List all available AI models and their status"""
    console.print(Panel.fit("🤖 Available AI Models", style="bold blue"))
    
    # Initialize components
    working_dir = os.getcwd() 
    config_manager = ConfigManager(working_dir)
    ai_router = AIRouter(config_manager)
    
    _display_ai_models(ai_router, config_manager, show_free, show_configured)

def handle_add_todo(todo_manager, ai_router, image_handler):
    """Handle adding a new todo item"""
    title = Prompt.ask("Todo title")
    
    # Validate title is not empty
    if not title.strip():
        console.print("❌ Todo title cannot be empty. Cancelling todo creation.")
        return
    
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
    
    table = Table(title="📋 Your Todos")
    table.add_column("ID", style="cyan", width=8)
    table.add_column("Title", style="bold")
    table.add_column("Type", style="magenta", width=8)
    table.add_column("Priority", style="yellow", width=8)
    table.add_column("Status", style="green", width=12)
    table.add_column("Created", style="dim", width=10)
    
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_todos = sorted(todos, key=lambda x: (
        priority_order.get(x.get("priority", "medium"), 2),
        x.get("created_at", "")
    ))
    
    for todo in sorted_todos:
        status = todo.get("status", "pending")
        status_display = {
            "pending": "⏳ Pending",
            "in_progress": "🔄 In Progress", 
            "completed": "✅ Completed",
            "failed": "❌ Failed"
        }.get(status, status)
        
        priority = todo.get("priority", "medium")
        priority_display = {
            "critical": "🔥 Critical",
            "high": "🔴 High",
            "medium": "🟡 Medium",
            "low": "🟢 Low"
        }.get(priority, priority)
        
        created_at = todo.get("created_at", "")
        if created_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_display = dt.strftime("%m/%d")
            except:
                created_display = created_at[:10] if len(created_at) >= 10 else created_at
        else:
            created_display = "N/A"
        
        title = todo.get("title", "")
        if len(title) > 50:
            title = title[:47] + "..."
        
        if todo.get("parent_id"):
            title = f"  ↳ {title}"  # Indent sub-tasks
        elif todo.get("sub_task_ids") and len(todo["sub_task_ids"]) > 0:
            title = f"📁 {title} ({len(todo['sub_task_ids'])} sub-tasks)"
        
        table.add_row(
            todo.get("id", "")[:8],
            title,
            todo.get("todo_type", "general"),
            priority_display,
            status_display,
            created_display
        )
    
    console.print(table)
    
    stats = todo_manager.get_completion_stats()
    completion_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
    console.print(f"\n📊 Progress: {stats['completed']}/{stats['total']} completed ({completion_rate:.1f}%)")

def handle_remove_todo(todo_manager):
    """Handle removing a todo by ID"""
    todos = todo_manager.get_todos()
    
    if not todos:
        console.print("📝 No todos found to remove.")
        return
    
    handle_list_todos(todo_manager)
    
    todo_id = Prompt.ask("\nEnter the ID of the todo to remove (or 'cancel' to abort)")
    
    if todo_id.lower() == 'cancel':
        console.print("🚫 Todo removal cancelled.")
        return
    
    todo = todo_manager.get_todo_by_id(todo_id)
    if not todo:
        console.print(f"❌ Todo with ID '{todo_id}' not found.")
        return
    
    console.print(f"\n📋 Todo to remove: {todo['title']}")
    if Confirm.ask("Are you sure you want to delete this todo?"):
        success = todo_manager.delete_todo(todo_id)
        if success:
            console.print("✅ Todo removed successfully!")
        else:
            console.print("❌ Failed to remove todo.")
    else:
        console.print("🚫 Todo removal cancelled.")

def handle_remove_completed_todos(todo_manager):
    """Handle removing all completed todos"""
    todos = todo_manager.get_todos()
    completed_todos = [todo for todo in todos if todo.get("status") == "completed"]
    
    if not completed_todos:
        console.print("📝 No completed todos found to remove.")
        return
    
    console.print(f"\n🗑️ Found {len(completed_todos)} completed todos:")
    for todo in completed_todos:
        console.print(f"  • {todo['id'][:8]}: {todo['title']}")
    
    if Confirm.ask(f"\nAre you sure you want to delete all {len(completed_todos)} completed todos?"):
        removed_count = 0
        for todo in completed_todos:
            if todo_manager.delete_todo(todo['id']):
                removed_count += 1
        
        console.print(f"✅ Removed {removed_count} completed todos!")
        
        remaining_todos = todo_manager.get_todos()
        if remaining_todos:
            console.print(f"\n📋 {len(remaining_todos)} todos remaining.")
        else:
            console.print("\n🎉 All todos cleared! Time to add some new ones.")
    else:
        console.print("🚫 Cleanup cancelled.")

def handle_multitask(multitasker, todo_manager, browser_integration):
    """Start multitasking on todos"""
    todos = todo_manager.get_pending_todos()
    
    if not todos:
        console.print("📝 No pending todos to process!")
        return
    
    console.print(f"🚀 Starting multitask processing for {len(todos)} todos...")
    console.print("💡 Press Escape key at any time to interrupt the operation")
    
    if Confirm.ask("Proceed with multitasking?"):
        try:
            with escape_listener() as escape_handler:
                # CRITICAL FIX: start_multitask is now async, use asyncio.run
                asyncio.run(multitasker.start_multitask(todos))
                
                if escape_handler.is_interrupted():
                    console.print("⚠️ Multitasking interrupted by user")
                    return
                    
            console.print("✅ Multitasking completed!")
            
            # Auto-refresh browser if active
            if browser_integration.is_active:
                console.print("🔄 Auto-refreshing browser...")
                browser_integration.refresh_browser()
                
        except EscapeInterrupt:
            console.print("⚠️ Multitasking interrupted by escape key")
        except KeyboardInterrupt:
            console.print("⚠️ Multitasking interrupted by user (Ctrl+C)")

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
    console.print("💡 Type '?' for help, 'exit' to return to main menu, or press Escape to interrupt AI responses\n")
    
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
        
        # Route to best AI model with escape handling
        try:
            with escape_listener() as escape_handler:
                if image_path:
                    # Legacy format support
                    if hasattr(ai_router, 'route_and_process_with_image'):
                        response = ai_router.route_and_process_with_image(prompt, image_path)
                    else:
                        response = asyncio.run(ai_router.route_and_process(f"{prompt}\n\n[Image: {image_path}]"))
                else:
                    response = asyncio.run(ai_router.route_and_process(prompt_with_image))
                
                if escape_handler.is_interrupted():
                    console.print("\n⚠️ AI response interrupted by user")
                    continue
                    
            console.print(f"\n🤖 AI: {response}\n")
            
        except EscapeInterrupt:
            console.print("\n⚠️ AI response interrupted by escape key")
        except KeyboardInterrupt:
            console.print("\n⚠️ AI response interrupted by user (Ctrl+C)")

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


def show_natural_language_help():
    """Display help for the natural language interface"""
    console.print("\n🎯 2DO Natural Language Help")
    console.print("=" * 50)
    
    console.print("\n💬 Just tell me what you want to do! Here are some examples:")
    
    console.print("\n📝 [bold]Managing Todos:[/bold]")
    console.print("   • 'Add a todo for fixing the login bug'")
    console.print("   • 'Create a task to implement user authentication'")
    console.print("   • 'I need to debug the payment system'")
    console.print("   • 'Show me my current tasks'")
    console.print("   • 'What am I working on?'")
    console.print("   • 'Break down my complex task into smaller pieces'")
    console.print("   • 'Remove todo by ID'")
    console.print("   • 'Delete completed todos'")
    console.print("   • 'Clean up finished tasks'")
    
    console.print("\n🤖 [bold]SMART TODO AUTOMATION:[/bold]")
    console.print("   • 'Change the text in readme.md from Hello to Hi'")
    console.print("   • 'Add a new function called validateUser to auth.js'")
    console.print("   • 'Fix the bug in payment.py line 42'")
    console.print("   • 'Replace the old API call with the new one in app.js'")
    console.print("   • 'Remove the deprecated function from utils.py'")
    console.print("   • 'Refactor the database connection in config.py'")
    
    console.print("\n🚀 [bold]ULTIMATE SHORTCUTS:[/bold]")
    console.print("   • 'run all' - Start multitasking on ALL pending todos")
    console.print("   • 'execute everything' - Maximum productivity mode")
    console.print("   • 'start all todos' - The ultimate automation shortcut")
    
    console.print("\n🐙 [bold]GitHub Integration:[/bold]")
    console.print("   • 'Show me GitHub issues'")
    console.print("   • 'Create a GitHub issue for the API bug'")
    console.print("   • 'Export my todos to GitHub'")
    console.print("   • 'Sync with repository issues'")
    
    console.print("\n🌐 [bold]Development Tools:[/bold]")
    console.print("   • 'Start browser integration'")
    console.print("   • 'Parse markdown files for tasks'")
    console.print("   • 'Manage MCP servers'")
    console.print("   • 'Run multitask on all todos'")
    
    console.print("\n💡 [bold]Getting Help:[/bold]")
    console.print("   • 'How do I implement OAuth?'")
    console.print("   • 'Help me with React state management'")
    console.print("   • 'Explain database indexing'")
    console.print("   • 'What's the best way to handle errors?'")
    
    console.print("\n🚪 [bold]Exiting:[/bold]")
    console.print("   • 'quit', 'exit', 'bye', 'done'")
    
    console.print("\n🤖 Remember: I'm here to help make your development workflow faster and more enjoyable!")
    console.print("=" * 50)

def handle_add_todo_natural(todo_manager, ai_router, image_handler, user_input, extracted_params, execute_immediately=True, multitasker=None):
    """Handle adding a todo from natural language input with human colleague interaction"""
    # Use extracted title if available, otherwise prompt
    if extracted_params and "suggested_title" in extracted_params:
        suggested_title = extracted_params["suggested_title"]
        title = Prompt.ask("📝 What should I call this task?", default=suggested_title)
    else:
        # Use AI to suggest a title based on user input
        ai_suggestion = asyncio.run(ai_router.route_and_process(
            f"Based on this request: '{user_input}', suggest a concise todo title (max 60 characters). "
            f"Just return the title, nothing else."
        ))
        title = Prompt.ask("📝 What should I call this task?", default=ai_suggestion.strip())
    
    # Validate title is not empty
    if not title.strip():
        console.print("😅 Hmm, I need a title to track this task. Let's try again!")
        return
    
    description = Prompt.ask("💭 Any additional details you'd like to add? (optional)", default="")
    
    # Smart type detection based on content
    todo_type = "general"
    user_input_lower = user_input.lower()
    if any(word in user_input_lower for word in ["code", "debug", "implement", "fix", "build", "deploy"]):
        todo_type = "code"
    elif any(word in user_input_lower for word in ["write", "document", "readme", "docs"]):
        todo_type = "text"
    
    todo_type = Prompt.ask(
        "🏷️ What type of work is this?",
        choices=["code", "text", "image", "general"],
        default=todo_type
    )
    
    # Smart priority detection
    priority = "medium"
    if any(word in user_input_lower for word in ["urgent", "critical", "asap", "important", "high"]):
        priority = "high"
    elif any(word in user_input_lower for word in ["minor", "low", "later", "someday"]):
        priority = "low"
    elif any(word in user_input_lower for word in ["critical", "emergency", "broken", "down"]):
        priority = "critical"
    
    priority = Prompt.ask(
        "⚡ How urgent is this?",
        choices=["low", "medium", "high", "critical"],
        default=priority
    )
    
    # Handle content input
    content = None
    if todo_type in ["code", "text"]:
        if Confirm.ask("🖋️ Want to add any specific content or details now?"):
            console.print("📝 Enter content (Ctrl+D when finished):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                content = "\n".join(lines)
    elif todo_type == "image":
        clipboard_image_path = image_handler.prompt_for_clipboard_image()
        if clipboard_image_path:
            content = clipboard_image_path
        else:
            file_path = Prompt.ask("📷 Path to image file (optional)", default="")
            if file_path and os.path.exists(file_path):
                content = file_path
    
    todo_id = todo_manager.add_todo(title, description, todo_type, priority, content)
    console.print("✅ Perfect! I've added this to your task list.")
    
    # Auto-suggest sub-task breakdown for complex todos
    todo = todo_manager.get_todo_by_id(todo_id)
    if todo and todo_manager.is_todo_too_large(todo):
        console.print("🔍 You know what? This task looks pretty substantial!")
        if Confirm.ask("🎯 Want me to break it down into smaller, more manageable pieces?"):
            sub_task_ids = todo_manager.create_sub_tasks_from_todo(todo_id, ai_router)
            if sub_task_ids:
                console.print(f"🎉 Great! I've created {len(sub_task_ids)} smaller tasks to help you tackle this step by step!")
                console.print("💡 Just ask to 'show me my tasks' to see the breakdown.")
                
                # If this was set to execute immediately, ask about sub-tasks too
                if execute_immediately:
                    if Confirm.ask("🚀 Want me to start working on these sub-tasks right now?"):
                        console.print("🔥 Awesome! Let me get started on these right away.")
                        if multitasker:
                            # Get the subtasks and process them
                            sub_tasks = todo_manager.get_sub_tasks(todo_id)
                            if sub_tasks:
                                try:
                                    asyncio.run(multitasker.start_multitask(sub_tasks))
                                except Exception as e:
                                    console.print(f"❌ Error processing sub-tasks: {e}")
                                    console.print("💡 You can run them manually with 'multitask' command")
                        else:
                            console.print("⚠️ Multitasker not available. You can run the sub-tasks manually with 'multitask' command")
                        return True
                else:
                    return False  # Don't execute immediately if subtasks created but execution not requested
            else:
                console.print("⚠️ Couldn't create sub-tasks, but I can still work on the original task if you want.")
        else:
            console.print("👍 No problem! I'll keep it as one large task.")
    
    # Handle immediate execution for non-subtask cases or when subtasks weren't created
    if execute_immediately:
        if multitasker and todo:
            if Confirm.ask("🚀 Ready to start working on this task right now?"):
                console.print("🔥 Let me get started on this right away.")
                try:
                    asyncio.run(multitasker.start_multitask([todo]))
                except Exception as e:
                    console.print(f"❌ Error processing task: {e}")
                    console.print("💡 You can run it manually with 'multitask' command")
                return True
    
    return execute_immediately

def handle_create_github_issue_natural(github_integration, repo_info, user_input, extracted_params):
    """Handle creating GitHub issue from natural language"""
    if not repo_info:
        console.print("❌ No GitHub repository information available")
        return
    
    # Use extracted title if available
    if extracted_params and "suggested_title" in extracted_params:
        suggested_title = extracted_params["suggested_title"]
        title = Prompt.ask("Issue title", default=suggested_title)
    else:
        title = Prompt.ask("Issue title")
    
    body = Prompt.ask("Issue description (optional)", default="")
    
    # Smart label suggestions based on user input
    suggested_labels = []
    user_input_lower = user_input.lower()
    if any(word in user_input_lower for word in ["bug", "error", "broken", "issue", "problem"]):
        suggested_labels.append("bug")
    if any(word in user_input_lower for word in ["feature", "enhancement", "new", "add"]):
        suggested_labels.append("enhancement")
    if any(word in user_input_lower for word in ["doc", "documentation", "readme"]):
        suggested_labels.append("documentation")
    
    labels_input = Prompt.ask(
        "Labels (comma-separated, optional)", 
        default=",".join(suggested_labels) if suggested_labels else ""
    )
    labels = [label.strip() for label in labels_input.split(",") if label.strip()]
    
    issue_info = github_integration.create_issue(
        repo_info['owner'], repo_info['repo_name'], title, body, labels
    )
    
    if issue_info:
        console.print(f"🎉 Successfully created issue #{issue_info['number']}: {issue_info['url']}")
        console.print("🚀 Time to tackle that problem!")
    else:
        console.print("❌ Failed to create issue - check your GitHub configuration")

def handle_browser_integration_natural(browser_integration, user_input):
    """Handle browser integration from natural language"""
    user_input_lower = user_input.lower()
    
    if any(word in user_input_lower for word in ["start", "open", "launch", "begin"]):
        handle_start_browser(browser_integration)
    elif any(word in user_input_lower for word in ["refresh", "reload", "update"]):
        handle_refresh_browser(browser_integration)
    elif any(word in user_input_lower for word in ["stop", "close", "end"]):
        handle_stop_browser(browser_integration)
    else:
        # Show browser status and options
        browser_status = browser_integration.get_status()
        if browser_status["active"]:
            console.print("🌐 Browser integration is currently active!")
            action = Prompt.ask(
                "What would you like to do?",
                choices=["refresh", "stop", "status"],
                default="status"
            )
            if action == "refresh":
                handle_refresh_browser(browser_integration)
            elif action == "stop":
                handle_stop_browser(browser_integration)
            else:
                console.print(f"📊 Browser Status: {browser_status}")
        else:
            console.print("🌐 Browser integration is not currently running.")
            if Confirm.ask("Would you like to start it?"):
                handle_start_browser(browser_integration)

def handle_chat_natural(ai_router, image_handler, user_input):
    """Handle natural chat - enhanced with developer context"""
    console.print("💬 Let me help you with that...")
    
    # Clean up old temporary files
    image_handler.cleanup_old_temp_files()
    
    # Check for clipboard image
    clipboard_image_path = None
    try:
        image = image_handler.check_clipboard_for_image()
        if image is not None:
            console.print("🖼️  I see you have an image in your clipboard!")
            if Confirm.ask("Should I include this image in my analysis?"):
                image_handler.display_image_info(image)
                clipboard_image_path = image_handler.save_image_temporarily(image)
                console.print(f"✅ Image attached to your question")
    except Exception:
        pass  # Silently ignore clipboard errors
    
    # Enhance the prompt with developer context
    enhanced_prompt = f"""As a developer-focused AI assistant, please help with this request: {user_input}

Context: This is from a developer using 2DO, a development productivity tool. Please provide helpful, practical advice that's relevant to software development workflows. Be friendly, encouraging, and add a touch of developer humor when appropriate.

If this is a technical question, provide clear explanations with code examples when relevant. If it's about productivity or workflow, suggest best practices that work well for developers."""
    
    if clipboard_image_path:
        enhanced_prompt += f"\n\n[Image attached: {clipboard_image_path}]"
    
    # Route to best AI model with developer context
    response = asyncio.run(ai_router.route_and_process(enhanced_prompt))
    console.print(f"\n🤖 {response}\n")
    
    # Offer follow-up suggestions
    console.print("💡 Want to do something with this information? Try:")
    console.print("   • 'Add a todo for implementing this'")
    console.print("   • 'Create a GitHub issue about this'")
    console.print("   • 'Show me my current tasks' to see what else you're working on")


def _show_supported_models():
    """Show all supported models from the built-in list"""
    console.print("\n🎯 Supported AI Models:")
    
    # Free models (included by default)
    console.print("\n💚 [bold green]Free Models (Included by Default):[/bold green]")
    free_models = [
        ("OpenAI", "gpt-4o-mini", "Fast, cost-effective model"),
        ("OpenAI", "gpt-3.5-turbo", "General purpose, high speed"),
        ("Anthropic", "claude-3-5-haiku", "Ultra-fast simple tasks"),
        ("Google", "gemini-1.5-flash", "Fast multimodal model"),
    ]
    
    for provider, model, description in free_models:
        console.print(f"   • [cyan]{provider}[/cyan] - [yellow]{model}[/yellow]: {description}")
    
    # Premium models (require API keys) - Claude 4 models highlighted
    console.print("\n💰 [bold yellow]Premium Models (Require API Keys):[/bold yellow]")
    console.print("\n🏆 [bold cyan]Claude 4 Models (Premier for Coding):[/bold cyan]")
    claude_4_models = [
        ("Anthropic", "claude-opus-4", "🥇 Premier coding model - best for complex development"),
        ("Anthropic", "claude-sonnet-4", "⭐ Advanced coding and reasoning"),
    ]
    
    for provider, model, description in claude_4_models:
        console.print(f"   • [cyan]{provider}[/cyan] - [bold yellow]{model}[/bold yellow]: {description}")
    
    console.print("\n🚀 [bold white]Other Premium Models:[/bold white]")
    premium_models = [
    ("OpenAI", "gpt-5-pro",      "Unified next-gen model with expert reasoning, multimodal input, agentic capabilities (highest performance)"),
    ("OpenAI", "gpt-5",          "High reasoning, multimodal inputs (text, image, audio, video), extended context, free user access with some limits"),
    ("OpenAI", "gpt-5-mini",     "Cost-optimized variant, lighter and faster"),
    ("OpenAI", "gpt-5-nano",     "Ultra-light, ultra-fast variant for mobile/low-cost use"),
    ("Anthropic", "claude-opus-4", "Top coding and deep reasoning model, long-horizon agentic workflows"),
    ("Anthropic", "claude-sonnet-4", "Balanced efficiency-focused model with strong coding and reasoning"),
    ("Google", "gemini-2.5-pro", "Massive 1M-token context, multimodal, great for long-context synthesis"),
    ("xAI", "grok-4",           "Strong code and reasoning, real-time updates, competitive pricing"),
    ("DeepSeek", "deepseek-r1", "Open-source chain-of-thought model—cost-effective reasoning & code performance"),
    ("Perplexity", "pplx-70b-online", "Search-augmented model with timely web grounding"),
]
    
    for provider, model, description in premium_models:
        console.print(f"   • [cyan]{provider}[/cyan] - [yellow]{model}[/yellow]: {description}")
    
    console.print(f"\n💡 Use [bold]2do add-ai[/bold] to add any of these models with your API key")
    console.print(f"🏆 [bold cyan]Recommended for coding:[/bold cyan] Claude Opus 4 models offer the best performance for development tasks!")


def _interactive_add_ai(config_manager):
    """Interactive AI model addition"""
    
    # Show current providers
    current_providers = config_manager.get_available_providers()
    if current_providers:
        console.print(f"\n📋 Currently configured providers: {', '.join(current_providers)}")
    
    console.print("\n🎯 Choose how to add AI models:")
    console.print("   1. Add from supported list")
    console.print("   2. Add custom provider/model")
    
    choice = Prompt.ask("Your choice", choices=["1", "2"], default="1")
    
    if choice == "1":
        _add_from_supported_list(config_manager)
    else:
        _add_custom_model(config_manager)


def _add_from_supported_list(config_manager):
    """Add model from supported list"""
    
    console.print("\n🤖 Available providers:")
    providers = ["openai", "anthropic", "google", "xai", "deepseek", "mistral", "cohere", "perplexity"]
    for i, provider in enumerate(providers, 1):
        has_key = "✅" if config_manager.get_api_key(provider) else "❌"
        console.print(f"   {i}. {provider} {has_key}")
    
    provider_choice = Prompt.ask("Choose provider (1-8)", choices=[str(i) for i in range(1, 9)])
    provider = providers[int(provider_choice) - 1]
    
    # Check if API key exists
    if not config_manager.get_api_key(provider):
        api_key = Prompt.ask(f"Enter {provider} API key", password=True)
        config_manager.set_api_key(provider, api_key)
        console.print(f"✅ API key saved for {provider}")
    else:
        console.print(f"✅ Using existing {provider} API key")
    
    console.print(f"\n🎉 {provider} models are now available!")
    console.print(f"💡 Use [bold]2do ai-list[/bold] to see all available models")


def _add_custom_model(config_manager):
    """Add custom provider and model"""
    
    provider = Prompt.ask("Provider name (e.g., 'my-custom-provider')")
    api_key = Prompt.ask("API key", password=True)
    
    # Save the API key
    config_manager.set_api_key(provider, api_key)
    
    console.print(f"✅ Custom provider '{provider}' added!")
    console.print("⚠️  Note: You'll need to modify the AI router code to add the actual model implementation")


def _direct_add_ai(config_manager, provider, model, api_key):
    """Direct AI model addition with command line arguments"""
    
    if not provider:
        console.print("❌ Provider is required")
        return
    
    if not api_key:
        api_key = Prompt.ask(f"Enter API key for {provider}", password=True)
    
    config_manager.set_api_key(provider, api_key)
    console.print(f"✅ API key saved for {provider}")
    
    if model:
        console.print(f"💡 Model '{model}' will be available if supported by {provider}")


def _display_ai_models(ai_router, config_manager, show_free, show_configured):
    """Display AI models in a formatted table"""
    
    # Get all models (both configured and potential)
    configured_models = ai_router.models
    available_providers = config_manager.get_available_providers()
    
    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan")
    table.add_column("Model", style="yellow") 
    table.add_column("Status", style="green")
    table.add_column("Type", style="blue")
    table.add_column("Speed", style="white")
    table.add_column("Strengths", style="dim")
    
    # Add configured models
    for model_name, model in configured_models.items():
        status = "✅ Ready"
        model_type = "💚 Free" if model.is_free else "💰 Paid"
        speed = "⚡" * (model.speed_rating // 2) if model.speed_rating else "❓"
        strengths = ", ".join(model.strengths[:3])  # Show first 3 strengths
        
        if show_free and not model.is_free:
            continue
        if show_configured:  # All configured models are shown
            pass
            
        table.add_row(
            model.provider.title(),
            model_name,
            status,
            model_type,
            speed,
            strengths
        )
    
    # Add potential models for providers with API keys but no models loaded
    potential_models = {
        "xai": [("grok-4", "Advanced reasoning", 7, ["reasoning", "general"])],
        "deepseek": [
            ("deepseek-v3", "Code and reasoning", 6, ["code", "reasoning"]),
            ("deepseek-r1", "Advanced reasoner", 5, ["reasoning", "analysis"])
        ],
        "mistral": [("mistral-large-2", "Advanced model", 7, ["reasoning", "code"])],
        "cohere": [("command-r-plus", "Command model", 6, ["general", "reasoning"])],
        "perplexity": [("pplx-70b-online", "Search model", 8, ["search", "general"])]
    }
    
    for provider in available_providers:
        if provider in potential_models and provider not in [m.provider for m in configured_models.values()]:
            for model_name, description, speed, strengths in potential_models[provider]:
                status = "⚠️  Available"
                model_type = "💰 Paid"
                speed_display = "⚡" * (speed // 2)
                strengths_str = ", ".join(strengths)
                
                if show_free:  # Skip paid models when showing only free
                    continue
                    
                table.add_row(
                    provider.title(),
                    model_name,
                    status,
                    model_type,
                    speed_display,
                    strengths_str
                )
    
    console.print(table)
    
    if not show_configured:
        console.print(f"\n💡 Models marked '⚠️  Available' need provider implementation")
        console.print(f"💡 Use [bold]2do add-ai --list-supported[/bold] to see all supported models")

@cli.command()
def github_pro():
    """Toggle GitHub Pro mode for advanced automation"""
    console.print(Panel.fit("🚀 GitHub Pro Mode Management", style="bold blue"))
    
    try:
        # Determine working directory
        working_dir = _get_safe_working_directory()
        
        # Initialize managers
        config_manager = ConfigManager(working_dir)
        if not config_manager.has_api_keys():
            console.print("❌ No API keys configured. Please run '2do setup' first.")
            return
        
        github_integration = GitHubIntegration(config_manager.get_api_key("github"))
        todo_manager = TodoManager(config_manager.config_dir)
        ai_router = AIRouter(config_manager)
        
        # CRITICAL FIX: Initialize all MCP servers with correct project path
        console.print(f"🎯 Initializing all MCP servers for directory: {working_dir}")
        asyncio.run(ai_router.initialize_all_servers(working_dir))
        
        multitasker = Multitasker(ai_router, todo_manager)
        
        # Initialize automation engine
        automation_engine = AutomationEngine(todo_manager, multitasker, github_integration)
        
        # Toggle GitHub Pro mode
        new_status = automation_engine.toggle_github_pro_mode()
        
        if new_status:
            console.print("\n🎯 GitHub Pro Mode Features:")
            console.print("  • Each todo gets its own branch")
            console.print("  • Automatic branch creation and switching")
            console.print("  • Auto-push when todo completes")
            console.print("  • Automatic PR creation per todo")
            console.print("  • Advanced GitHub workflow integration")
        
    except Exception as e:
        console.print(f"❌ Error managing GitHub Pro mode: {e}")

@cli.command()
def run_all():
    """Run multitasking on all pending todos - the ultimate shortcut"""
    console.print(Panel.fit("🔥 RUN ALL MODE", style="bold red"))
    
    try:
        # Determine working directory
        working_dir = _get_safe_working_directory()
        
        # Initialize managers
        config_manager = ConfigManager(working_dir)
        if not config_manager.has_api_keys():
            console.print("❌ No API keys configured. Please run '2do setup' first.")
            return
        
        github_integration = GitHubIntegration(config_manager.get_api_key("github"))
        todo_manager = TodoManager(config_manager.config_dir)
        ai_router = AIRouter(config_manager)
        
        # CRITICAL FIX: Initialize all MCP servers with correct project path
        console.print(f"🎯 Initializing all MCP servers for directory: {working_dir}")
        asyncio.run(ai_router.initialize_all_servers(working_dir))
        
        multitasker = Multitasker(ai_router, todo_manager)
        
        # Initialize automation engine
        automation_engine = AutomationEngine(todo_manager, multitasker, github_integration)
        
        # Run all todos
        # CRITICAL FIX: Use synchronous wrapper to avoid nested event loops
        automation_engine.run_all_todos_sync()
        
    except Exception as e:
        console.print(f"❌ Error in run all mode: {e}")

@cli.command()
@click.argument('request', required=False)
def smart_todo(request):
    """Create a smart todo from natural language (e.g., 'change text in readme.md')"""
    console.print(Panel.fit("🤖 Smart Todo Creation", style="bold green"))
    
    if not request:
        request = Prompt.ask("What would you like to do?", default="")
    
    if not request.strip():
        console.print("❌ Please provide a request.")
        return
    
    try:
        # Determine working directory
        working_dir = _get_safe_working_directory()
        
        # Initialize managers
        config_manager = ConfigManager(working_dir)
        if not config_manager.has_api_keys():
            console.print("❌ No API keys configured. Please run '2do setup' first.")
            return
        
        github_integration = GitHubIntegration(config_manager.get_api_key("github"))
        todo_manager = TodoManager(config_manager.config_dir)
        ai_router = AIRouter(config_manager)
        
        # CRITICAL FIX: Initialize all MCP servers with correct project path
        console.print(f"🎯 Initializing all MCP servers for directory: {working_dir}")
        asyncio.run(ai_router.initialize_all_servers(working_dir))
        
        multitasker = Multitasker(ai_router, todo_manager)
        
        # Initialize automation engine
        automation_engine = AutomationEngine(todo_manager, multitasker, github_integration)
        
        # Handle smart todo creation
        asyncio.run(automation_engine.handle_smart_todo_creation(request))
        
    except Exception as e:
        console.print(f"❌ Error creating smart todo: {e}")

@cli.command()
@click.option('--session-id', help='Specific session ID to show')
def permissions(session_id):
    """Manage file access permissions and sessions"""
    console.print(Panel.fit("🔐 Permission Management", style="bold blue"))
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        
        # Get session permission manager
        session_manager = get_session_permission_manager(config_manager.config_dir)
        
        if session_id:
            # Show specific session
            session = session_manager.get_session(session_id)
            if session:
                perms = session_manager.list_permissions()
                console.print(f"\n📋 Session: {session_id}")
                console.print(f"Created: {time.ctime(perms['created_at'])}")
                console.print(f"Last used: {time.ctime(perms['last_used'])}")
                console.print(f"Allowed paths: {len(perms['allowed_paths'])}")
                console.print(f"Allowed patterns: {len(perms['allowed_patterns'])}")
                
                if perms['allowed_paths']:
                    console.print("\n📁 Allowed Paths:")
                    for path in list(perms['allowed_paths'])[:10]:
                        read_access = "R" if path in perms['read_permissions'] else "-"
                        write_access = "W" if path in perms['write_permissions'] else "-"
                        execute_access = "X" if path in perms['execute_permissions'] else "-"
                        console.print(f"  {read_access}{write_access}{execute_access} {path}")
                
                if perms['allowed_patterns']:
                    console.print("\n🔍 Allowed Patterns:")
                    for pattern in list(perms['allowed_patterns'])[:10]:
                        read_access = "R" if pattern in perms['read_permissions'] else "-"
                        write_access = "W" if pattern in perms['write_permissions'] else "-"
                        execute_access = "X" if pattern in perms['execute_permissions'] else "-"
                        console.print(f"  {read_access}{write_access}{execute_access} {pattern}")
            else:
                console.print(f"❌ Session {session_id} not found")
        else:
            # Show current session and general permissions info
            if session_manager.current_session:
                perms = session_manager.list_permissions()
                console.print(f"\n📋 Current Session: {perms['session_id']}")
                console.print(f"Created: {time.ctime(perms['created_at'])}")
                console.print(f"Last used: {time.ctime(perms['last_used'])}")
                console.print(f"Allowed paths: {len(perms['allowed_paths'])}")
                console.print(f"Allowed patterns: {len(perms['allowed_patterns'])}")
                
                # Show interactive options
                console.print("\n🎯 Permission Actions:")
                console.print("1. Grant project permissions for current directory")
                console.print("2. Clear current session")
                console.print("3. View detailed permissions")
                console.print("4. Exit")
                
                choice = _safe_prompt("Choose action (1-4)", default="4")
                
                if choice == "1":
                    success = session_manager.grant_project_permissions(working_dir)
                    if success:
                        console.print("✅ Project permissions granted")
                    else:
                        console.print("❌ Failed to grant project permissions")
                
                elif choice == "2":
                    session_manager.clear_session()
                    console.print("✅ Session cleared")
                
                elif choice == "3":
                    # Show detailed permissions
                    if perms['allowed_paths']:
                        console.print("\n📁 Detailed Path Permissions:")
                        for path in perms['allowed_paths']:
                            permissions = []
                            if path in perms['read_permissions']:
                                permissions.append("read")
                            if path in perms['write_permissions']:
                                permissions.append("write")
                            if path in perms['execute_permissions']:
                                permissions.append("execute")
                            console.print(f"  {path}: {', '.join(permissions) if permissions else 'none'}")
            else:
                console.print("📝 No active permission session")
                console.print("💡 A session will be created automatically when needed")
        
        # Always show system permission status
        console.print("\n" + "="*50)
        diagnose_permissions()
        
    except Exception as e:
        console.print(f"❌ Error managing permissions: {e}")


@cli.command()
@click.option('--clear-all', is_flag=True, help='Clear all permission sessions')
@click.option('--session-id', help='Clear specific session')
def clear_permissions(clear_all, session_id):
    """Clear permission sessions"""
    console.print(Panel.fit("🗑️ Clear Permissions", style="bold red"))
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        session_manager = get_session_permission_manager(config_manager.config_dir)
        
        if clear_all:
            if _safe_confirm("Clear ALL permission sessions?", default=False):
                # Clear all sessions
                session_count = len(session_manager.sessions)
                session_manager.sessions.clear()
                session_manager.current_session = None
                session_manager._save_sessions()
                console.print(f"✅ Cleared {session_count} permission sessions")
            else:
                console.print("❌ Operation cancelled")
        
        elif session_id:
            session_manager.clear_session(session_id)
            console.print(f"✅ Cleared session: {session_id}")
        
        else:
            # Clear current session
            if session_manager.current_session:
                session_id = session_manager.current_session.session_id
                session_manager.clear_session()
                console.print(f"✅ Cleared current session: {session_id}")
            else:
                console.print("📝 No active session to clear")
        
    except Exception as e:
        console.print(f"❌ Error clearing permissions: {e}")


@cli.command()
@click.argument('path')
@click.option('--read', is_flag=True, help='Grant read permission')
@click.option('--write', is_flag=True, help='Grant write permission')
@click.option('--execute', is_flag=True, help='Grant execute permission')
def grant_permission(path, read, write, execute):
    """Grant specific permissions for a path"""
    console.print(Panel.fit("✅ Grant Permission", style="bold green"))
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        session_manager = get_session_permission_manager(config_manager.config_dir)
        
        if not session_manager.current_session:
            session_manager.create_session()
        
        # Default to read permission if none specified
        if not any([read, write, execute]):
            read = True
        
        # Add the permission
        session_manager.current_session.add_path_permission(
            path, read=read, write=write, execute=execute
        )
        session_manager._save_sessions()
        
        permissions = []
        if read:
            permissions.append("read")
        if write:
            permissions.append("write")
        if execute:
            permissions.append("execute")
        
        console.print(f"✅ Granted {', '.join(permissions)} permission for: {path}")
        
    except Exception as e:
        console.print(f"❌ Error granting permission: {e}")


@cli.command()
@click.argument('files', nargs=-1, required=True)
@click.option('--no-cache', is_flag=True, help='Skip cache for reading')
@click.option('--no-progress', is_flag=True, help='Hide progress indicators')
def fast_read(files, no_cache, no_progress):
    """Fast file reading with caching and progress indicators"""
    console.print(Panel.fit("⚡ Fast File Reading", style="bold green"))
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        session_manager = get_session_permission_manager(config_manager.config_dir)
        file_handler = get_enhanced_file_handler(session_manager)
        
        async def read_files():
            if len(files) == 1:
                # Single file
                content = await file_handler.read_file_fast(
                    files[0], show_progress=not no_progress
                )
                console.print(f"\n📄 Content of {files[0]}:")
                console.print(Panel(content[:1000] + ("..." if len(content) > 1000 else ""), 
                                  title=Path(files[0]).name))
            else:
                # Multiple files
                results = await file_handler.batch_read_files(list(files))
                console.print(f"\n📚 Read {len(results)} files:")
                for file_path, content in results.items():
                    console.print(f"  ✅ {Path(file_path).name}: {len(content)} characters")
        
        asyncio.run(read_files())
        
    except Exception as e:
        console.print(f"❌ Error reading files: {e}")


@cli.command()
@click.argument('file_path')
@click.argument('content')
@click.option('--no-backup', is_flag=True, help='Skip backup creation')
@click.option('--no-progress', is_flag=True, help='Hide progress indicators')
def fast_write(file_path, content, no_backup, no_progress):
    """Fast file writing with backup and progress indicators"""
    console.print(Panel.fit("✍️ Fast File Writing", style="bold green"))
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        session_manager = get_session_permission_manager(config_manager.config_dir)
        file_handler = get_enhanced_file_handler(session_manager)
        
        async def write_file():
            success = await file_handler.write_file_fast(
                file_path, content, 
                show_progress=not no_progress,
                create_backup=not no_backup
            )
            if success:
                console.print(f"✅ Successfully wrote to {file_path}")
            else:
                console.print(f"❌ Failed to write to {file_path}")
        
        asyncio.run(write_file())
        
    except Exception as e:
        console.print(f"❌ Error writing file: {e}")


@cli.command()
def file_stats():
    """Show file operation performance statistics"""
    console.print(Panel.fit("📊 File Performance Statistics", style="bold blue"))
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        session_manager = get_session_permission_manager(config_manager.config_dir)
        file_handler = get_enhanced_file_handler(session_manager)
        
        file_handler.show_performance_report()
        
    except Exception as e:
        console.print(f"❌ Error showing file stats: {e}")


@cli.command()
def clear_cache():
    """Clear file operation cache"""
    console.print(Panel.fit("🗑️ Clear File Cache", style="bold red"))
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        session_manager = get_session_permission_manager(config_manager.config_dir)
        file_handler = get_enhanced_file_handler(session_manager)
        
        file_handler.clear_cache()
        console.print("✅ File cache cleared successfully")
        
    except Exception as e:
        console.print(f"❌ Error clearing cache: {e}")


@cli.command()
def automation_status():
    """Show current automation engine status and features"""
    console.print(Panel.fit("🤖 Automation Engine Status", style="bold cyan"))
    
    try:
        # Determine working directory
        working_dir = _get_safe_working_directory()
        
        # Initialize managers
        config_manager = ConfigManager(working_dir)
        github_integration = GitHubIntegration(config_manager.get_api_key("github")) if config_manager.has_api_keys() else None
        todo_manager = TodoManager(config_manager.config_dir)
        ai_router = AIRouter(config_manager) if config_manager.has_api_keys() else None
        multitasker = Multitasker(ai_router, todo_manager) if ai_router else None
        
        # Initialize automation engine
        automation_engine = AutomationEngine(todo_manager, multitasker, github_integration)
        
        # Get status
        status = automation_engine.get_automation_status()
        
        console.print("\n🎯 Automation Features:")
        console.print(f"  • Smart Todo Parsing: {'✅ Enabled' if status['smart_parsing_enabled'] else '❌ Disabled'}")
        console.print(f"  • Instant Action Prompts: {'✅ Enabled' if status['instant_actions_enabled'] else '❌ Disabled'}")
        console.print(f"  • Run All Shortcut: {'✅ Available' if status['run_all_available'] else '❌ Unavailable'}")
        console.print(f"  • GitHub Pro Mode: {'🚀 Active' if status['github_pro_mode'] else '📴 Inactive'}")
        console.print(f"  • GitHub Integration: {'✅ Connected' if status['github_integration'] else '❌ Not configured'}")
        
        console.print("\n🔧 Available Commands:")
        console.print("  • [bold]2do smart-todo[/bold] - Create smart todos from natural language")
        console.print("  • [bold]2do run-all[/bold] - Run multitasking on all pending todos")
        console.print("  • [bold]2do github-pro[/bold] - Toggle GitHub Pro mode")
        console.print("  • [bold]2do automation-status[/bold] - Show this status")
        
        # Show current todos
        todos = todo_manager.get_todos()
        pending_todos = [todo for todo in todos if todo.status == 'pending']
        
        console.print(f"\n📊 Current Status:")
        console.print(f"  • Total todos: {len(todos)}")
        console.print(f"  • Pending todos: {len(pending_todos)}")
        console.print(f"  • Ready for 'run all': {'✅ Yes' if pending_todos else '❌ No pending todos'}")
        
    except Exception as e:
        console.print(f"❌ Error getting automation status: {e}")


@cli.command()
@click.option('--project', '-p', help='Project path to analyze (default: current directory)')
@click.option('--file', '-f', help='Specific file to analyze')
@click.option('--max-files', default=50, help='Maximum number of files to analyze')
def smart_analyze(project, file, max_files):
    """Smart code analysis for enhanced development intelligence"""
    console.print(Panel.fit("🧠 Smart Code Analysis", style="bold blue"))
    
    try:
        analyzer = SmartCodeAnalyzer()
        
        if file:
            # Analyze single file
            console.print(f"📄 Analyzing file: {file}")
            analysis = analyzer.analyze_file(file)
            
            if not analysis:
                console.print("❌ Could not analyze file (unsupported format or file not found)")
                return
            
            # Display file analysis
            _display_file_analysis(analysis)
            
        else:
            # Analyze project
            project_path = project or os.getcwd()
            console.print(f"📁 Analyzing project: {project_path}")
            
            project_analysis = analyzer.analyze_project(project_path, max_files)
            
            if not project_analysis.file_analyses:
                console.print("❌ No code files found to analyze")
                return
            
            # Display project analysis
            _display_project_analysis(project_analysis)
            
            # Show intelligent suggestions
            suggestions = analyzer.get_intelligent_suggestions(project_analysis)
            if suggestions:
                console.print("\n💡 Intelligent Development Suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    console.print(f"   {i}. {suggestion}")
            
    except Exception as e:
        console.print(f"❌ Error during analysis: {e}")

@cli.command()
@click.option('--project', '-p', help='Project path (default: current directory)')
def tall_stack_check(project):
    """Analyze TALL stack completeness and provide recommendations"""
    console.print(Panel.fit("🏗️ TALL Stack Analysis", style="bold yellow"))
    
    try:
        project_path = project or os.getcwd()
        
        # Initialize tech stack detector
        config_manager = ConfigManager()
        tech_detector = TechStackDetector(config_manager.config_dir)
        
        # Analyze TALL stack completeness
        tall_analysis = tech_detector.analyze_tall_stack_completeness(project_path)
        
        # Display results
        console.print(f"\n📊 TALL Stack Analysis for: {project_path}")
        console.print(f"Completeness Score: {tall_analysis['completeness_score']:.0f}%")
        console.print(f"Is TALL Stack: {'✅ Yes' if tall_analysis['is_tall_stack'] else '❌ No'}")
        
        # Show components
        console.print("\n🔧 TALL Stack Components:")
        components = tall_analysis['components']
        
        tailwind_status = "✅" if components['tailwindcss'] else "❌"
        alpine_status = "✅" if components['alpinejs'] else "❌"
        laravel_status = "✅" if components['laravel'] else "❌"
        livewire_status = "✅" if components['livewire'] else "❌"
        
        console.print(f"   {tailwind_status} TailwindCSS - Utility-first CSS framework")
        console.print(f"   {alpine_status} Alpine.js - Minimal reactive framework")
        console.print(f"   {laravel_status} Laravel - PHP web application framework")
        console.print(f"   {livewire_status} Livewire - Dynamic Laravel components")
        
        # Show detected files
        if any(tall_analysis['detected_files'].values()):
            console.print("\n📄 Detected Files:")
            for component, files in tall_analysis['detected_files'].items():
                if files:
                    console.print(f"   {component.capitalize()}: {', '.join(files[:3])}")
        
        # Show recommendations
        if tall_analysis['recommendations']:
            console.print("\n💡 Recommendations:")
            for i, rec in enumerate(tall_analysis['recommendations'], 1):
                console.print(f"   {i}. {rec}")
        
        # Suggest MCP servers based on analysis
        if tall_analysis['is_tall_stack']:
            console.print("\n🔌 Recommended MCP Servers for TALL Stack:")
            console.print("   • Context7 (Upstash) - Advanced context management")
            console.print("   • PHP MCP Server - PHP code execution")
            console.print("   • Git MCP Server - Version control operations")
            console.print("   • GitHub MCP Server - Repository integration")
            console.print("\n💡 Run '2do mcp' to configure these servers")
        
    except Exception as e:
        console.print(f"❌ Error analyzing TALL stack: {e}")

def _display_file_analysis(analysis):
    """Display analysis results for a single file"""
    console.print(f"\n📄 File: {analysis.file_path}")
    console.print(f"Language: {analysis.language}")
    console.print(f"Complexity Score: {analysis.complexity_score}")
    
    if analysis.functions:
        console.print(f"Functions: {len(analysis.functions)}")
        for func in analysis.functions[:5]:  # Show first 5
            console.print(f"   • {func['name']} (line {func.get('line', 'unknown')})")
    
    if analysis.classes:
        console.print(f"Classes: {len(analysis.classes)}")
        for cls in analysis.classes[:5]:  # Show first 5
            console.print(f"   • {cls['name']} (line {cls.get('line', 'unknown')})")
    
    if analysis.tech_stack_hints:
        console.print(f"Tech Stack Hints: {', '.join(analysis.tech_stack_hints)}")
    
    if analysis.suggestions:
        console.print("Suggestions:")
        for sugg in analysis.suggestions:
            console.print(f"   • {sugg}")

def _display_project_analysis(analysis):
    """Display analysis results for an entire project"""
    console.print(f"\n📁 Project: {analysis.project_path}")
    console.print(f"Files Analyzed: {len(analysis.file_analyses)}")
    console.print(f"Overall Complexity: {analysis.overall_complexity}")
    
    if analysis.tech_stack:
        console.print(f"Detected Technologies: {', '.join(analysis.tech_stack)}")
    
    if analysis.architecture_patterns:
        console.print(f"Architecture Patterns: {', '.join(analysis.architecture_patterns)}")
    
    # Show file breakdown by language
    languages = {}
    for file_analysis in analysis.file_analyses:
        lang = file_analysis.language
        languages[lang] = languages.get(lang, 0) + 1
    
    if languages:
        console.print("File Types:")
        for lang, count in languages.items():
            console.print(f"   • {lang}: {count} files")
    
    if analysis.recommendations:
        console.print("Project Recommendations:")
        for rec in analysis.recommendations:
            console.print(f"   • {rec}")

def _generate_smart_todos(project_analysis):
    """Generate intelligent todos based on project analysis"""
    todos = []
    
    # High complexity files need refactoring
    for file_analysis in project_analysis.file_analyses:
        if file_analysis.complexity_score > 30:
            todos.append({
                'content': f"Refactor high-complexity file: {Path(file_analysis.file_path).name} (complexity: {file_analysis.complexity_score})",
                'priority': 'high',
                'type': 'code'
            })
    
    # Missing TALL stack components
    tech_stack = set(project_analysis.tech_stack)
    if 'laravel' in tech_stack:
        if 'livewire' not in tech_stack:
            todos.append({
                'content': "Consider adding Livewire for reactive PHP components without complex JavaScript",
                'priority': 'medium',
                'type': 'code'
            })
        
        if 'tailwind' not in tech_stack:
            todos.append({
                'content': "Add TailwindCSS for utility-first styling approach",
                'priority': 'medium',
                'type': 'code'
            })
        
        if 'alpine' not in tech_stack:
            todos.append({
                'content': "Add Alpine.js for lightweight reactive frontend components",
                'priority': 'low',
                'type': 'code'
            })
    
    # Large functions/classes need attention
    for file_analysis in project_analysis.file_analyses:
        large_functions = [f for f in file_analysis.functions if f.get('complexity', 0) > 10]
        if large_functions:
            for func in large_functions[:2]:  # Limit to 2 per file
                todos.append({
                    'content': f"Refactor complex function: {func['name']} in {Path(file_analysis.file_path).name}",
                    'priority': 'medium',
                    'type': 'code'
                })
    
    # Add testing suggestions
    if not any('test' in fa.file_path.lower() for fa in project_analysis.file_analyses):
        todos.append({
            'content': "Add unit tests for better code quality and maintainability",
            'priority': 'high',
            'type': 'code'
        })
    
    # Documentation suggestions
    if project_analysis.overall_complexity == 'high' and len(project_analysis.file_analyses) > 10:
        todos.append({
            'content': "Create comprehensive project documentation due to high complexity",
            'priority': 'medium',
            'type': 'text'
        })
    
    return todos[:10]  # Limit to 10 todos

@cli.command()
@click.option('--project', '-p', help='Project path (default: current directory)')
@click.option('--type', 'scaffold_type', help='Scaffold type: livewire, controller, model, crud')
@click.argument('name', required=False)
def scaffold(project, scaffold_type, name):
    """Intelligent TALL Stack scaffolding and code generation"""
    console.print(Panel.fit("🏗️ TALL Stack Scaffolding", style="bold blue"))
    
    try:
        project_path = project or os.getcwd()
        
        # Initialize components
        config_manager = ConfigManager()
        todo_manager = TodoManager(config_manager.config_dir)
        tech_detector = TechStackDetector(config_manager.config_dir)
        automation_engine = EnhancedAutomationEngine(todo_manager, None, None, tech_detector)
        
        # If no name provided, ask for user input
        if not name:
            user_input = Prompt.ask("What would you like to scaffold? (e.g., 'create Livewire component UserProfile')")
            
            # Try to detect scaffolding from natural language
            scaffold_info = automation_engine.detect_scaffolding_opportunity(user_input, project_path)
            
            if scaffold_info:
                console.print(f"🎯 Detected request: {scaffold_info['scaffold_info'].description}")
                console.print(f"📝 Component name: {scaffold_info['name']}")
                
                if Confirm.ask("Proceed with scaffolding?", default=True):
                    success = automation_engine.execute_scaffolding(scaffold_info, project_path)
                    if success:
                        console.print("✅ Scaffolding completed successfully!")
                    else:
                        console.print("❌ Scaffolding failed!")
                return
            else:
                console.print("❌ Could not understand scaffolding request. Try being more specific.")
                return
        
        # Handle specific scaffold type and name
        if scaffold_type and name:
            # Map common scaffold types
            scaffold_map = {
                'livewire': 'laravel_livewire_component',
                'component': 'laravel_livewire_component',
                'controller': 'laravel_controller',
                'model': 'laravel_model',
                'crud': 'full_tall_crud'
            }
            
            template_key = scaffold_map.get(scaffold_type.lower())
            if template_key and template_key in automation_engine.scaffold_templates:
                scaffold_info = {
                    'template': template_key,
                    'name': name.capitalize(),
                    'scaffold_info': automation_engine.scaffold_templates[template_key],
                    'confidence': 1.0
                }
                
                console.print(f"🏗️ Scaffolding {scaffold_info['scaffold_info'].description}")
                success = automation_engine.execute_scaffolding(scaffold_info, project_path)
                
                if success:
                    console.print("✅ Scaffolding completed successfully!")
                else:
                    console.print("❌ Scaffolding failed!")
            else:
                console.print(f"❌ Unknown scaffold type: {scaffold_type}")
                console.print("Available types: livewire, controller, model, crud")
        else:
            console.print("❌ Please provide both --type and name, or use natural language")
    
    except Exception as e:
        console.print(f"❌ Error during scaffolding: {e}")

@cli.command()
@click.option('--project', '-p', help='Project path (default: current directory)')
@click.option('--generate', is_flag=True, help='Generate test files automatically')
def generate_tests(project, generate):
    """Generate intelligent test suggestions and files"""
    console.print(Panel.fit("🧪 Test Generation Assistant", style="bold green"))
    
    try:
        project_path = project or os.getcwd()
        
        # Initialize components
        config_manager = ConfigManager()
        todo_manager = TodoManager(config_manager.config_dir)
        tech_detector = TechStackDetector(config_manager.config_dir)
        automation_engine = EnhancedAutomationEngine(todo_manager, None, None, tech_detector)
        
        console.print(f"🔍 Analyzing project for test opportunities: {project_path}")
        
        # Generate test suggestions
        test_suggestions = automation_engine.generate_tests_for_project(project_path)
        
        if not test_suggestions:
            console.print("✅ No immediate test files needed - project looks well tested!")
            return
        
        console.print(f"\n📋 Found {len(test_suggestions)} test opportunities:")
        
        tests_created = 0
        for i, test_info in enumerate(test_suggestions, 1):
            console.print(f"\n{i}. {test_info['name']}")
            console.print(f"   Priority: {test_info['priority']}")
            console.print(f"   Description: {test_info['description']}")
            
            if generate:
                # Auto-generate
                should_create = True
            else:
                # Ask user
                should_create = Confirm.ask(f"   Create this test?", default=True)
            
            if should_create:
                if test_info['type'] == 'setup_js_testing':
                    # Special case for JS testing setup
                    console.print("   🔧 Setting up JavaScript testing framework...")
                    console.print("   💡 Consider running: npm install --save-dev jest @testing-library/jest-dom")
                elif test_info.get('file_path'):
                    # Create the test file
                    test_file_path = Path(test_info['file_path'])
                    test_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Generate test content based on template
                    test_content = automation_engine._generate_file_content(
                        test_info.get('template', 'basic_test'),
                        Path(test_info['file_path']).stem.replace('Test', '')
                    )
                    
                    with open(test_file_path, 'w') as f:
                        f.write(test_content)
                    
                    console.print(f"   ✅ Created: {test_info['file_path']}")
                    tests_created += 1
                
                # Also create a todo for manual completion
                todo_id = todo_manager.add_todo(
                    content=test_info['description'],
                    todo_type="code",
                    priority=test_info['priority']
                )
                console.print(f"   📝 Created todo #{todo_id}")
        
        if tests_created > 0:
            console.print(f"\n🎉 Created {tests_created} test files!")
            console.print("💡 Remember to implement the actual test logic in the generated files.")
        
    except Exception as e:
        console.print(f"❌ Error generating tests: {e}")

@cli.command()
@click.option('--project', '-p', help='Project path (default: current directory)')
@click.option('--setup', is_flag=True, help='Setup CI/CD automatically')
def cicd_assistant(project, setup):
    """Setup CI/CD pipelines for TALL Stack projects"""
    console.print(Panel.fit("🚀 CI/CD Pipeline Assistant", style="bold yellow"))
    
    try:
        project_path = project or os.getcwd()
        
        # Initialize components
        config_manager = ConfigManager()
        todo_manager = TodoManager(config_manager.config_dir)
        tech_detector = TechStackDetector(config_manager.config_dir)
        automation_engine = EnhancedAutomationEngine(todo_manager, None, None, tech_detector)
        
        console.print(f"🔍 Analyzing project for CI/CD opportunities: {project_path}")
        
        # Generate CI/CD suggestions
        cicd_suggestions = automation_engine.generate_ci_cd_suggestions(project_path)
        
        if not cicd_suggestions:
            console.print("✅ CI/CD pipeline appears to be well configured!")
            return
        
        console.print(f"\n📋 Found {len(cicd_suggestions)} CI/CD improvements:")
        
        pipelines_created = 0
        for i, suggestion in enumerate(cicd_suggestions, 1):
            console.print(f"\n{i}. {suggestion['name']}")
            console.print(f"   Priority: {suggestion['priority']}")
            console.print(f"   Description: {suggestion['description']}")
            
            if setup:
                # Auto-setup
                should_create = True
            else:
                # Ask user
                should_create = Confirm.ask(f"   Setup this pipeline?", default=True)
            
            if should_create:
                if suggestion['type'] == 'setup_github_actions':
                    # Create .github/workflows directory
                    workflows_dir = Path(project_path) / ".github" / "workflows"
                    workflows_dir.mkdir(parents=True, exist_ok=True)
                    console.print(f"   ✅ Created: .github/workflows/")
                    pipelines_created += 1
                
                elif suggestion.get('template'):
                    # Create specific pipeline file
                    if suggestion['type'] == 'laravel_ci':
                        file_path = Path(project_path) / ".github" / "workflows" / "laravel.yml"
                    elif suggestion['type'] == 'node_ci':
                        file_path = Path(project_path) / ".github" / "workflows" / "node.yml"
                    else:
                        file_path = Path(project_path) / ".github" / "workflows" / f"{suggestion['type']}.yml"
                    
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Generate pipeline content
                    pipeline_content = automation_engine._generate_file_content(
                        suggestion['template'],
                        suggestion['name']
                    )
                    
                    with open(file_path, 'w') as f:
                        f.write(pipeline_content)
                    
                    console.print(f"   ✅ Created: {file_path}")
                    pipelines_created += 1
                
                # Create todo for manual configuration
                todo_id = todo_manager.add_todo(
                    content=f"Configure and test {suggestion['name']}",
                    todo_type="code",
                    priority=suggestion['priority']
                )
                console.print(f"   📝 Created todo #{todo_id}")
        
        if pipelines_created > 0:
            console.print(f"\n🎉 Created {pipelines_created} CI/CD pipelines!")
            console.print("💡 Remember to configure secrets and environment variables in GitHub.")
            console.print("🔗 Visit your repository settings to add required secrets like:")
            console.print("   - Database credentials")
            console.print("   - Deployment keys")
            console.print("   - API tokens")
        
    except Exception as e:
        console.print(f"❌ Error setting up CI/CD: {e}")

@cli.command()
@click.argument('description')
@click.option('--project', '-p', help='Project path (default: current directory)')
def smart_scaffold(description, project):
    """Natural language scaffolding - describe what you want to build"""
    console.print(Panel.fit("🤖 AI-Powered Smart Scaffolding", style="bold magenta"))
    
    try:
        project_path = project or os.getcwd()
        
        # Initialize components
        config_manager = ConfigManager()
        todo_manager = TodoManager(config_manager.config_dir)
        tech_detector = TechStackDetector(config_manager.config_dir)
        automation_engine = EnhancedAutomationEngine(todo_manager, None, None, tech_detector)
        
        console.print(f"🧠 Analyzing request: '{description}'")
        
        # Try to detect what the user wants to scaffold
        scaffold_info = automation_engine.detect_scaffolding_opportunity(description, project_path)
        
        if scaffold_info:
            template_info = scaffold_info['scaffold_info']
            console.print(f"\n🎯 Detected scaffolding opportunity:")
            console.print(f"   Template: {template_info.name}")
            console.print(f"   Description: {template_info.description}")
            console.print(f"   Component name: {scaffold_info['name']}")
            console.print(f"   Confidence: {scaffold_info['confidence']:.0%}")
            
            if Confirm.ask("\nProceed with scaffolding?", default=True):
                success = automation_engine.execute_scaffolding(scaffold_info, project_path)
                
                if success:
                    console.print("✅ Smart scaffolding completed successfully!")
                    
                    # Create follow-up todos for manual steps
                    todo_manager.add_todo(
                        content=f"Review and customize generated {scaffold_info['name']} component",
                        todo_type="code",
                        priority="medium"
                    )
                    
                    console.print("📝 Created follow-up todo for code review and customization")
                else:
                    console.print("❌ Scaffolding failed!")
        else:
            console.print("❌ Could not understand the scaffolding request.")
            console.print("💡 Try being more specific, for example:")
            console.print("   • 'create Livewire component UserProfile'")
            console.print("   • 'generate Laravel controller ProductController'")
            console.print("   • 'scaffold full CRUD for Product'")
            console.print("   • 'make TailwindCSS component DropdownMenu'")
    
    except Exception as e:
        console.print(f"❌ Error in smart scaffolding: {e}")
@click.option('--daemon', '-d', is_flag=True, help='Run scheduler in daemon mode')
@click.option('--stop', is_flag=True, help='Stop running scheduler daemon')
def scheduler(daemon, stop):
    """Start the 2DO task scheduler"""
    console.print(Panel.fit("📅 2DO Task Scheduler", style="bold cyan"))
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        scheduler_instance = Scheduler(config_manager)
        
        if stop:
            scheduler_instance.stop()
            return
            
        if daemon:
            console.print("🔄 Starting scheduler in daemon mode...")
            console.print("💡 Use 'Ctrl+C' to stop the scheduler")
            
            scheduler_instance.start()
            
            try:
                # Keep the scheduler running
                import signal
                import time
                
                def signal_handler(sig, frame):
                    console.print("\n🛑 Stopping scheduler...")
                    scheduler_instance.stop()
                    exit(0)
                    
                signal.signal(signal.SIGINT, signal_handler)
                signal.signal(signal.SIGTERM, signal_handler)
                
                while True:
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                scheduler_instance.stop()
        else:
            # Show scheduler status and schedules
            status = scheduler_instance.get_status()
            
            console.print(f"\n📊 Scheduler Status:")
            console.print(f"  • Running: {'✅ Yes' if status['running'] else '❌ No'}")
            console.print(f"  • Total schedules: {status['schedule_count']}")
            console.print(f"  • Enabled schedules: {status['enabled_schedules']}")
            
            if status['schedule_count'] > 0:
                scheduler_instance.load_schedules()
                scheduler_instance.list_schedules()
            else:
                console.print("\n💡 No schedules configured. Use 'schedule add' to create your first schedule.")
                
            console.print("\n🔧 Available scheduler commands:")
            console.print("  • [bold]2do scheduler --daemon[/bold] - Start scheduler daemon")
            console.print("  • [bold]2do schedule add[/bold] - Add new schedule")
            console.print("  • [bold]2do schedule list[/bold] - List all schedules")
            console.print("  • [bold]2do schedule remove[/bold] - Remove a schedule")
            console.print("  • [bold]2do schedule trigger[/bold] - Manually trigger a schedule")
            
    except Exception as e:
        console.print(f"❌ Error with scheduler: {e}")


@cli.group()
def schedule():
    """Manage scheduled tasks"""
    pass


@schedule.command()
@click.option('--name', prompt='Schedule name', help='Name for the schedule')
@click.option('--schedule', prompt='Schedule (cron expression)', help='Cron expression (e.g., "0 7 * * 1-5" for 7 AM weekdays)')
@click.option('--description', prompt='Description', help='Description of what this schedule does')
def add(name, schedule, description):
    """Add a new schedule interactively"""
    console.print(Panel.fit("➕ Add New Schedule", style="bold green"))
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        scheduler_instance = Scheduler(config_manager)
        
        # Create schedule configuration
        schedule_config = {
            'name': name,
            'description': description,
            'schedule': schedule,
            'enabled': True,
            'tasks': []
        }
        
        # Interactive task configuration
        console.print("\n📋 Now let's add tasks to your schedule:")
        console.print("Available task types:")
        console.print("  1. github_sync - Sync GitHub issues and create todos")
        console.print("  2. multitask - Run multitasking on pending todos")
        console.print("  3. add_todo - Add a new todo")
        console.print("  4. create_branch - Create git branch for issue")
        console.print("  5. github_pr - Create GitHub pull request")
        console.print("  6. custom_command - Run custom shell command")
        console.print("  7. ai_prompt - Execute AI prompt")
        
        while True:
            add_task = _safe_confirm("\nAdd a task to this schedule?", default=True)
            if not add_task:
                break
                
            task_type = _safe_prompt("Task type (1-7)", default="1")
            task_map = {
                '1': 'github_sync',
                '2': 'multitask', 
                '3': 'add_todo',
                '4': 'create_branch',
                '5': 'github_pr',
                '6': 'custom_command',
                '7': 'ai_prompt'
            }
            
            task_type_name = task_map.get(task_type, 'github_sync')
            task_config = _get_task_config(task_type_name)
            
            schedule_config['tasks'].append({
                'type': task_type_name,
                'config': task_config
            })
            
            console.print(f"✅ Added {task_type_name} task")
        
        if not schedule_config['tasks']:
            console.print("❌ At least one task is required for a schedule")
            return
            
        # Add the schedule
        if scheduler_instance.add_schedule(schedule_config):
            console.print(f"✅ Successfully created schedule: {name}")
            console.print(f"📅 Next run: Check with '2do scheduler' command")
        else:
            console.print("❌ Failed to create schedule")
            
    except Exception as e:
        console.print(f"❌ Error adding schedule: {e}")


@schedule.command()
def list():
    """List all schedules"""
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        scheduler_instance = Scheduler(config_manager)
        
        scheduler_instance.load_schedules()
        scheduler_instance.list_schedules()
        
    except Exception as e:
        console.print(f"❌ Error listing schedules: {e}")


@schedule.command()
@click.argument('name')
def remove(name):
    """Remove a schedule"""
    console.print(f"🗑️ Removing schedule: {name}")
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        scheduler_instance = Scheduler(config_manager)
        
        scheduler_instance.load_schedules()
        
        if _safe_confirm(f"Are you sure you want to remove '{name}'?", default=False):
            if scheduler_instance.remove_schedule(name):
                console.print(f"✅ Successfully removed schedule: {name}")
            else:
                console.print(f"❌ Failed to remove schedule: {name}")
        else:
            console.print("❌ Cancelled")
            
    except Exception as e:
        console.print(f"❌ Error removing schedule: {e}")


@schedule.command()
@click.argument('name')
def trigger(name):
    """Manually trigger a schedule"""
    console.print(f"🔧 Manually triggering schedule: {name}")
    
    try:
        working_dir = _get_safe_working_directory()
        config_manager = ConfigManager(working_dir)
        scheduler_instance = Scheduler(config_manager)
        
        scheduler_instance.load_schedules()
        scheduler_instance.trigger_schedule(name)
        
    except Exception as e:
        console.print(f"❌ Error triggering schedule: {e}")


def _get_task_config(task_type):
    """Get configuration for a specific task type"""
    config = {}
    
    if task_type == 'github_sync':
        config['action'] = 'sync_issues'
        config['create_todos'] = _safe_confirm("Create todos from synced issues?", default=True)
        
    elif task_type == 'multitask':
        priority_filter = _safe_prompt("Priority filter (high/medium/low or empty for all)", default="")
        if priority_filter:
            config['filter'] = f"priority:{priority_filter}"
        config['max_parallel'] = int(_safe_prompt("Max parallel tasks", default="3"))
        
    elif task_type == 'add_todo':
        config['content'] = _safe_prompt("Todo content")
        config['type'] = _safe_prompt("Todo type (code/text/image/general)", default="general")
        config['priority'] = _safe_prompt("Priority (high/medium/low)", default="medium")
        
    elif task_type == 'create_branch':
        config['issue_number'] = _safe_prompt("GitHub issue number (or leave empty for latest)")
        config['branch_prefix'] = _safe_prompt("Branch prefix", default="issue")
        
    elif task_type == 'github_pr':
        config['title'] = _safe_prompt("PR title")
        config['body'] = _safe_prompt("PR body", default="")
        config['branch'] = _safe_prompt("Source branch")
        
    elif task_type == 'custom_command':
        config['command'] = _safe_prompt("Shell command to execute")
        config['working_dir'] = _safe_prompt("Working directory", default=_get_safe_working_directory())
        
    elif task_type == 'ai_prompt':
        config['prompt'] = _safe_prompt("AI prompt")
        config['model'] = _safe_prompt("Preferred model (or 'auto')", default="auto")
        
    return config

def main():
    """Main entry point"""
    cli()

if __name__ == "__main__":
    main()