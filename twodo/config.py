"""
Configuration management for 2DO
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv
from .permission_manager import PermissionManager

class ConfigManager:
    """Manages configuration and API keys for AI models"""
    
    def __init__(self, project_dir=None, suppress_prompts=False):
        # If project_dir is provided and is a git repo, use local 2DO folder
        if project_dir and self._is_git_repo(project_dir):
            # Check for both '2DO' and '2dos' directories
            project_path = Path(project_dir)
            if (project_path / "2dos").exists():
                self.config_dir = project_path / "2dos" / ".2do"
            else:
                self.config_dir = project_path / "2DO"
            self.is_local_project = True
        else:
            self.config_dir = Path.home() / ".2do"
            self.is_local_project = False
            
        self.config_file = self.config_dir / "config.yaml"
        self.global_config_dir = Path.home() / ".2do"
        self.global_config_file = self.global_config_dir / "config.yaml"
        self.suppress_prompts = suppress_prompts
        
        # Load environment variables from .env file
        self._load_environment_variables()
        
        # Ensure config directory exists with enhanced permission handling
        preferred_paths = []
        if self.is_local_project:
            preferred_paths.append(self.config_dir)
        preferred_paths.extend([
            Path.home() / ".2do",
            Path.home() / ".2do_fallback"
        ])
        
        # Use PermissionManager to get a secure directory
        secure_dir = PermissionManager.get_secure_directory(preferred_paths, "2do_config")
        
        # Update paths if we had to use a fallback
        if secure_dir != self.config_dir:
            from rich.console import Console
            console = Console()
            if self.is_local_project:
                console.print(f"💡 Using fallback configuration directory: {secure_dir}")
                self.is_local_project = False
            self.config_dir = secure_dir
            self.config_file = self.config_dir / "config.yaml"
        
        # Ensure proper permissions on the config directory
        PermissionManager.ensure_directory_permissions(self.config_dir)
        
        self._load_config()
    
    def _is_git_repo(self, path):
        """Check if the path is a git repository"""
        git_dir = Path(path) / ".git"
        return git_dir.exists()
    
    def _load_environment_variables(self):
        """Load environment variables from .env file"""
        # Try to load from project root first, then from current directory
        env_paths = []
        
        # If we're in a project, look for .env in project root
        if hasattr(self, 'config_dir') and self.is_local_project:
            project_root = self.config_dir.parent.parent if self.config_dir.name == '.2do' else self.config_dir.parent
            env_paths.append(project_root / '.env')
        
        # Also check current working directory
        env_paths.append(Path.cwd() / '.env')
        
        # Load from the first .env file found
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {
                "api_keys": {},
                "preferences": {
                    "default_model": "auto",
                    "max_parallel_tasks": 5,
                    "memory_enabled": True
                },
                "mcp_servers": [],
                "analysis": {
                    "last_analyzed": None,
                    "tech_stack": [],
                    "memory_files_created": False,
                    "analysis_completed": False
                }
            }
            self._save_config()
        
        # Check if local config is empty or missing keys and global config has values
        if self.is_local_project:
            self._handle_local_config_fallback()
    
    def _handle_local_config_fallback(self):
        """Handle fallback to global config when local config is empty or missing keys"""
        # Skip if prompts are suppressed
        if self.suppress_prompts:
            return
            
        # Check if local config has any meaningful API keys
        local_has_keys = self._config_has_api_keys(self.config)
        
        # Load global config to check if it has keys
        global_config = self._load_global_config()
        global_has_keys = global_config and self._config_has_api_keys(global_config)
        
        # If local doesn't have keys but global does, offer to copy or use global
        if not local_has_keys and global_has_keys:
            self._prompt_for_global_config_usage(global_config)
    
    def _config_has_api_keys(self, config):
        """Check if config has any non-empty API keys"""
        api_keys = config.get("api_keys", {})
        return any(
            key and str(key).strip() and str(key).strip().lower() not in ['null', 'none', '']
            for key in api_keys.values()
        )
    
    def _load_global_config(self):
        """Load global config from home directory"""
        if not self.global_config_file.exists():
            return None
        
        try:
            with open(self.global_config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return None
    
    def _prompt_for_global_config_usage(self, global_config):
        """Prompt user to copy global config or use global values"""
        try:
            from rich.console import Console
            from rich.prompt import Confirm, Prompt
            from rich.panel import Panel
            
            console = Console()
            
            # Show what keys are available in global config
            global_keys = [
                key for key, value in global_config.get("api_keys", {}).items()
                if value and str(value).strip() and str(value).strip().lower() not in ['null', 'none', '']
            ]
            
            if not global_keys:
                return
            
            console.print(Panel(
                f"📁 Local 2DO config is empty, but global config has API keys:\n"
                f"   {', '.join(global_keys)}\n\n"
                f"Local config: {self.config_file}\n"
                f"Global config: {self.global_config_file}",
                title="🔑 Configuration Found",
                style="yellow"
            ))
            
            # Check for non-interactive mode (for testing)
            if os.environ.get('TWODO_NON_INTERACTIVE') == '1':
                # In non-interactive mode, default to copying global config
                self._copy_global_to_local(global_config)
                console.print("✅ Global configuration copied to local project (non-interactive mode)")
                return
            
            choice = Prompt.ask(
                "What would you like to do?",
                choices=["copy", "global", "skip"],
                default="copy"
            )
            
            if choice == "copy":
                self._copy_global_to_local(global_config)
                console.print("✅ Global configuration copied to local project")
            elif choice == "global":
                console.print("✅ Will use global configuration")
                # Use global config but don't modify local file
                self.config = global_config
            else:
                console.print("⏭️ Keeping empty local configuration")
                
        except ImportError:
            # If rich is not available, just copy the config silently
            self._copy_global_to_local(global_config)
        except Exception:
            # If prompting fails for any reason, silently fall back to local config
            pass
    
    def _copy_global_to_local(self, global_config):
        """Copy global config values to local config"""
        # Copy API keys
        if "api_keys" in global_config:
            self.config["api_keys"] = global_config["api_keys"].copy()
        
        # Copy preferences (merge with existing)
        if "preferences" in global_config:
            self.config.setdefault("preferences", {})
            for key, value in global_config["preferences"].items():
                # Only copy if local doesn't already have a value
                if key not in self.config["preferences"]:
                    self.config["preferences"][key] = value
        
        # Copy MCP servers
        if "mcp_servers" in global_config:
            self.config["mcp_servers"] = global_config["mcp_servers"].copy()
        
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file with enhanced permission handling"""
        try:
            # Ensure directory and file permissions
            PermissionManager.ensure_directory_permissions(self.config_file.parent)
            
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            # Set secure file permissions
            PermissionManager.ensure_file_permissions(self.config_file)
            
        except (OSError, PermissionError) as e:
            from rich.console import Console
            console = Console()
            console.print(f"❌ Cannot save config to {self.config_file}: {e}")
            
            # Try backup location
            backup_file = self.config_file.parent / f"config_backup_{int(__import__('time').time())}.yaml"
            try:
                with open(backup_file, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
                console.print(f"💾 Saved config to backup file: {backup_file}")
            except Exception as backup_error:
                console.print(f"❌ Cannot save backup config: {backup_error}")
                raise Exception(f"Cannot save configuration: {e}") from e
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a provider"""
        self.config["api_keys"][provider] = api_key
        self._save_config()
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider - prioritize environment variables over config file"""
        # Environment variable mapping
        env_var_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY', 
            'github': 'GITHUB_TOKEN'
        }
        
        # First check environment variables (most secure)
        env_var = env_var_map.get(provider)
        if env_var:
            env_value = os.getenv(env_var)
            if env_value and env_value.strip():
                return env_value.strip()
        
        # Fallback to config file (for backward compatibility)
        return self.config["api_keys"].get(provider)
    
    def has_api_keys(self) -> bool:
        """Check if any API keys are configured"""
        return bool(self.config["api_keys"])
    
    def get_available_providers(self) -> list:
        """Get list of configured AI providers"""
        return list(self.config["api_keys"].keys())
    
    def get_preference(self, key: str, default=None):
        """Get a preference value"""
        return self.config["preferences"].get(key, default)
    
    def set_preference(self, key: str, value):
        """Set a preference value"""
        self.config["preferences"][key] = value
        self._save_config()
    
    def add_mcp_server(self, server_config: dict):
        """Add MCP server configuration"""
        self.config["mcp_servers"].append(server_config)
        self._save_config()
    
    def get_mcp_servers(self) -> list:
        """Get configured MCP servers"""
        return self.config["mcp_servers"]
    
    def has_been_analyzed(self, repo_path: str = None) -> bool:
        """Check if repository has been analyzed recently"""
        analysis_config = self.config.get("analysis", {})
        last_analyzed = analysis_config.get("last_analyzed")
        analysis_completed = analysis_config.get("analysis_completed", False)
        
        # If never analyzed, return False
        if not last_analyzed:
            return False
            
        # Check if analysis was completed (new field takes precedence)
        if "analysis_completed" in analysis_config:
            return analysis_completed
            
        # Backward compatibility: check memory files if no analysis_completed field
        memory_files_created = analysis_config.get("memory_files_created", False)
        if not memory_files_created:
            return False
            
        # Check if memory files still exist for backward compatibility
        memory_dir = self.config_dir / "memory"
        if not memory_dir.exists():
            return False
            
        # Check if we have at least one memory file
        memory_files = list(memory_dir.glob("*_context.json"))
        return len(memory_files) > 0
    
    def get_last_analysis(self) -> dict:
        """Get the last analysis results"""
        return self.config.get("analysis", {})
    
    def save_analysis_results(self, tech_stack: list, memory_files_created: bool = False):
        """Save analysis results to config"""
        import datetime
        
        if "analysis" not in self.config:
            self.config["analysis"] = {}
            
        self.config["analysis"]["last_analyzed"] = datetime.datetime.now().isoformat()
        self.config["analysis"]["tech_stack"] = tech_stack
        self.config["analysis"]["memory_files_created"] = memory_files_created
        self.config["analysis"]["analysis_completed"] = True  # New field to track completion
        self._save_config()
    
    def should_skip_analysis(self, force_reanalyze: bool = False) -> bool:
        """Determine if analysis should be skipped"""
        if force_reanalyze:
            return False
        return self.has_been_analyzed()
    
    def has_memory_files(self) -> bool:
        """Check if memory files exist for the last analysis"""
        analysis_config = self.config.get("analysis", {})
        memory_files_created = analysis_config.get("memory_files_created", False)
        
        if not memory_files_created:
            return False
            
        # Check if memory files still exist
        memory_dir = self.config_dir / "memory"
        if not memory_dir.exists():
            return False
            
        # Check if we have at least one memory file
        memory_files = list(memory_dir.glob("*_context.json"))
        return len(memory_files) > 0