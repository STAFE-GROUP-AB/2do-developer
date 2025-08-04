"""
MCP Server Manager - Manages Model Context Protocol servers based on tech stack analysis
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()

class MCPServerManager:
    """Manages MCP servers recommendations and configuration"""
    
    def __init__(self, config_manager=None, tech_stack_detector=None):
        self.config_manager = config_manager
        self.tech_stack_detector = tech_stack_detector
        
        # Define popular MCP servers organized by technology
        self.mcp_servers = {
            # Always recommended servers
            "essential": {
                "context7": {
                    "name": "Context7 (Upstash)",
                    "repository": "https://github.com/upstash/context7",
                    "description": "Advanced context management and memory for AI applications",
                    "command": "uvx context7",
                    "technologies": ["general"],
                    "priority": 1
                },
                "filesystem": {
                    "name": "Filesystem MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
                    "description": "File system operations and management",
                    "command": "uvx mcp-server-filesystem",
                    "technologies": ["general"],
                    "priority": 2
                }
            },
            
            # Development tools
            "development": {
                "git": {
                    "name": "Git MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/git",
                    "description": "Git repository operations and version control",
                    "command": "uvx mcp-server-git",
                    "technologies": ["git"],
                    "priority": 3
                },
                "github": {
                    "name": "GitHub MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/github",
                    "description": "GitHub API integration for issues, PRs, and repositories",
                    "command": "uvx mcp-server-github",
                    "technologies": ["git", "github"],
                    "priority": 4
                }
            },
            
            # Programming languages
            "languages": {
                "python": {
                    "name": "Python MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/python",
                    "description": "Python code execution and package management",
                    "command": "uvx mcp-server-python",
                    "technologies": ["python"],
                    "priority": 5
                },
                "nodejs": {
                    "name": "Node.js MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/nodejs",
                    "description": "Node.js and npm package management",
                    "command": "uvx mcp-server-nodejs",
                    "technologies": ["javascript", "node", "typescript"],
                    "priority": 6
                }
            },
            
            # Databases
            "databases": {
                "sqlite": {
                    "name": "SQLite MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
                    "description": "SQLite database operations and queries",
                    "command": "uvx mcp-server-sqlite",
                    "technologies": ["database", "sqlite"],
                    "priority": 7
                },
                "postgres": {
                    "name": "PostgreSQL MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/postgres",
                    "description": "PostgreSQL database operations and queries",
                    "command": "uvx mcp-server-postgres",
                    "technologies": ["database", "postgres"],
                    "priority": 8
                }
            },
            
            # Web and browser
            "web": {
                "browser": {
                    "name": "Browser MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/browser",
                    "description": "Browser automation and web scraping",
                    "command": "uvx mcp-server-browser",
                    "technologies": ["javascript", "web", "html", "css"],
                    "priority": 9
                },
                "playwright": {
                    "name": "Playwright MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/playwright",
                    "description": "Advanced browser automation with Playwright",
                    "command": "uvx mcp-server-playwright",
                    "technologies": ["javascript", "web", "playwright"],
                    "priority": 10
                }
            },
            
            # Infrastructure
            "infrastructure": {
                "docker": {
                    "name": "Docker MCP Server",
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/docker",
                    "description": "Docker container management and operations",
                    "command": "uvx mcp-server-docker",
                    "technologies": ["docker"],
                    "priority": 11
                },
                "aws": {
                    "name": "AWS MCP Server", 
                    "repository": "https://github.com/modelcontextprotocol/servers/tree/main/src/aws",
                    "description": "AWS cloud services integration",
                    "command": "uvx mcp-server-aws",
                    "technologies": ["aws", "cloud"],
                    "priority": 12
                }
            }
        }
    
    def get_recommended_servers(self, detected_technologies: List[str]) -> List[Dict]:
        """Get recommended MCP servers based on detected technologies"""
        recommended = []
        
        # Convert detected technologies to lowercase for matching
        detected_tech_lower = [tech.lower() for tech in detected_technologies]
        
        # Always include essential servers (especially context7)
        for server_id, server_info in self.mcp_servers["essential"].items():
            recommended.append({
                "id": server_id,
                "category": "essential",
                **server_info,
                "match_reason": "Essential for all projects"
            })
        
        # Add servers based on detected technologies
        for category, servers in self.mcp_servers.items():
            if category == "essential":
                continue  # Already added above
                
            for server_id, server_info in servers.items():
                server_technologies = [tech.lower() for tech in server_info["technologies"]]
                
                # Check if any detected technology matches server technologies
                matches = set(detected_tech_lower) & set(server_technologies)
                if matches:
                    recommended.append({
                        "id": server_id,
                        "category": category,
                        **server_info,
                        "match_reason": f"Matches detected: {', '.join(matches)}"
                    })
        
        # Sort by priority (lower number = higher priority)
        recommended.sort(key=lambda x: x["priority"])
        
        return recommended
    
    def display_recommended_servers(self, recommended_servers: List[Dict]):
        """Display recommended MCP servers in a nice table"""
        if not recommended_servers:
            console.print("No MCP servers recommended for this project.")
            return
        
        console.print(Panel.fit("🔌 Recommended MCP Servers", style="bold blue"))
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Match Reason", style="green")
        table.add_column("Command", style="yellow")
        
        for server in recommended_servers:
            table.add_row(
                server["name"],
                server["description"][:50] + "..." if len(server["description"]) > 50 else server["description"],
                server["match_reason"],
                server["command"]
            )
        
        console.print(table)
    
    def select_servers_interactive(self, recommended_servers: List[Dict]) -> List[Dict]:
        """Interactive selection of MCP servers"""
        selected_servers = []
        
        console.print("\n🎯 Select MCP servers to configure:")
        
        for i, server in enumerate(recommended_servers, 1):
            # Auto-select essential servers (like context7)
            if server["category"] == "essential":
                console.print(f"  {i}. ✅ {server['name']} (Essential - Auto-selected)")
                selected_servers.append(server)
            else:
                if Confirm.ask(f"  {i}. Add {server['name']}?", default=True):
                    selected_servers.append(server)
        
        return selected_servers
    
    def configure_mcp_servers(self, selected_servers: List[Dict]) -> bool:
        """Configure selected MCP servers"""
        if not self.config_manager:
            console.print("❌ No configuration manager available")
            return False
        
        if not selected_servers:
            console.print("No MCP servers selected for configuration")
            return True
        
        console.print(f"\n🔧 Configuring {len(selected_servers)} MCP servers...")
        
        configured_count = 0
        for server in selected_servers:
            try:
                # Check if server is already configured
                existing_servers = self.config_manager.get_mcp_servers()
                already_configured = any(
                    existing["name"] == server["name"] 
                    for existing in existing_servers
                )
                
                if already_configured:
                    console.print(f"  ⏭️  {server['name']} - Already configured")
                    continue
                
                # Add server configuration
                server_config = {
                    "name": server["name"],
                    "command": server["command"],
                    "description": server["description"],
                    "repository": server["repository"],
                    "category": server["category"],
                    "enabled": True
                }
                
                self.config_manager.add_mcp_server(server_config)
                console.print(f"  ✅ {server['name']} - Configured")
                configured_count += 1
                
            except Exception as e:
                console.print(f"  ❌ {server['name']} - Failed: {e}")
        
        console.print(f"\n🎉 Successfully configured {configured_count} MCP servers!")
        return configured_count > 0
    
    def list_configured_servers(self):
        """List currently configured MCP servers"""
        if not self.config_manager:
            console.print("❌ No configuration manager available")
            return
        
        configured_servers = self.config_manager.get_mcp_servers()
        
        if not configured_servers:
            console.print("No MCP servers configured yet.")
            return
        
        console.print(Panel.fit("🔌 Configured MCP Servers", style="bold green"))
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Command", style="yellow")
        table.add_column("Status", style="white")
        table.add_column("Category", style="blue")
        
        for server in configured_servers:
            status = "✅ Enabled" if server.get("enabled", True) else "❌ Disabled"
            table.add_row(
                server["name"],
                server["command"],
                status,
                server.get("category", "unknown")
            )
        
        console.print(table)
    
    def run_tech_stack_analysis_and_recommend(self, project_path: str = None) -> List[Dict]:
        """Run tech stack analysis and get MCP server recommendations"""
        if not self.tech_stack_detector:
            console.print("❌ No tech stack detector available")
            return []
        
        # Analyze the project
        if project_path and os.path.exists(project_path):
            console.print(f"🔍 Analyzing project: {project_path}")
            tech_stack = self.tech_stack_detector.analyze_repo(project_path)
        else:
            console.print("🔍 Analyzing current directory")
            tech_stack = self.tech_stack_detector.analyze_repo(os.getcwd())
        
        # Get recommendations based on detected tech stack
        recommended_servers = self.get_recommended_servers(tech_stack)
        
        # Display the analysis results
        if tech_stack:
            console.print(f"\n📋 Detected technologies: {', '.join(tech_stack)}")
        else:
            console.print("\n📋 No specific technologies detected, showing essential servers")
        
        return recommended_servers
    
    def setup_mcp_servers_interactive(self, project_path: str = None) -> bool:
        """Complete interactive MCP server setup process"""
        console.print(Panel.fit("🔌 MCP Server Setup", style="bold blue"))
        
        # Run analysis and get recommendations
        recommended_servers = self.run_tech_stack_analysis_and_recommend(project_path)
        
        if not recommended_servers:
            console.print("No MCP servers to recommend.")
            return False
        
        # Display recommendations
        self.display_recommended_servers(recommended_servers)
        
        # Interactive selection
        selected_servers = self.select_servers_interactive(recommended_servers)
        
        if not selected_servers:
            console.print("No MCP servers selected.")
            return False
        
        # Configure selected servers
        return self.configure_mcp_servers(selected_servers)