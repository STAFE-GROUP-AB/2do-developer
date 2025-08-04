"""
MCP Client - Integrates AI models with Model Context Protocol servers for file operations
"""

import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console

console = Console()

class MCPClient:
    """Client for connecting AI models to MCP servers"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.active_servers = {}
        self.filesystem_server = None
        
    async def initialize_filesystem_server(self, project_path: str = None):
        """Initialize filesystem server with project context"""
        try:
            # Use explicitly passed project_path first, then fall back to cwd
            if project_path:
                base_path = Path(project_path).resolve()
                console.print(f"🔍 DEBUG: Using explicit project_path: {project_path} -> {base_path}")
            else:
                base_path = Path.cwd()
                console.print(f"🔍 DEBUG: Using cwd fallback: {base_path}")
            
            console.print(f"🎯 Using explicit project path: {base_path}")
            # Start the filesystem MCP server
            cmd = [
                "npx", "-y", "@modelcontextprotocol/server-filesystem", base_path
            ]
            
            # Create the server process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.filesystem_server = {
                'process': process,
                'base_path': base_path,
                'tools': await self._get_filesystem_tools()
            }
            
            console.print(f"✅ Filesystem MCP server initialized for: {base_path}")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to initialize filesystem MCP server: {e}")
            return False
    
    async def initialize_all_configured_servers(self, project_path: str = None):
        """Initialize all configured MCP servers for comprehensive tool access"""
        try:
            # Initialize filesystem server first
            filesystem_success = await self.initialize_filesystem_server(project_path)
            
            if not self.config_manager:
                console.print("⚠️ No config manager available, only filesystem server initialized")
                return filesystem_success
            
            # Get all configured MCP servers
            configured_servers = self.config_manager.get_mcp_servers()
            if not configured_servers:
                console.print("⚠️ No additional MCP servers configured")
                return filesystem_success
            
            # Initialize each configured server
            for server in configured_servers:
                if server.get('name') == 'Filesystem MCP Server':
                    continue  # Already initialized
                
                if not server.get('enabled', True):
                    continue  # Skip disabled servers
                
                try:
                    await self._initialize_mcp_server(server, project_path)
                except Exception as e:
                    console.print(f"⚠️ Failed to initialize {server['name']}: {e}")
                    continue
            
            console.print(f"✅ Initialized {len(self.active_servers)} MCP servers total")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to initialize MCP servers: {e}")
            return filesystem_success
    
    async def _initialize_mcp_server(self, server_config: Dict, project_path: str = None):
        """Initialize a specific MCP server"""
        server_name = server_config['name']
        command = server_config['command']
        
        console.print(f"🔧 Initializing {server_name}...")
        
        # Parse command (e.g., "uvx mcp-server-git")
        cmd_parts = command.split()
        if project_path:
            cmd_parts.append(str(Path(project_path).resolve()))
        
        # Create the server process
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Get tools for this server
        tools = await self._get_server_tools(server_name, server_config)
        
        # Store in active servers
        self.active_servers[server_name] = {
            'process': process,
            'config': server_config,
            'tools': tools,
            'base_path': project_path
        }
        
        console.print(f"✅ {server_name} initialized with {len(tools)} tools")
    
    async def _get_server_tools(self, server_name: str, server_config: Dict) -> List[Dict]:
        """Get tools available from a specific MCP server"""
        # For now, return predefined tools based on server type
        # In a full implementation, this would query the actual MCP server
        
        if 'git' in server_name.lower():
            return await self._get_git_tools()
        elif 'github' in server_name.lower():
            return await self._get_github_tools()
        elif 'context' in server_name.lower():
            return await self._get_context_tools()
        else:
            return []  # Unknown server type
    
    async def _get_git_tools(self) -> List[Dict]:
        """Get Git MCP server tools"""
        return [
            {
                "name": "git_log",
                "description": "Get git commit history and logs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Number of commits to show", "default": 10},
                        "path": {"type": "string", "description": "Specific file or directory path"}
                    }
                }
            },
            {
                "name": "git_status",
                "description": "Get current git repository status",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "git_diff",
                "description": "Get git diff for changes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "staged": {"type": "boolean", "description": "Show staged changes", "default": False},
                        "path": {"type": "string", "description": "Specific file path"}
                    }
                }
            },
            {
                "name": "git_branch_info",
                "description": "Get information about git branches",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    
    async def _get_github_tools(self) -> List[Dict]:
        """Get GitHub MCP server tools"""
        return [
            {
                "name": "github_repo_info",
                "description": "Get GitHub repository information and metadata",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "github_issues",
                "description": "List GitHub issues for the repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                        "limit": {"type": "integer", "description": "Number of issues to fetch", "default": 10}
                    }
                }
            },
            {
                "name": "github_pull_requests",
                "description": "List GitHub pull requests for the repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                        "limit": {"type": "integer", "description": "Number of PRs to fetch", "default": 10}
                    }
                }
            },
            {
                "name": "github_readme",
                "description": "Get the repository README content",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    
    async def _get_context_tools(self) -> List[Dict]:
        """Get Context7 MCP server tools"""
        return [
            {
                "name": "context_search",
                "description": "Search through project context and memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Number of results", "default": 5}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "context_analyze",
                "description": "Analyze project structure and dependencies",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "context_memory",
                "description": "Store or retrieve project context memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["store", "retrieve"], "default": "retrieve"},
                        "key": {"type": "string", "description": "Memory key"},
                        "value": {"type": "string", "description": "Value to store (for store action)"}
                    },
                    "required": ["key"]
                }
            }
        ]
    
    async def _get_filesystem_tools(self):
        """Get available tools from filesystem MCP server"""
        return [
            {
                "name": "read_file",
                "description": "Read the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to read"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file", 
                "description": "Write content to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to write"},
                        "content": {"type": "string", "description": "Content to write to the file"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "create_directory",
                "description": "Create a directory",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "path": {"type": "string", "description": "Path to the directory to create"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "list_directory",
                "description": "List contents of a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the directory to list"}
                    },
                    "required": ["path"]
                }
            }
        ]
    
    def _is_restricted_path(self, file_path: str) -> bool:
        """Check if path is in restricted directories (vendor, node_modules)"""
        path_parts = Path(file_path).parts
        file_name = Path(file_path).name.lower()
        restricted_dirs = {'vendor', 'node_modules', '.git', '__pycache__', '.pytest_cache'}
        
        # Allow package manifest files for dependency detection
        allowed_manifest_files = {
            'composer.json', 'package.json', 'requirements.txt', 
            'pyproject.toml', 'pom.xml', 'build.gradle', 'cargo.toml'
        }
        
        # If it's a manifest file, allow it even in restricted directories
        if file_name in allowed_manifest_files:
            return False
        
        # Check if any part of the path is a restricted directory
        for part in path_parts:
            if part.lower() in restricted_dirs:
                return True
        return False
    
    def _validate_file_operation(self, file_path: str, operation: str) -> None:
        """Validate that file operation is allowed on this path"""
        if self._is_restricted_path(file_path):
            restricted_msg = (
                f"❌ RESTRICTED: {operation} operation blocked on '{file_path}'. "
                f"Access to vendor/, node_modules/, .git/, and cache directories is prohibited "
                f"for security and performance reasons. Only package manifest files "
                f"(composer.json, package.json) can be read for dependency detection."
            )
            raise PermissionError(restricted_msg)
    
    async def call_filesystem_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Call a filesystem tool through the MCP server"""
        if not self.filesystem_server:
            raise RuntimeError("Filesystem MCP server not initialized")
        
        # Validate path for all operations
        file_path = parameters.get("path", "")
        self._validate_file_operation(file_path, tool_name)
        
        try:
            if tool_name == "read_file":
                return await self._read_file(parameters["path"])
            elif tool_name == "write_file":
                return await self._write_file(parameters["path"], parameters["content"])
            elif tool_name == "create_directory":
                return await self._create_directory(parameters["path"])
            elif tool_name == "list_directory":
                return await self._list_directory(parameters["path"])
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            console.print(f"❌ Error calling {tool_name}: {e}")
            raise
    
    async def _read_file(self, file_path: str) -> str:
        """Read file contents"""
        try:
            base_path = Path(self.filesystem_server['base_path'])
            full_path = base_path / file_path
            
            # CRITICAL DEBUG: Print full file path details
            console.print(f"🔍 READ FILE DEBUG:")
            console.print(f"   📁 Base path: {base_path}")
            console.print(f"   📄 Relative path: {file_path}")
            console.print(f"   📍 Full resolved path: {full_path.resolve()}")
            console.print(f"   📂 File exists: {full_path.exists()}")
            
            if not full_path.exists():
                error_msg = f"Error: File {file_path} does not exist at {full_path.resolve()}"
                console.print(f"   ❌ {error_msg}")
                return error_msg
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            console.print(f"   ✅ File read successfully: {full_path.resolve()} ({len(content)} bytes)")
            return f"Successfully read {file_path}:\n{content}"
            
        except Exception as e:
            error_msg = f"Error reading {file_path}: {str(e)}"
            console.print(f"❌ {error_msg}")
            return error_msg
    
    async def _write_file(self, file_path: str, content: str) -> str:
        """Write content to a file"""
        try:
            # Validate the operation
            self._validate_file_operation(file_path, "write")
            
            # Resolve full path
            if self.filesystem_server:
                base_path = self.filesystem_server['base_path']
                full_path = base_path / file_path
            else:
                full_path = Path(file_path)
            
            # CRITICAL DEBUG: Print full file path details
            console.print(f"🔍 WRITE FILE DEBUG:")
            console.print(f"   📁 Base path: {self.filesystem_server['base_path'] if self.filesystem_server else 'None'}")
            console.print(f"   📄 Relative path: {file_path}")
            console.print(f"   📍 Full resolved path: {full_path.resolve()}")
            console.print(f"   ✍️  Content length: {len(content)} chars")
            console.print(f"   📝 Content preview: {content[:100]}{'...' if len(content) > 100 else ''}")
            
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            full_path.write_text(content, encoding='utf-8')
            
            # Verify the file was written
            if full_path.exists():
                actual_size = full_path.stat().st_size
                console.print(f"   ✅ File written successfully: {full_path.resolve()} ({actual_size} bytes)")
            else:
                console.print(f"   ❌ File write failed: {full_path.resolve()} does not exist after write")
            
            return f"Successfully wrote content to {file_path}"
            
        except Exception as e:
            error_msg = f"Error writing to {file_path}: {str(e)}"
            console.print(f"❌ {error_msg}")
            return error_msg
    
    async def _create_directory(self, dir_path: str) -> str:
        """Create directory"""
        try:
            base_path = Path(self.filesystem_server['base_path'])
            full_path = base_path / dir_path
            
            full_path.mkdir(parents=True, exist_ok=True)
            
            console.print(f"✅ Successfully created directory {dir_path}")
            return f"Successfully created directory {dir_path}"
            
        except Exception as e:
            error_msg = f"Error creating directory {dir_path}: {str(e)}"
            console.print(f"❌ {error_msg}")
            return error_msg
    
    async def _list_directory(self, dir_path: str) -> str:
        """List directory contents"""
        try:
            base_path = Path(self.filesystem_server['base_path'])
            full_path = base_path / dir_path
            
            if not full_path.exists():
                return f"Error: Directory {dir_path} does not exist"
            
            if not full_path.is_dir():
                return f"Error: {dir_path} is not a directory"
            
            items = []
            for item in full_path.iterdir():
                item_type = "directory" if item.is_dir() else "file"
                items.append(f"{item.name} ({item_type})")
            
            return f"Contents of {dir_path}:\n" + "\n".join(items)
            
        except Exception as e:
            return f"Error listing directory {dir_path}: {str(e)}"
    
    def get_all_tools_for_openai(self) -> List[Dict]:
        """Get all available tools formatted for OpenAI function calling"""
        all_tools = []
        
        # Add filesystem tools
        if self.filesystem_server:
            for tool in self.filesystem_server['tools']:
                all_tools.append({
                    "type": "function",
                    "function": tool
                })
        
        # Add tools from all other configured servers
        for server_name, server_data in self.active_servers.items():
            for tool in server_data.get('tools', []):
                all_tools.append({
                    "type": "function",
                    "function": tool
                })
        
        console.print(f"🔧 Providing {len(all_tools)} total tools to OpenAI model")
        return all_tools
    
    def get_filesystem_tools_for_openai(self) -> List[Dict]:
        """Get filesystem tools formatted for OpenAI function calling (legacy method)"""
        if not self.filesystem_server:
            return []
        
        return [
            {
                "type": "function",
                "function": tool
            }
            for tool in self.filesystem_server['tools']
        ]
    
    def get_all_tools_for_anthropic(self) -> List[Dict]:
        """Get all available tools formatted for Anthropic tool use"""
        all_tools = []
        
        # Add filesystem tools
        if self.filesystem_server:
            for tool in self.filesystem_server['tools']:
                anthropic_tool = {
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool["parameters"]
                }
                all_tools.append(anthropic_tool)
        
        # Add tools from all other configured servers
        for server_name, server_data in self.active_servers.items():
            for tool in server_data.get('tools', []):
                anthropic_tool = {
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool["parameters"]
                }
                all_tools.append(anthropic_tool)
        
        console.print(f"🔧 Providing {len(all_tools)} total tools to Anthropic model")
        return all_tools
    
    def get_filesystem_tools_for_anthropic(self) -> List[Dict]:
        """Get filesystem tools formatted for Anthropic tool use (legacy method)"""
        if not self.filesystem_server:
            return []
        
        # Anthropic uses a different format for tools
        anthropic_tools = []
        for tool in self.filesystem_server['tools']:
            anthropic_tool = {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"]
            }
            anthropic_tools.append(anthropic_tool)
        
        return anthropic_tools
    
    async def cleanup(self):
        """Clean up MCP server processes"""
        if self.filesystem_server and self.filesystem_server.get('process'):
            try:
                self.filesystem_server['process'].terminate()
                await self.filesystem_server['process'].wait()
                console.print("✅ Filesystem MCP server cleaned up")
            except Exception as e:
                console.print(f"⚠️ Error cleaning up filesystem server: {e}")
