#!/usr/bin/env python3
"""
Browser Integration for 2DO - Provides web browser interaction during development
"""

import os
import subprocess
import threading
import time
import socket
from pathlib import Path
from typing import Optional, Dict, Any, List
import psutil
from rich.console import Console

console = Console()


class BrowserIntegration:
    """Manages browser interaction for development workflow"""
    
    def __init__(self, working_dir: str = None):
        self.working_dir = working_dir or os.getcwd()
        self.browser_process = None
        self.dev_server_process = None
        self.dev_server_url = None
        self.is_active = False
        
    def detect_project_type(self) -> Dict[str, Any]:
        """Detect the type of project and determine how to serve it"""
        project_info = {
            "type": "unknown",
            "server_command": None,
            "server_port": None,
            "server_url": None
        }
        
        # Check for React/Vue/Angular (package.json with scripts)
        package_json = Path(self.working_dir) / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    pkg_data = json.load(f)
                    
                scripts = pkg_data.get("scripts", {})
                dependencies = pkg_data.get("dependencies", {})
                dev_dependencies = pkg_data.get("devDependencies", {})
                all_deps = {**dependencies, **dev_dependencies}
                
                # React project
                if "react" in all_deps:
                    project_info["type"] = "react"
                    if "start" in scripts:
                        project_info["server_command"] = ["npm", "start"]
                        project_info["server_port"] = 3000
                    elif "dev" in scripts:
                        project_info["server_command"] = ["npm", "run", "dev"]
                        project_info["server_port"] = 3000
                
                # Vue project
                elif "vue" in all_deps or "@vue/cli-service" in all_deps:
                    project_info["type"] = "vue"
                    if "serve" in scripts:
                        project_info["server_command"] = ["npm", "run", "serve"]
                        project_info["server_port"] = 8080
                    elif "dev" in scripts:
                        project_info["server_command"] = ["npm", "run", "dev"]
                        project_info["server_port"] = 8080
                
                # Angular project
                elif "@angular/core" in all_deps:
                    project_info["type"] = "angular"
                    if "start" in scripts:
                        project_info["server_command"] = ["npm", "start"]
                        project_info["server_port"] = 4200
                    elif "serve" in scripts:
                        project_info["server_command"] = ["npm", "run", "serve"]
                        project_info["server_port"] = 4200
                
                # Next.js project
                elif "next" in all_deps:
                    project_info["type"] = "nextjs"
                    if "dev" in scripts:
                        project_info["server_command"] = ["npm", "run", "dev"]
                        project_info["server_port"] = 3000
                
                # Vite project
                elif "vite" in all_deps:
                    project_info["type"] = "vite"
                    if "dev" in scripts:
                        project_info["server_command"] = ["npm", "run", "dev"]
                        project_info["server_port"] = 5173
                        
            except Exception as e:
                console.print(f"⚠️  Error reading package.json: {e}")
        
        # Check for Laravel (composer.json + artisan)
        composer_json = Path(self.working_dir) / "composer.json"
        artisan_file = Path(self.working_dir) / "artisan"
        if composer_json.exists() and artisan_file.exists():
            project_info["type"] = "laravel"
            project_info["server_command"] = ["php", "artisan", "serve"]
            project_info["server_port"] = 8000
        
        # Check for Django (manage.py)
        manage_py = Path(self.working_dir) / "manage.py"
        if manage_py.exists():
            project_info["type"] = "django"
            project_info["server_command"] = ["python", "manage.py", "runserver"]
            project_info["server_port"] = 8000
        
        # Check for Flask (app.py or main.py with flask)
        for flask_file in ["app.py", "main.py", "run.py"]:
            flask_path = Path(self.working_dir) / flask_file
            if flask_path.exists():
                try:
                    content = flask_path.read_text()
                    if "flask" in content.lower() or "Flask" in content:
                        project_info["type"] = "flask"
                        project_info["server_command"] = ["python", flask_file]
                        project_info["server_port"] = 5000
                        break
                except Exception:
                    pass
        
        # Check for static HTML files
        html_files = list(Path(self.working_dir).glob("*.html"))
        if html_files and project_info["type"] == "unknown":
            project_info["type"] = "static"
            project_info["server_port"] = 8080
        
        # Set server URL if port is determined
        if project_info["server_port"]:
            project_info["server_url"] = f"http://localhost:{project_info['server_port']}"
        
        return project_info
    
    def find_free_port(self, start_port: int = 8080) -> int:
        """Find a free port starting from the given port"""
        for port in range(start_port, start_port + 100):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return port
                except OSError:
                    continue
        return start_port  # Fallback
    
    def start_dev_server(self, project_info: Dict[str, Any]) -> bool:
        """Start the development server for the project"""
        if project_info["type"] == "unknown":
            console.print("❌ Unknown project type, cannot start development server")
            return False
        
        try:
            if project_info["type"] == "static":
                # Use Python's built-in HTTP server for static files
                port = self.find_free_port(8080)
                self.dev_server_process = subprocess.Popen(
                    ["python", "-m", "http.server", str(port)],
                    cwd=self.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.dev_server_url = f"http://localhost:{port}"
                console.print(f"🌐 Started static file server at {self.dev_server_url}")
                
            elif project_info["server_command"]:
                # Start the project's development server
                self.dev_server_process = subprocess.Popen(
                    project_info["server_command"],
                    cwd=self.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.dev_server_url = project_info["server_url"]
                console.print(f"🚀 Started {project_info['type']} development server at {self.dev_server_url}")
            
            # Wait a moment for server to start
            time.sleep(2)
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to start development server: {e}")
            return False
    
    def open_browser(self, url: str = None) -> bool:
        """Open browser with the specified URL"""
        target_url = url or self.dev_server_url or "http://localhost:8080"
        
        try:
            # First try to use system default browser (more reliable)
            import webbrowser
            webbrowser.open(target_url)
            console.print(f"🌐 Opened system browser at {target_url}")
            self.is_active = True
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to open browser: {e}")
            return False
    
    def refresh_browser(self):
        """Refresh the browser page"""
        # This is a simplified implementation
        # In a full implementation, we'd maintain a browser page reference
        console.print("🔄 Browser refresh requested")
        
        # For now, we can re-open the browser or send a refresh signal
        if self.dev_server_url:
            # Could implement WebSocket-based auto-refresh here
            console.print(f"💡 Tip: Visit {self.dev_server_url} to see the latest changes")
    
    def start_browser_mode(self) -> bool:
        """Start the complete browser integration mode"""
        console.print("🚀 Starting browser integration mode...")
        
        # Detect project type
        project_info = self.detect_project_type()
        console.print(f"📁 Detected project type: {project_info['type']}")
        
        # Start development server
        if not self.start_dev_server(project_info):
            return False
        
        # Wait for server to be ready
        time.sleep(3)
        
        # Open browser
        if not self.open_browser():
            return False
        
        self.is_active = True
        console.print("✅ Browser integration mode is active!")
        console.print("💡 The browser will refresh automatically after task completion")
        return True
    
    def stop_browser_mode(self):
        """Stop browser integration mode"""
        console.print("🛑 Stopping browser integration mode...")
        
        self.is_active = False
        
        # Stop development server
        if self.dev_server_process:
            try:
                # Terminate the process and its children
                parent = psutil.Process(self.dev_server_process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                
                # Wait for termination
                parent.wait(timeout=5)
                console.print("🛑 Development server stopped")
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                # Force kill if needed
                try:
                    parent.kill()
                except psutil.NoSuchProcess:
                    pass
            except Exception as e:
                console.print(f"⚠️  Error stopping development server: {e}")
            finally:
                self.dev_server_process = None
        
        # Browser will close automatically when the thread exits
        console.print("✅ Browser integration mode stopped")
    
    def is_server_running(self) -> bool:
        """Check if the development server is running"""
        return self.dev_server_process is not None and self.dev_server_process.poll() is None
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of browser integration"""
        return {
            "active": self.is_active,
            "server_running": self.is_server_running(),
            "server_url": self.dev_server_url,
            "working_dir": self.working_dir
        }