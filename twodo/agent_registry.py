#!/usr/bin/env python3
"""
Agent Registry System for 2DO CLI
Enables multiple 2DO agents to discover and communicate with each other across repositories.
"""

import json
import os
import time
import uuid
import socket
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from .config import ConfigManager


@dataclass
class AgentInfo:
    """Information about a 2DO agent"""
    agent_id: str
    repo_path: str
    repo_name: str
    repo_description: str
    hostname: str
    process_id: int
    last_heartbeat: float
    capabilities: List[str]
    tech_stack: List[str]
    readme_summary: str
    github_url: Optional[str] = None
    agent_name: Optional[str] = None
    status: str = "online"  # online, busy, helping, available


class AgentRegistry:
    """Manages agent registration, discovery, and presence"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.registry_dir = Path.home() / ".2do" / "agents"
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
        self.agent_id = self._generate_agent_id()
        self.heartbeat_interval = 30  # seconds
        self.agent_timeout = 120  # seconds - consider agent offline after this
        
    def _generate_agent_id(self) -> str:
        """Generate unique agent ID"""
        return f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    
    def _get_repo_info(self) -> Dict[str, Any]:
        """Extract repository information from current directory"""
        cwd = Path.cwd()
        repo_name = cwd.name
        repo_path = str(cwd)
        
        # Try to get repository description from README
        readme_files = ['README.md', 'readme.md', 'README.txt', 'README']
        readme_content = ""
        readme_summary = "No description available"
        
        for readme_file in readme_files:
            readme_path = cwd / readme_file
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        readme_content = f.read()
                        # Extract first meaningful paragraph as summary
                        lines = readme_content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#') and len(line) > 20:
                                readme_summary = line[:200] + ('...' if len(line) > 200 else '')
                                break
                    break
                except Exception:
                    continue
        
        # Try to get GitHub URL from git remote
        github_url = None
        try:
            import subprocess
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True, cwd=cwd)
            if result.returncode == 0:
                github_url = result.stdout.strip()
        except Exception:
            pass
        
        # Detect tech stack (simplified version)
        tech_stack = []
        tech_indicators = {
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', '*.py'],
            'javascript': ['package.json', 'node_modules', '*.js'],
            'typescript': ['tsconfig.json', '*.ts'],
            'react': ['package.json'],  # Will check content later
            'laravel': ['composer.json', 'artisan'],
            'php': ['composer.json', '*.php'],
            'docker': ['Dockerfile', 'docker-compose.yml'],
            'git': ['.git']
        }
        
        for tech, indicators in tech_indicators.items():
            for indicator in indicators:
                if indicator.startswith('*'):
                    # Check for file pattern
                    ext = indicator[1:]
                    if any(cwd.glob(f"**/*{ext}")):
                        tech_stack.append(tech)
                        break
                else:
                    # Check for specific file/directory
                    if (cwd / indicator).exists():
                        tech_stack.append(tech)
                        break
        
        # Check package.json for React/Vue/Angular
        package_json_path = cwd / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    dependencies = {**package_data.get('dependencies', {}), 
                                  **package_data.get('devDependencies', {})}
                    
                    if 'react' in dependencies:
                        tech_stack.append('react')
                    if 'vue' in dependencies:
                        tech_stack.append('vue')
                    if '@angular/core' in dependencies:
                        tech_stack.append('angular')
            except Exception:
                pass
        
        # Define capabilities based on tech stack and repository features
        capabilities = ['general-development', 'code-review', 'documentation']
        
        if 'python' in tech_stack:
            capabilities.extend(['python-development', 'api-development'])
        if 'javascript' in tech_stack or 'typescript' in tech_stack:
            capabilities.extend(['frontend-development', 'web-development'])
        if 'react' in tech_stack:
            capabilities.extend(['react-development', 'ui-development'])
        if 'laravel' in tech_stack or 'php' in tech_stack:
            capabilities.extend(['php-development', 'backend-development'])
        if 'docker' in tech_stack:
            capabilities.extend(['containerization', 'devops'])
        if github_url and 'github.com' in github_url:
            capabilities.append('github-integration')
        
        # Check for specific patterns that indicate expertise
        if any(keyword in readme_content.lower() for keyword in ['authentication', 'auth', 'login']):
            capabilities.append('authentication-systems')
        if any(keyword in readme_content.lower() for keyword in ['api', 'rest', 'graphql']):
            capabilities.append('api-development')
        if any(keyword in readme_content.lower() for keyword in ['test', 'testing', 'pytest', 'jest']):
            capabilities.append('testing-frameworks')
        if any(keyword in readme_content.lower() for keyword in ['database', 'sql', 'mongodb']):
            capabilities.append('database-design')
        
        return {
            'repo_name': repo_name,
            'repo_path': repo_path,
            'repo_description': readme_summary,
            'github_url': github_url,
            'tech_stack': list(set(tech_stack)),  # Remove duplicates
            'capabilities': list(set(capabilities)),  # Remove duplicates
            'readme_summary': readme_summary
        }
    
    def register_agent(self, agent_name: Optional[str] = None) -> AgentInfo:
        """Register this agent in the registry"""
        repo_info = self._get_repo_info()
        
        agent_info = AgentInfo(
            agent_id=self.agent_id,
            repo_path=repo_info['repo_path'],
            repo_name=repo_info['repo_name'],
            repo_description=repo_info['repo_description'],
            hostname=socket.gethostname(),
            process_id=os.getpid(),
            last_heartbeat=time.time(),
            capabilities=repo_info['capabilities'],
            tech_stack=repo_info['tech_stack'],
            readme_summary=repo_info['readme_summary'],
            github_url=repo_info['github_url'],
            agent_name=agent_name or f"Agent-{repo_info['repo_name']}"
        )
        
        # Save agent info to registry
        agent_file = self.registry_dir / f"{self.agent_id}.json"
        with open(agent_file, 'w') as f:
            json.dump(asdict(agent_info), f, indent=2)
        
        return agent_info
    
    def update_heartbeat(self) -> None:
        """Update agent heartbeat timestamp"""
        agent_file = self.registry_dir / f"{self.agent_id}.json"
        if agent_file.exists():
            try:
                with open(agent_file, 'r') as f:
                    data = json.load(f)
                data['last_heartbeat'] = time.time()
                with open(agent_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass  # Ignore heartbeat update errors
    
    def get_online_agents(self) -> List[AgentInfo]:
        """Get list of currently online agents (excluding self)"""
        online_agents = []
        current_time = time.time()
        
        for agent_file in self.registry_dir.glob("*.json"):
            try:
                with open(agent_file, 'r') as f:
                    data = json.load(f)
                
                # Skip self
                if data['agent_id'] == self.agent_id:
                    continue
                
                # Check if agent is still online (heartbeat within timeout)
                if current_time - data['last_heartbeat'] <= self.agent_timeout:
                    agent_info = AgentInfo(**data)
                    online_agents.append(agent_info)
                else:
                    # Remove stale agent file
                    try:
                        agent_file.unlink()
                    except Exception:
                        pass
                        
            except Exception:
                # Remove corrupted agent file
                try:
                    agent_file.unlink()
                except Exception:
                    pass
        
        return online_agents
    
    def find_agents_with_capability(self, capability: str) -> List[AgentInfo]:
        """Find agents that have a specific capability"""
        online_agents = self.get_online_agents()
        return [agent for agent in online_agents if capability in agent.capabilities]
    
    def find_agents_with_tech_stack(self, tech: str) -> List[AgentInfo]:
        """Find agents that work with specific technology"""
        online_agents = self.get_online_agents()
        return [agent for agent in online_agents if tech in agent.tech_stack]
    
    def cleanup_registry(self) -> None:
        """Clean up stale agent entries"""
        current_time = time.time()
        
        for agent_file in self.registry_dir.glob("*.json"):
            try:
                with open(agent_file, 'r') as f:
                    data = json.load(f)
                
                # Remove stale entries
                if current_time - data['last_heartbeat'] > self.agent_timeout:
                    agent_file.unlink()
                    
            except Exception:
                # Remove corrupted files
                try:
                    agent_file.unlink()
                except Exception:
                    pass
    
    def unregister_agent(self) -> None:
        """Remove this agent from registry"""
        agent_file = self.registry_dir / f"{self.agent_id}.json"
        try:
            if agent_file.exists():
                agent_file.unlink()
        except Exception:
            pass  # Ignore cleanup errors
    
    def get_agent_by_id(self, agent_id: str) -> Optional[AgentInfo]:
        """Get specific agent by ID"""
        agent_file = self.registry_dir / f"{agent_id}.json"
        if agent_file.exists():
            try:
                with open(agent_file, 'r') as f:
                    data = json.load(f)
                return AgentInfo(**data)
            except Exception:
                return None
        return None
    
    def update_agent_status(self, status: str) -> None:
        """Update this agent's status"""
        agent_file = self.registry_dir / f"{self.agent_id}.json"
        if agent_file.exists():
            try:
                with open(agent_file, 'r') as f:
                    data = json.load(f)
                data['status'] = status
                data['last_heartbeat'] = time.time()
                with open(agent_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass  # Ignore status update errors