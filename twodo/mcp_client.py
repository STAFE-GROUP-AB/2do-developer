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
        """Initialize official MCP filesystem server with proper JSON-RPC communication"""
        try:
            # Use explicitly passed project_path first, then fall back to cwd
            if project_path:
                base_path = Path(project_path).resolve()
                console.print(f"🔍 DEBUG: Using explicit project_path: {project_path} -> {base_path}")
            else:
                base_path = Path.cwd()
                console.print(f"🔍 DEBUG: Using cwd fallback: {base_path}")
            
            console.print(f"🎯 Using explicit project path: {base_path}")
            
            # Start the official MCP filesystem server
            cmd = [
                "npx", "-y", "@modelcontextprotocol/server-filesystem", str(base_path)
            ]
            
            # Create the server process with proper stdio handling
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Initialize MCP protocol communication
            server_info = {
                'process': process,
                'base_path': str(base_path),
                'tools': [],
                'initialized': False
            }
            
            # Perform MCP handshake and get available tools
            try:
                tools = await self._initialize_mcp_protocol(process)
                server_info['tools'] = tools
                server_info['initialized'] = True
                console.print(f"✅ Official MCP filesystem server initialized with {len(tools)} tools")
            except Exception as protocol_error:
                console.print(f"⚠️ MCP protocol initialization failed: {protocol_error}")
                console.print(f"📋 Using fallback tool definitions for official server")
                server_info['tools'] = await self._get_filesystem_tools()
                server_info['initialized'] = False
            
            self.filesystem_server = server_info
            console.print(f"✅ Filesystem MCP server initialized for: {base_path}")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to initialize filesystem MCP server: {e}")
            return False
    
    async def _initialize_mcp_protocol(self, process):
        """Initialize MCP JSON-RPC protocol and get available tools from official server"""
        import json
        import asyncio
        
        try:
            # Send initialize request to MCP server
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "2do-mcp-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send the request
            request_json = json.dumps(init_request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Read the response with timeout
            try:
                response_data = await asyncio.wait_for(
                    process.stdout.readline(), 
                    timeout=5.0
                )
                response_text = response_data.decode().strip()
                
                if response_text:
                    response = json.loads(response_text)
                    console.print(f"🔧 MCP Initialize response: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
                else:
                    raise Exception("Empty response from MCP server")
                    
            except asyncio.TimeoutError:
                raise Exception("Timeout waiting for MCP server response")
            
            # Send tools/list request to get available tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            request_json = json.dumps(tools_request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Read tools response
            try:
                response_data = await asyncio.wait_for(
                    process.stdout.readline(),
                    timeout=5.0
                )
                response_text = response_data.decode().strip()
                
                if response_text:
                    tools_response = json.loads(response_text)
                    tools = tools_response.get('result', {}).get('tools', [])
                    
                    # Convert MCP tool format to our internal format
                    converted_tools = []
                    for tool in tools:
                        converted_tool = {
                            "name": tool.get("name", ""),
                            "description": tool.get("description", ""),
                            "parameters": tool.get("inputSchema", {})
                        }
                        converted_tools.append(converted_tool)
                    
                    console.print(f"🔧 Retrieved {len(converted_tools)} tools from official MCP server")
                    for tool in converted_tools:
                        console.print(f"  - {tool['name']}: {tool['description'][:60]}...")
                    
                    return converted_tools
                else:
                    raise Exception("Empty tools response from MCP server")
                    
            except asyncio.TimeoutError:
                raise Exception("Timeout waiting for tools list response")
                
        except Exception as e:
            console.print(f"❌ MCP protocol error: {e}")
            raise
    
    async def initialize_all_configured_servers(self, project_path: str = None):
        """Initialize all configured MCP servers for comprehensive tool access"""
        try:
            # Always initialize filesystem server first
            await self.initialize_filesystem_server(project_path)
            
            if not self.config_manager:
                console.print("⚠️ No config manager available for additional MCP servers")
                return
            
            # Get configured MCP servers from config
            mcp_servers = self.config_manager.get_mcp_servers()
            console.print(f"🔧 Found {len(mcp_servers)} configured MCP servers")
            
            # Initialize each configured server
            for server_config in mcp_servers:
                server_name = server_config.get('name')
                if server_name == 'filesystem':
                    continue  # Already initialized
                
                if server_config.get('enabled', True):
                    console.print(f"🚀 Initializing {server_name} MCP server...")
                    success = await self._initialize_mcp_server(server_config, project_path)
                    if success:
                        console.print(f"✅ {server_name} MCP server initialized")
                    else:
                        console.print(f"⚠️ {server_name} MCP server initialization failed")
                else:
                    console.print(f"⏭️ Skipping disabled server: {server_name}")
            
            # Log total tools available
            total_tools = len(self.filesystem_server.get('tools', []))
            for server_data in self.active_servers.values():
                total_tools += len(server_data.get('tools', []))
            
            console.print(f"✅ MCP initialization complete - {total_tools} total tools available")
            
        except Exception as e:
            console.print(f"❌ Error initializing MCP servers: {e}")
            import traceback
            traceback.print_exc()
    
    async def _initialize_mcp_server(self, server_config: Dict, project_path: str = None) -> bool:
        """Initialize a specific MCP server"""
        try:
            server_name = server_config.get('name')
            command = server_config.get('command')
            args = server_config.get('args', [])
            
            # Handle special server configurations
            if server_name == 'figma':
                # Figma server needs API key from token
                figma_token = self.config_manager.get_mcp_token('figma') if self.config_manager else None
                if not figma_token:
                    console.print(f"⚠️ Figma token not found, skipping {server_name} server")
                    return False
                # Update args with token
                args = [arg.replace('{figma_token}', figma_token) if '{figma_token}' in str(arg) else arg for arg in args]
            
            elif server_name == 'github':
                # GitHub server needs environment variable
                github_token = self.config_manager.get_mcp_token('github') if self.config_manager else None
                if github_token:
                    import os
                    os.environ['GITHUB_PERSONAL_ACCESS_TOKEN'] = github_token
            
            elif server_name == 'database':
                # Database server needs special handling
                db_config = server_config.get('config')
                if not db_config or not db_config.get('detected'):
                    console.print(f"⚠️ Database not configured, skipping {server_name} server")
                    return False
            
            # Build command with project path if needed
            if server_name == 'filesystem' and project_path:
                args = args + [project_path]
            
            # Start the server process
            try:
                process = await asyncio.create_subprocess_exec(
                    command, *args,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            except FileNotFoundError:
                console.print(f"⚠️ Command '{command}' not found for {server_name} server")
                return False
            
            # Get tools for this server
            tools = await self._get_server_tools(server_name, server_config)
            
            # Store server info
            self.active_servers[server_name] = {
                'process': process,
                'config': server_config,
                'tools': tools,
                'initialized': True
            }
            
            console.print(f"✅ {server_name} server initialized with {len(tools)} tools")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to initialize {server_name} server: {e}")
            return False
    
    async def _get_server_tools(self, server_name: str, server_config: Dict):
        """Get tools available from a specific MCP server"""
        # Return predefined tools based on server type
        if server_name == 'git':
            return await self._get_git_tools()
        elif server_name == 'github':
            return await self._get_github_tools()
        elif server_name == 'context':
            return await self._get_context_tools()
        elif server_name == 'web-fetch':
            return await self._get_web_fetch_tools()
        elif server_name == 'memory':
            return await self._get_memory_tools()
        elif server_name == 'database':
            return await self._get_database_tools()
        elif server_name == 'figma':
            return await self._get_figma_tools()
        else:
            # Return empty list for unknown servers
            console.print(f"⚠️ Unknown server type: {server_name}")
            return []
    
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
    
    async def _get_web_fetch_tools(self) -> List[Dict]:
        """Get Web Fetch MCP server tools"""
        return [
            {
                "name": "web_fetch",
                "description": "Fetch content from web URLs for research and analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch content from"},
                        "format": {"type": "string", "enum": ["text", "html", "markdown"], "default": "text"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "web_search",
                "description": "Search the web for information and documentation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Number of results", "default": 5}
                    },
                    "required": ["query"]
                }
            }
        ]
    
    async def _get_memory_tools(self) -> List[Dict]:
        """Get Memory MCP server tools"""
        return [
            {
                "name": "memory_store",
                "description": "Store information in persistent memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Memory key/identifier"},
                        "value": {"type": "string", "description": "Information to store"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags"}
                    },
                    "required": ["key", "value"]
                }
            },
            {
                "name": "memory_retrieve",
                "description": "Retrieve information from persistent memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Memory key to retrieve"},
                        "search": {"type": "string", "description": "Search query for fuzzy matching"}
                    }
                }
            },
            {
                "name": "memory_list",
                "description": "List all stored memory keys",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tag": {"type": "string", "description": "Filter by tag"}
                    }
                }
            }
        ]
    
    async def _get_database_tools(self) -> List[Dict]:
        """Get Database MCP server tools"""
        return [
            {
                "name": "db_query",
                "description": "Execute SQL query on the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query to execute"},
                        "params": {"type": "array", "description": "Query parameters"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "db_schema",
                "description": "Get database schema information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Specific table name (optional)"}
                    }
                }
            },
            {
                "name": "db_tables",
                "description": "List all tables in the database",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    
    async def _get_figma_tools(self) -> List[Dict]:
        """Get Figma MCP server tools"""
        return [
            {
                "name": "figma_file",
                "description": "Get Figma file information and components",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_key": {"type": "string", "description": "Figma file key"},
                        "node_ids": {"type": "array", "items": {"type": "string"}, "description": "Specific node IDs"}
                    },
                    "required": ["file_key"]
                }
            },
            {
                "name": "figma_components",
                "description": "Get design system components from Figma",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_key": {"type": "string", "description": "Figma file key"},
                        "component_type": {"type": "string", "description": "Filter by component type"}
                    },
                    "required": ["file_key"]
                }
            },
            {
                "name": "figma_styles",
                "description": "Get design tokens and styles from Figma",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_key": {"type": "string", "description": "Figma file key"},
                        "style_type": {"type": "string", "enum": ["FILL", "TEXT", "EFFECT", "GRID"], "description": "Style type"}
                    },
                    "required": ["file_key"]
                }
            }
        ]
    
    async def _get_filesystem_tools(self):
        """Get available tools from official MCP filesystem server"""
        return [
            {
                "name": "read_text_file",
                "description": "Read complete contents of a file as text with optional head/tail lines",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the file to read"},
                        "head": {"type": "number", "description": "First N lines (optional)"},
                        "tail": {"type": "number", "description": "Last N lines (optional)"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "read_media_file",
                "description": "Read an image or audio file and return base64 data with MIME type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the media file to read"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "read_multiple_files",
                "description": "Read multiple files simultaneously - failed reads won't stop the operation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "paths": {"type": "array", "items": {"type": "string"}, "description": "Array of file paths to read"}
                    },
                    "required": ["paths"]
                }
            },
            {
                "name": "write_file", 
                "description": "Create new file or overwrite existing (exercise caution with this)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File location"},
                        "content": {"type": "string", "description": "File content"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "edit_file",
                "description": "Make selective edits using advanced pattern matching with dry-run preview, whitespace preservation, and git-style diffs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File to edit"},
                        "edits": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "oldText": {"type": "string", "description": "Text to search for (can be substring)"},
                                    "newText": {"type": "string", "description": "Text to replace with"}
                                },
                                "required": ["oldText", "newText"]
                            },
                            "description": "List of edit operations"
                        },
                        "dryRun": {"type": "boolean", "description": "Preview changes without applying (default: false)"}
                    },
                    "required": ["path", "edits"]
                }
            },
            {
                "name": "create_directory",
                "description": "Create new directory or ensure it exists - creates parent directories if needed",
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
                "description": "List directory contents with [FILE] or [DIR] prefixes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the directory to list"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "move_file",
                "description": "Move or rename files and directories - fails if destination exists",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "description": "Source file or directory path"},
                        "destination": {"type": "string", "description": "Destination file or directory path"}
                    },
                    "required": ["source", "destination"]
                }
            },
            {
                "name": "search_files",
                "description": "Recursively search for files/directories with pattern matching",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Starting directory for search"},
                        "pattern": {"type": "string", "description": "Search pattern (glob or regex)"},
                        "fileType": {"type": "string", "enum": ["file", "directory", "both"], "description": "Type of items to search for"}
                    },
                    "required": ["path", "pattern"]
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
        """Call a filesystem tool through the official MCP server"""
        if not self.filesystem_server:
            raise RuntimeError("Official Filesystem MCP server not initialized")
        
        # Validate path for all operations that have a path parameter
        file_path = parameters.get("path", parameters.get("source", ""))
        if file_path:
            self._validate_file_operation(file_path, tool_name)
        
        try:
            # Route to official MCP filesystem server tools
            if tool_name == "read_text_file":
                return await self._call_official_mcp_tool(tool_name, parameters)
            elif tool_name == "read_media_file":
                return await self._call_official_mcp_tool(tool_name, parameters)
            elif tool_name == "read_multiple_files":
                return await self._call_official_mcp_tool(tool_name, parameters)
            elif tool_name == "write_file":
                return await self._call_official_mcp_tool(tool_name, parameters)
            elif tool_name == "edit_file":
                return await self._call_official_mcp_tool(tool_name, parameters)
            elif tool_name == "create_directory":
                return await self._call_official_mcp_tool(tool_name, parameters)
            elif tool_name == "list_directory":
                return await self._call_official_mcp_tool(tool_name, parameters)
            elif tool_name == "move_file":
                return await self._call_official_mcp_tool(tool_name, parameters)
            elif tool_name == "search_files":
                return await self._call_official_mcp_tool(tool_name, parameters)
            # Backward compatibility for old tool names
            elif tool_name == "read_file":
                # Map old read_file to new read_text_file
                return await self._call_official_mcp_tool("read_text_file", parameters)
            else:
                raise ValueError(f"Unknown filesystem tool: {tool_name}. Available tools: read_text_file, read_media_file, read_multiple_files, write_file, edit_file, create_directory, list_directory, move_file, search_files")
                
        except Exception as e:
            console.print(f"❌ Error calling official MCP tool {tool_name}: {e}")
            raise
    
    async def _call_official_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Call a tool on the official MCP filesystem server using JSON-RPC protocol"""
        import json
        import asyncio
        
        try:
            # Get the server info
            server_info = self.filesystem_server
            if not server_info or 'process' not in server_info:
                raise RuntimeError("Official MCP filesystem server process not available")
            
            console.print(f"🔧 Calling official MCP tool: {tool_name} with args: {parameters}")
            
            # If MCP protocol is properly initialized, use JSON-RPC
            if server_info.get('initialized', False):
                try:
                    return await self._call_mcp_tool_jsonrpc(tool_name, parameters, server_info['process'])
                except Exception as jsonrpc_error:
                    console.print(f"⚠️ JSON-RPC call failed: {jsonrpc_error}")
                    console.print(f"📋 Falling back to direct file operations")
            
            # Fallback to direct file operations with official server behavior
            return await self._fallback_file_operation(tool_name, parameters)
            
        except Exception as e:
            console.print(f"❌ Error in official MCP tool call: {e}")
            # Fallback to direct file operations
            return await self._fallback_file_operation(tool_name, parameters)
    
    async def _call_mcp_tool_jsonrpc(self, tool_name: str, parameters: Dict[str, Any], process) -> str:
        """Make actual JSON-RPC call to the MCP server"""
        import json
        import asyncio
        
        # Prepare the JSON-RPC request
        request_id = f"req_{tool_name}_{hash(str(parameters)) % 10000}"
        json_rpc_request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        # Send the request
        request_json = json.dumps(json_rpc_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # Read the response with timeout
        try:
            response_data = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=10.0  # Longer timeout for file operations
            )
            response_text = response_data.decode().strip()
            
            if response_text:
                response = json.loads(response_text)
                
                if 'error' in response:
                    error_msg = response['error'].get('message', 'Unknown MCP error')
                    console.print(f"❌ MCP tool error: {error_msg}")
                    return f"Error: {error_msg}"
                
                result = response.get('result', {})
                
                # Handle different result formats
                if isinstance(result, dict):
                    if 'content' in result:
                        content = result['content']
                        if isinstance(content, list) and len(content) > 0:
                            # Handle MCP content array format
                            return content[0].get('text', str(result))
                        else:
                            return str(content)
                    else:
                        return str(result)
                else:
                    return str(result)
            else:
                raise Exception("Empty response from MCP server")
                
        except asyncio.TimeoutError:
            raise Exception(f"Timeout waiting for {tool_name} response from MCP server")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from MCP server: {e}")
    
    async def _fallback_file_operation(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Fallback file operations using direct Python file I/O with official MCP server behavior"""
        base_path = Path(self.filesystem_server['base_path'])
        
        try:
            if tool_name == "read_text_file":
                file_path = base_path / parameters["path"]
                console.print(f"🔍 Reading file: {file_path.resolve()}")
                
                if not file_path.exists():
                    return f"Error: File {parameters['path']} does not exist"
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Handle head/tail parameters
                if 'head' in parameters or 'tail' in parameters:
                    lines = content.splitlines()
                    if 'head' in parameters:
                        lines = lines[:parameters['head']]
                    elif 'tail' in parameters:
                        lines = lines[-parameters['tail']:]
                    content = '\n'.join(lines)
                
                console.print(f"✅ File read successfully: {file_path.resolve()} ({len(content)} chars)")
                return content
                
            elif tool_name == "write_file":
                file_path = base_path / parameters["path"]
                console.print(f"✍️ Writing file: {file_path.resolve()}")
                
                # Create parent directories if needed
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(parameters["content"])
                
                console.print(f"✅ File written successfully: {file_path.resolve()} ({len(parameters['content'])} chars)")
                return f"Successfully wrote {len(parameters['content'])} characters to {parameters['path']}"
                
            elif tool_name == "edit_file":
                file_path = base_path / parameters["path"]
                console.print(f"✏️ Editing file: {file_path.resolve()}")
                
                if not file_path.exists():
                    return f"Error: File {parameters['path']} does not exist"
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply edits
                modified_content = content
                changes_made = 0
                
                for edit in parameters["edits"]:
                    old_text = edit["oldText"]
                    new_text = edit["newText"]
                    
                    if old_text in modified_content:
                        modified_content = modified_content.replace(old_text, new_text)
                        changes_made += 1
                        console.print(f"  ✅ Applied edit: '{old_text[:50]}...' → '{new_text[:50]}...'")
                    else:
                        console.print(f"  ⚠️ Edit target not found: '{old_text[:50]}...'")
                
                # Check if this is a dry run
                if parameters.get("dryRun", False):
                    return f"Dry run complete. Would make {changes_made} changes to {parameters['path']}"
                
                # Write the modified content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                console.print(f"✅ File edited successfully: {changes_made} changes applied")
                return f"Successfully applied {changes_made} edits to {parameters['path']}"
                
            elif tool_name == "list_directory":
                dir_path = base_path / parameters["path"]
                console.print(f"📁 Listing directory: {dir_path.resolve()}")
                
                if not dir_path.exists():
                    return f"Error: Directory {parameters['path']} does not exist"
                
                if not dir_path.is_dir():
                    return f"Error: {parameters['path']} is not a directory"
                
                items = []
                for item in sorted(dir_path.iterdir()):
                    prefix = "[DIR]" if item.is_dir() else "[FILE]"
                    items.append(f"{prefix} {item.name}")
                
                result = f"Contents of {parameters['path']}:\n" + "\n".join(items)
                console.print(f"✅ Directory listed: {len(items)} items")
                return result
                
            elif tool_name == "create_directory":
                dir_path = base_path / parameters["path"]
                console.print(f"📁 Creating directory: {dir_path.resolve()}")
                
                dir_path.mkdir(parents=True, exist_ok=True)
                console.print(f"✅ Directory created: {dir_path.resolve()}")
                return f"Successfully created directory {parameters['path']}"
                
            elif tool_name == "search_files":
                search_path = base_path / parameters["path"]
                pattern = parameters["pattern"]
                file_type = parameters.get("fileType", "both")
                
                console.print(f"🔍 Searching in {search_path.resolve()} for pattern: {pattern}")
                
                import glob
                matches = []
                search_pattern = str(search_path / "**" / pattern)
                
                for match in glob.glob(search_pattern, recursive=True):
                    match_path = Path(match)
                    relative_path = match_path.relative_to(base_path)
                    
                    if file_type == "file" and not match_path.is_file():
                        continue
                    elif file_type == "directory" and not match_path.is_dir():
                        continue
                    
                    prefix = "[DIR]" if match_path.is_dir() else "[FILE]"
                    matches.append(f"{prefix} {relative_path}")
                
                result = f"Search results for '{pattern}' in {parameters['path']}:\n" + "\n".join(matches[:50])  # Limit to 50 results
                if len(matches) > 50:
                    result += f"\n... and {len(matches) - 50} more matches"
                
                console.print(f"✅ Search complete: {len(matches)} matches found")
                return result
                
            elif tool_name == "move_file":
                source_path = base_path / parameters["source"]
                dest_path = base_path / parameters["destination"]
                
                console.print(f"📦 Moving {source_path.resolve()} → {dest_path.resolve()}")
                
                if not source_path.exists():
                    return f"Error: Source {parameters['source']} does not exist"
                
                if dest_path.exists():
                    return f"Error: Destination {parameters['destination']} already exists"
                
                # Create parent directory if needed
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                source_path.rename(dest_path)
                console.print(f"✅ File moved successfully")
                return f"Successfully moved {parameters['source']} to {parameters['destination']}"
                
            else:
                return f"Error: Unsupported tool {tool_name} in fallback mode"
                
        except Exception as e:
            error_msg = f"Error in {tool_name}: {str(e)}"
            console.print(f"❌ {error_msg}")
            return error_msg
    
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
