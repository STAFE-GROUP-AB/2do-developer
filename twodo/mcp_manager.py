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
    
    def get_recommended_servers(self, detected_technologies: List[str], project_context: Dict = None) -> List[Dict]:
        """Enhanced intelligent MCP server recommendations based on project context"""
        recommended = []
        
        # Convert detected technologies to lowercase for matching
        detected_tech_lower = [tech.lower() for tech in detected_technologies]
        
        # Enhanced scoring system for recommendations
        server_scores = {}
        
        # Always include essential servers with high base scores
        for server_id, server_info in self.mcp_servers["essential"].items():
            score = 100  # High base score for essential servers
            if server_id == "context7":
                score = 150  # Highest priority for Context7
            
            server_scores[f"essential_{server_id}"] = {
                "server": server_info,
                "category": "essential", 
                "id": server_id,
                "score": score,
                "match_reason": "Essential for intelligent development workflow"
            }
        
        # Analyze all server categories for matches
        for category, servers in self.mcp_servers.items():
            if category == "essential":
                continue  # Already processed
                
            for server_id, server_info in servers.items():
                server_technologies = [tech.lower() for tech in server_info["technologies"]]
                
                # Calculate match score
                matches = set(detected_tech_lower) & set(server_technologies)
                if matches:
                    base_score = len(matches) * 20  # 20 points per technology match
                    
                    # Bonus scoring based on project context
                    if project_context:
                        if project_context.get("project_type") == "tall_stack":
                            # TALL stack specific bonuses
                            if server_id in ["php", "git", "github"]:
                                base_score += 30
                            elif server_id in ["nodejs", "sqlite"]:
                                base_score += 20
                        
                        elif project_context.get("project_type") == "javascript":
                            if server_id in ["nodejs", "git", "github"]:
                                base_score += 30
                        
                        elif project_context.get("project_type") == "python":
                            if server_id in ["python", "git", "github"]:
                                base_score += 30
                    
                    # Category-based scoring adjustments
                    if category == "development":
                        base_score += 10  # Development tools are generally useful
                    elif category == "languages" and matches:
                        base_score += 15  # Language-specific tools get priority
                    
                    server_scores[f"{category}_{server_id}"] = {
                        "server": server_info,
                        "category": category,
                        "id": server_id, 
                        "score": base_score,
                        "match_reason": f"Matches detected: {', '.join(matches)} (Score: {base_score})"
                    }
        
        # Convert to list and sort by score (descending)
        sorted_servers = sorted(server_scores.values(), key=lambda x: x["score"], reverse=True)
        
        # Format for output
        for server_data in sorted_servers:
            recommended.append({
                "id": server_data["id"],
                "category": server_data["category"],
                "score": server_data["score"],
                **server_data["server"],
                "match_reason": server_data["match_reason"]
            })
        
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
        """Complete interactive MCP server setup with human colleague approach"""
        console.print(Panel.fit("🔌 MCP Server Setup - Let's optimize your development environment!", style="bold blue"))
        
        console.print("😊 Hey! I'm going to analyze your project and suggest some MCP servers that'll make your development workflow much smoother.")
        console.print("💡 Think of these as power-ups for our AI collaboration!")
        
        # Run analysis and get recommendations
        recommended_servers = self.run_tech_stack_analysis_and_recommend(project_path)
        
        if not recommended_servers:
            console.print("🤔 Hmm, I couldn't find specific recommendations for your project.")
            console.print("💡 But don't worry! The essential servers will still help you a lot.")
            return False
        
        # Display recommendations
        console.print(f"\n🎯 Based on your project, I found {len(recommended_servers)} servers that could really help!")
        self.display_recommended_servers(recommended_servers)
        
        # Interactive selection with encouraging tone
        console.print(f"\n🤝 Now, let's pick which ones you'd like me to set up.")
        console.print("💭 I recommend starting with the essential ones - they're like having a super-powered assistant!")
        
        selected_servers = self.select_servers_interactive(recommended_servers)
        
        if not selected_servers:
            console.print("👍 No problem! You can always set these up later when you're ready.")
            console.print("💡 Just run '2do mcp' anytime to come back to this setup.")
            return False
        
        # Configure selected servers with progress updates
        console.print(f"\n🚀 Awesome! Let me configure {len(selected_servers)} servers for you...")
        success = self.configure_mcp_servers(selected_servers)
        
        if success:
            console.print("🎉 Perfect! Your development environment is now supercharged!")
            console.print("💪 These servers will help me understand your project better and provide more accurate assistance.")
            console.print("🧠 I'll remember your preferences and project context across sessions now!")
        else:
            console.print("😅 Something went wrong with the setup, but we can try again anytime.")
        
        return success