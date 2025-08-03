"""
Configuration management for 2DO
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Optional

class ConfigManager:
    """Manages configuration and API keys for AI models"""
    
    def __init__(self, project_dir=None):
        # If project_dir is provided and is a git repo, use local 2DO folder
        if project_dir and self._is_git_repo(project_dir):
            self.config_dir = Path(project_dir) / "2DO"
            self.is_local_project = True
        else:
            self.config_dir = Path.home() / ".2do"
            self.is_local_project = False
            
        self.config_file = self.config_dir / "config.yaml"
        
        # Ensure config directory exists with proper error handling
        try:
            self.config_dir.mkdir(exist_ok=True)
        except (OSError, PermissionError) as e:
            # Fallback to home directory if we can't create the config directory
            if self.is_local_project:
                self.config_dir = Path.home() / ".2do"
                self.config_file = self.config_dir / "config.yaml"
                self.is_local_project = False
                self.config_dir.mkdir(exist_ok=True)
            else:
                raise
        
        self._load_config()
    
    def _is_git_repo(self, path):
        """Check if the path is a git repository"""
        git_dir = Path(path) / ".git"
        return git_dir.exists()
    
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
                "mcp_servers": []
            }
            self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a provider"""
        self.config["api_keys"][provider] = api_key
        self._save_config()
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
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