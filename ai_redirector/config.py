"""
Configuration management for AI Redirector
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Optional

class ConfigManager:
    """Manages configuration and API keys for AI models"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".ai_redirector"
        self.config_file = self.config_dir / "config.yaml"
        self.config_dir.mkdir(exist_ok=True)
        self._load_config()
    
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