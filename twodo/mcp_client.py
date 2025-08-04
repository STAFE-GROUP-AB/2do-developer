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
            
            if not full_path.exists():
                return f"Error: File {file_path} does not exist"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"Successfully read {file_path}:\n{content}"
            
        except Exception as e:
            return f"Error reading {file_path}: {str(e)}"
    
    async def _write_file(self, file_path: str, content: str) -> str:
        """Write content to file"""
        try:
            base_path = Path(self.filesystem_server['base_path'])
            full_path = base_path / file_path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            console.print(f"✅ Successfully wrote to {file_path}")
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
    
    def get_filesystem_tools_for_openai(self) -> List[Dict]:
        """Get filesystem tools formatted for OpenAI function calling"""
        if not self.filesystem_server:
            return []
        
        return [
            {
                "type": "function",
                "function": tool
            }
            for tool in self.filesystem_server['tools']
        ]
    
    async def cleanup(self):
        """Clean up MCP server processes"""
        if self.filesystem_server and self.filesystem_server.get('process'):
            try:
                self.filesystem_server['process'].terminate()
                await self.filesystem_server['process'].wait()
                console.print("✅ Filesystem MCP server cleaned up")
            except Exception as e:
                console.print(f"⚠️ Error cleaning up filesystem server: {e}")
