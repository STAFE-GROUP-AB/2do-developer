#!/usr/bin/env python3
"""
Interactive setup guidance system for 2DO
Helps users through the setup process and verifies configuration
"""

import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from .config import ConfigManager
from .ai_router import AIRouter
from .github_integration import GitHubIntegration


class SetupGuide:
    """Interactive setup guidance system"""
    
    def __init__(self, console=None):
        self.console = console or Console()
        self.config = None
    
    def run_complete_setup_check(self, project_dir=None):
        """Run a complete setup verification and guide user through missing components"""
        self.console.print(Panel.fit("🔍 2DO Setup Verification", style="bold blue"))
        
        # Initialize config
        self.config = ConfigManager(project_dir)
        
        # Check setup status
        setup_status = self.get_comprehensive_setup_status()
        
        # Display current status
        self.display_setup_status(setup_status)
        
        # Guide through missing components
        if not setup_status["is_fully_configured"]:
            self.console.print("\n🚧 Some components need configuration. Let's fix that!")
            self.guide_missing_components(setup_status)
        else:
            self.console.print("\n✅ Great! Your 2DO setup is complete and ready to use!")
            self.run_connectivity_tests()
        
        # Final verification
        self.console.print("\n" + "="*60)
        final_status = self.get_comprehensive_setup_status()
        self.display_final_status(final_status)
        
        return final_status
    
    def get_comprehensive_setup_status(self):
        """Get comprehensive setup status"""
        status = {
            "config_file_exists": self.config.config_file.exists(),
            "config_directory_exists": self.config.config_dir.exists(),
            "is_local_project": self.config.is_local_project,
            "openai_configured": bool(self.config.get_api_key("openai")),
            "anthropic_configured": bool(self.config.get_api_key("anthropic")),
            "google_configured": bool(self.config.get_api_key("google")),
            "github_configured": bool(self.config.get_api_key("github")),
            "has_any_api_keys": self.config.has_api_keys(),
            "memory_enabled": self.config.get_preference("memory_enabled", True),
            "max_parallel_tasks": self.config.get_preference("max_parallel_tasks", 5)
        }
        
        # Calculate completion - Google is optional, not required
        required_components = ["openai_configured", "anthropic_configured", "github_configured"]
        configured_count = sum(1 for comp in required_components if status[comp])
        status["configuration_percentage"] = (configured_count / len(required_components)) * 100
        status["is_fully_configured"] = configured_count == len(required_components)
        
        return status
    
    def display_setup_status(self, status):
        """Display current setup status in a formatted table"""
        table = Table(title="2DO Setup Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        # Configuration basics
        config_status = "✅ Exists" if status["config_file_exists"] else "❌ Missing"
        config_details = f"Located at: {self.config.config_file}"
        if status["is_local_project"]:
            config_details += " (Local 2DO folder)"
        table.add_row("Configuration File", config_status, config_details)
        
        # API Keys
        openai_status = "✅ Configured" if status["openai_configured"] else "❌ Not configured"
        table.add_row("OpenAI API Key", openai_status, "Required for GPT models")
        
        anthropic_status = "✅ Configured" if status["anthropic_configured"] else "❌ Not configured"
        table.add_row("Anthropic API Key", anthropic_status, "Required for Claude models")
        
        google_status = "✅ Configured" if status["google_configured"] else "⚠️ Optional"
        table.add_row("Google AI API Key", google_status, "Optional for Gemini models")
        
        github_status = "✅ Configured" if status["github_configured"] else "❌ Not configured"
        table.add_row("GitHub Token", github_status, "Required for GitHub integration")
        
        # Preferences
        memory_status = "✅ Enabled" if status["memory_enabled"] else "⚠️ Disabled"
        table.add_row("Memory System", memory_status, "Tech stack memory files")
        
        parallel_status = f"✅ {status['max_parallel_tasks']} tasks"
        table.add_row("Parallel Tasks", parallel_status, "Max concurrent processing")
        
        self.console.print(table)
        
        # Overall progress
        percentage = status["configuration_percentage"]
        if percentage == 100:
            progress_text = f"🎉 Setup Complete ({percentage:.0f}%)"
            progress_style = "bold green"
        elif percentage >= 50:
            progress_text = f"🔧 Partially Configured ({percentage:.0f}%)"
            progress_style = "bold yellow"
        else:
            progress_text = f"🚧 Needs Configuration ({percentage:.0f}%)"
            progress_style = "bold red"
        
        self.console.print(f"\n{progress_text}", style=progress_style)
    
    def guide_missing_components(self, status):
        """Guide user through configuring missing components"""
        missing_components = []
        
        if not status["openai_configured"]:
            missing_components.append(("OpenAI API Key", self.configure_openai))
        if not status["anthropic_configured"]:
            missing_components.append(("Anthropic API Key", self.configure_anthropic))
        if not status["github_configured"]:
            missing_components.append(("GitHub Token", self.configure_github))
        
        self.console.print(f"\n📝 Found {len(missing_components)} required components to configure:")
        
        for i, (component_name, _) in enumerate(missing_components, 1):
            self.console.print(f"   {i}. {component_name}")
        
        # Offer optional Google configuration
        if not status["google_configured"]:
            self.console.print(f"\n🔧 Optional: Google AI API Key (for Gemini models)")
        
        if Confirm.ask("\n🚀 Would you like to configure these now?"):
            for component_name, configure_func in missing_components:
                self.console.print(f"\n🔧 Configuring {component_name}...")
                configure_func()
            
            # Optionally configure Google
            if not status["google_configured"] and Confirm.ask("\n🤖 Would you like to configure Google AI (optional)?"):
                self.configure_google()
        else:
            self.console.print("\n💡 You can run '2do setup' anytime to configure these components.")
            self.display_manual_setup_instructions(missing_components)
    
    def configure_openai(self):
        """Guide OpenAI API key configuration"""
        self.console.print(Panel(
            "To use OpenAI models (GPT-3.5, GPT-4), you need an API key:\n\n"
            "1. Visit: https://platform.openai.com/api-keys\n"
            "2. Sign in or create an account\n"
            "3. Click 'Create new secret key'\n"
            "4. Copy the key (starts with 'sk-')",
            title="🤖 OpenAI Setup",
            style="blue"
        ))
        
        if Confirm.ask("Do you want to configure OpenAI now?"):
            api_key = Prompt.ask("Enter your OpenAI API key", password=True)
            if api_key and api_key.strip():
                self.config.set_api_key("openai", api_key.strip())
                self.console.print("✅ OpenAI API key configured!")
            else:
                self.console.print("⚠️ No API key entered. Skipping OpenAI configuration.")
    
    def configure_anthropic(self):
        """Guide Anthropic API key configuration"""
        self.console.print(Panel(
            "To use Anthropic models (Claude), you need an API key:\n\n"
            "1. Visit: https://console.anthropic.com/\n"
            "2. Sign in or create an account\n"
            "3. Go to API Keys section\n"
            "4. Create a new API key\n"
            "5. Copy the key",
            title="🧠 Anthropic Setup",
            style="purple"
        ))
        
        if Confirm.ask("Do you want to configure Anthropic now?"):
            api_key = Prompt.ask("Enter your Anthropic API key", password=True)
            if api_key and api_key.strip():
                self.config.set_api_key("anthropic", api_key.strip())
                self.console.print("✅ Anthropic API key configured!")
            else:
                self.console.print("⚠️ No API key entered. Skipping Anthropic configuration.")
    
    def configure_google(self):
        """Guide Google AI API key configuration"""
        self.console.print(Panel(
            "To use Google Gemini models, you need an API key:\n\n"
            "1. Visit: https://aistudio.google.com/app/apikey\n"
            "2. Sign in with your Google account\n"
            "3. Click 'Create API key'\n"
            "4. Copy the generated API key\n\n"
            "Note: Google AI Studio may have usage limits.",
            title="🔮 Google AI Setup",
            style="cyan"
        ))
        
        if Confirm.ask("Do you want to configure Google AI now?"):
            api_key = Prompt.ask("Enter your Google AI API key", password=True)
            if api_key and api_key.strip():
                self.config.set_api_key("google", api_key.strip())
                self.console.print("✅ Google AI API key configured!")
            else:
                self.console.print("⚠️ No API key entered. Skipping Google AI configuration.")
    
    def configure_github(self):
        """Guide GitHub token configuration"""
        self.console.print(Panel(
            "To use GitHub integration, you need a Personal Access Token:\n\n"
            "1. Visit: https://github.com/settings/tokens\n"
            "2. Click 'Generate new token (classic)'\n"
            "3. Select scopes: repo, issues, pull_requests\n"
            "4. Generate and copy the token (starts with 'ghp_')",
            title="🐙 GitHub Setup",
            style="green"
        ))
        
        if Confirm.ask("Do you want to configure GitHub now?"):
            token = Prompt.ask("Enter your GitHub Personal Access Token", password=True)
            if token and token.strip():
                self.config.set_api_key("github", token.strip())
                self.console.print("✅ GitHub token configured!")
            else:
                self.console.print("⚠️ No token entered. Skipping GitHub configuration.")
    
    def display_manual_setup_instructions(self, missing_components):
        """Display manual setup instructions for missing components"""
        self.console.print(Panel(
            "📖 Manual Setup Instructions:\n\n"
            "You can configure these components later by:\n"
            "1. Running: 2do setup\n"
            "2. Or manually editing the config file:\n"
            f"   {self.config.config_file}",
            title="Manual Configuration",
            style="cyan"
        ))
    
    def run_connectivity_tests(self):
        """Run connectivity tests for configured services"""
        self.console.print("\n🔌 Testing connectivity to configured services...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Test OpenAI
            if self.config.get_api_key("openai"):
                task = progress.add_task("Testing OpenAI connection...", total=None)
                try:
                    # Note: Actual API test would require real API call
                    # For now, just verify the key format
                    api_key = self.config.get_api_key("openai")
                    if api_key.startswith("sk-"):
                        progress.update(task, description="✅ OpenAI: API key format valid")
                    else:
                        progress.update(task, description="⚠️ OpenAI: API key format unusual")
                except Exception as e:
                    progress.update(task, description=f"❌ OpenAI: Error - {e}")
                progress.remove_task(task)
            
            # Test Anthropic
            if self.config.get_api_key("anthropic"):
                task = progress.add_task("Testing Anthropic connection...", total=None)
                try:
                    # Note: Actual API test would require real API call
                    api_key = self.config.get_api_key("anthropic")
                    if len(api_key) > 20:  # Basic validation
                        progress.update(task, description="✅ Anthropic: API key configured")
                    else:
                        progress.update(task, description="⚠️ Anthropic: API key seems short")
                except Exception as e:
                    progress.update(task, description=f"❌ Anthropic: Error - {e}")
                progress.remove_task(task)
            
            # Test GitHub
            if self.config.get_api_key("github"):
                task = progress.add_task("Testing GitHub connection...", total=None)
                try:
                    github_integration = GitHubIntegration(self.config.get_api_key("github"))
                    if github_integration.github:
                        progress.update(task, description="✅ GitHub: Token configured")
                    else:
                        progress.update(task, description="⚠️ GitHub: Token validation failed")
                except Exception as e:
                    progress.update(task, description=f"❌ GitHub: Error - {e}")
                progress.remove_task(task)
    
    def display_final_status(self, status):
        """Display final setup status and next steps"""
        if status["is_fully_configured"]:
            self.console.print(Panel(
                "🎉 Congratulations! Your 2DO setup is complete!\n\n"
                "You can now:\n"
                "• Run '2do start' to begin an interactive session\n"
                "• Create and manage todos\n"
                "• Use AI-powered multitasking\n"
                "• Work with GitHub issues\n"
                "• Analyze tech stacks automatically\n\n"
                "🤖 AI Model Management:\n"
                "• Run '2do ai-list' to see available AI models\n"
                "• Run '2do add-ai' to add more AI providers\n"
                "• Only free models are enabled by default",
                title="Setup Complete!",
                style="bold green"
            ))
        else:
            configured_count = sum(1 for key in ["openai_configured", "anthropic_configured", "github_configured"] 
                                 if status[key])
            self.console.print(Panel(
                f"⚠️ Setup is {status['configuration_percentage']:.0f}% complete.\n\n"
                f"You have {configured_count}/3 services configured.\n"
                "You can still use 2DO with the configured services.\n\n"
                "To complete setup, run: 2do setup\n"
                "To add more AI models, run: 2do add-ai",
                title="Partial Setup",
                style="yellow"
            ))
    
    def verify_project_setup(self, project_dir):
        """Verify setup for a specific project directory"""
        self.console.print(f"🔍 Verifying 2DO setup for project: {project_dir}")
        
        # Check if it's a git repository
        git_dir = Path(project_dir) / ".git"
        if git_dir.exists():
            self.console.print("✅ Git repository detected")
            
            # Check for local 2DO folder
            local_2do_dir = Path(project_dir) / "2DO"
            if local_2do_dir.exists():
                self.console.print("✅ Local 2DO folder found")
            else:
                self.console.print("📁 Local 2DO folder will be created automatically")
        else:
            self.console.print("ℹ️ Not a git repository - will use global configuration")
        
        # Run standard setup check
        return self.run_complete_setup_check(project_dir)


def main():
    """Main function for running setup guide standalone"""
    console = Console()
    guide = SetupGuide(console)
    
    console.print("🚀 Welcome to the 2DO Setup Guide!")
    
    # Check if we're in a project directory
    current_dir = os.getcwd()
    if Path(current_dir, ".git").exists():
        if Confirm.ask(f"Run setup verification for current project ({current_dir})?"):
            guide.verify_project_setup(current_dir)
        else:
            guide.run_complete_setup_check()
    else:
        guide.run_complete_setup_check()


if __name__ == "__main__":
    main()