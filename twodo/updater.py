#!/usr/bin/env python3
"""
2DO Update Manager - Handles version checking and updates
"""

import os
import sys
import json
import subprocess
import shutil
import tempfile
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
import requests
from packaging import version
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

class UpdateManager:
    """Manages 2DO updates with multiple installation methods support"""
    
    def __init__(self):
        self.repo_owner = "STAFE-GROUP-AB"
        self.repo_name = "2do-developer"
        self.github_api_base = "https://api.github.com"
        
        try:
            self.current_version = self._get_current_version()
            # Ensure we never have an empty version
            if not self.current_version or not self.current_version.strip():
                console.print("⚠️ Warning: Could not detect version, using default 0.1.0")
                self.current_version = "0.1.0"
        except Exception as e:
            console.print(f"⚠️ Error detecting version: {e}, using default 0.1.0")
            self.current_version = "0.1.0"
        
        try:
            self.install_method = self._detect_install_method()
        except Exception as e:
            console.print(f"⚠️ Error detecting install method: {e}, using unknown")
            self.install_method = "unknown"
        
    def _get_current_version(self) -> str:
        """Get current installed version"""
        try:
            # Try to get version from package metadata
            import pkg_resources
            try:
                version = pkg_resources.get_distribution("2do").version
                if version and version.strip():
                    return version
            except pkg_resources.DistributionNotFound:
                pass
        except ImportError:
            pass
        
        # Fallback: try to get from pyproject.toml if in development
        try:
            import toml
            current_dir = Path(__file__).parent.parent
            pyproject_path = current_dir / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, 'r') as f:
                    data = toml.load(f)
                    version = data.get('project', {}).get('version', '0.1.0')
                    if version and version.strip():
                        return version
        except (ImportError, Exception) as e:
            # If toml is not available or parsing fails, continue to fallback
            pass
        
        # Alternative fallback: try to parse pyproject.toml manually
        try:
            current_dir = Path(__file__).parent.parent
            pyproject_path = current_dir / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, 'r') as f:
                    content = f.read()
                    # Simple regex to extract version
                    import re
                    # Try both single and double quotes
                    version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
                    if not version_match:
                        version_match = re.search(r"version\s*=\s*'([^']+)'", content)
                    if version_match:
                        version = version_match.group(1)
                        if version and version.strip():
                            return version
        except Exception:
            pass
        
        # Final fallback - ensure we never return empty string
        return "0.1.0"
    
    def _detect_install_method(self) -> str:
        """Detect how 2DO was installed"""
        executable_path = sys.executable
        
        # Check if running in virtual environment created by installer
        venv_path = Path.home() / ".2do"
        if venv_path.exists() and str(executable_path).startswith(str(venv_path)):
            return "installer_script"
        
        # Check if installed via pip in system/user environment
        try:
            import pkg_resources
            dist = pkg_resources.get_distribution("2do")
            if dist:
                return "pip"
        except (ImportError, pkg_resources.DistributionNotFound):
            pass
        
        # Check if running from source
        current_dir = Path(__file__).parent.parent
        if (current_dir / "setup.py").exists() or (current_dir / "pyproject.toml").exists():
            return "source"
        
        return "unknown"
    
    def check_for_updates(self) -> Dict:
        """Check if updates are available"""
        console.print("🔍 Checking for updates...")
        
        try:
            # Get latest release from GitHub
            url = f"{self.github_api_base}/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                # No releases found - this is common for new repositories
                return {
                    'update_available': False,
                    'current_version': self.current_version,
                    'latest_version': self.current_version,
                    'message': 'No releases available. This project may not use GitHub releases yet.',
                    'can_update_from_main': True,
                    'install_method': self.install_method
                }
            
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')
            
            # Compare versions with error handling
            try:
                # Ensure versions are not empty
                if not self.current_version or not self.current_version.strip():
                    console.print("⚠️ Warning: Current version is empty, defaulting to 0.1.0")
                    self.current_version = "0.1.0"
                
                if not latest_version or not latest_version.strip():
                    console.print("⚠️ Warning: Latest version is empty, using current version")
                    latest_version = self.current_version
                
                current_ver = version.parse(self.current_version)
                latest_ver = version.parse(latest_version)
                
                update_available = latest_ver > current_ver
            except Exception as e:
                console.print(f"⚠️ Version comparison failed: {e}")
                # Default to no update available if version parsing fails
                update_available = False
            
            return {
                'update_available': update_available,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'release_notes': release_data.get('body', ''),
                'download_url': release_data.get('tarball_url', ''),
                'release_url': release_data.get('html_url', ''),
                'published_at': release_data.get('published_at', ''),
                'install_method': self.install_method
            }
            
        except requests.RequestException as e:
            console.print(f"❌ Failed to check for updates: {e}")
            return {
                'update_available': False,
                'current_version': self.current_version,
                'latest_version': self.current_version,
                'error': str(e),
                'can_update_from_main': True,
                'install_method': self.install_method
            }
    
    def display_update_info(self, update_info: Dict):
        """Display update information in a nice format"""
        if update_info.get('error'):
            console.print(Panel(
                f"❌ Error checking for updates:\n{update_info['error']}\n\n"
                f"💡 You can still update from the main branch using --force\n"
                f"🔧 Install method: {update_info['install_method']}",
                title="Update Check Failed",
                style="red"
            ))
            return
        
        if update_info.get('message'):
            console.print(Panel(
                f"ℹ️ {update_info['message']}\n\n"
                f"🔧 Current version: {update_info['current_version']}\n"
                f"📦 Install method: {update_info['install_method']}\n\n"
                f"💡 You can update from the latest main branch using: 2do update --force",
                title="No Releases Found",
                style="yellow"
            ))
            return
        
        if not update_info['update_available']:
            console.print(Panel(
                f"✅ You're running the latest version!\n\n"
                f"🔧 Current version: {update_info['current_version']}\n"
                f"📦 Install method: {update_info['install_method']}",
                title="Up to Date",
                style="green"
            ))
            return
        
        # Show update available information
        console.print(Panel(
            f"🎉 New version available!\n\n"
            f"📦 Current version: {update_info['current_version']}\n"
            f"🆕 Latest version: {update_info['latest_version']}\n"
            f"🔧 Install method: {update_info['install_method']}\n"
            f"📅 Released: {update_info['published_at'][:10]}",
            title="Update Available",
            style="cyan"
        ))
        
        # Show release notes if available
        if update_info.get('release_notes'):
            notes = update_info['release_notes'][:500]
            if len(update_info['release_notes']) > 500:
                notes += "..."
            
            console.print(Panel(
                notes,
                title="📝 Release Notes",
                style="blue"
            ))
    
    def create_backup(self) -> Optional[str]:
        """Create backup of current installation"""
        if self.install_method == "installer_script":
            try:
                venv_path = Path.home() / ".2do"
                backup_path = Path.home() / f".2do_backup_{self.current_version}"
                
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                
                console.print("💾 Creating backup of current installation...")
                shutil.copytree(venv_path, backup_path)
                console.print(f"✅ Backup created: {backup_path}")
                return str(backup_path)
                
            except Exception as e:
                console.print(f"⚠️ Failed to create backup: {e}")
                return None
        
        return None
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup"""
        try:
            if not Path(backup_path).exists():
                console.print(f"❌ Backup not found: {backup_path}")
                return False
            
            venv_path = Path.home() / ".2do"
            if venv_path.exists():
                shutil.rmtree(venv_path)
            
            console.print("🔄 Restoring from backup...")
            shutil.copytree(backup_path, venv_path)
            console.print("✅ Backup restored successfully!")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to restore backup: {e}")
            return False
    
    def update_via_installer_script(self) -> bool:
        """Update using direct installation method (bypasses problematic installer script)"""
        try:
            console.print("🚀 Updating via direct installation...")
            
            # Get the virtual environment path
            venv_path = Path.home() / ".2do"
            pip_path = venv_path / "bin" / "pip"
            
            if not pip_path.exists():
                console.print("❌ Virtual environment not found. Please reinstall 2do.")
                return False
            
            # Create temporary directory for cloning
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_path = Path(temp_dir) / "2do-developer"
                
                # Clone the repository with explicit latest commit fetch
                console.print("📥 Downloading latest version...")
                result = subprocess.run([
                    "git", "clone", "--depth=1", "--branch=main", 
                    f"https://github.com/{self.repo_owner}/{self.repo_name}.git", str(repo_path)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    console.print(f"❌ Failed to download: {result.stderr}")
                    return False
                
                # Verify we have the latest commit with our fix
                console.print("🔍 Verifying latest code...")
                git_log_result = subprocess.run([
                    "git", "log", "--oneline", "-1"
                ], cwd=str(repo_path), capture_output=True, text=True)
                
                if git_log_result.returncode == 0:
                    latest_commit = git_log_result.stdout.strip()
                    console.print(f"📋 Installing from commit: {latest_commit}")
                    
                    # Check if our critical fix is present
                    ai_router_path = repo_path / "twodo" / "ai_router.py"
                    if ai_router_path.exists():
                        with open(ai_router_path, 'r') as f:
                            content = f.read()
                            if "def set_developer_context" in content:
                                console.print("✅ Critical fix verified in downloaded code")
                            else:
                                console.print("⚠️ Warning: Critical fix not found in downloaded code")
                else:
                    console.print("⚠️ Could not verify commit information")
                
                # Install all dependencies first to ensure nothing is missing
                console.print("🔧 Installing all dependencies...")
                
                # First, upgrade pip to ensure compatibility
                subprocess.run([
                    str(pip_path), "install", "--upgrade", "pip"
                ], capture_output=True, text=True)
                
                # Install critical dependencies that are often missing
                critical_deps = [
                    "python-dotenv>=1.0.0",
                    "croniter>=6.0.0", 
                    "apscheduler>=3.11.0",
                    "setuptools>=65.0.0",
                    "wheel"
                ]
                
                for dep in critical_deps:
                    console.print(f"📦 Installing {dep}...")
                    result = subprocess.run([
                        str(pip_path), "install", dep
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        console.print(f"⚠️ Warning: Failed to install {dep}: {result.stderr}")
                        # Continue anyway, as the main install might handle it
                
                # Install the updated package with all dependencies
                console.print("📦 Installing updated 2do with all dependencies...")
                result = subprocess.run([
                    str(pip_path), "install", "--upgrade", "--force-reinstall", str(repo_path)
                ], capture_output=True, text=True, cwd=str(repo_path))
                
                if result.returncode == 0:
                    console.print("✅ Update completed successfully!")
                    
                    # Verify the installed package has our critical fix
                    console.print("🔍 Verifying installed package...")
                    try:
                        # Check if the installed ai_router has our fix
                        installed_ai_router = venv_path / "lib" / "python3.9" / "site-packages" / "twodo" / "ai_router.py"
                        if installed_ai_router.exists():
                            with open(installed_ai_router, 'r') as f:
                                installed_content = f.read()
                                if "def set_developer_context" in installed_content:
                                    console.print("✅ Critical fix verified in installed package")
                                else:
                                    console.print("❌ CRITICAL: Fix missing in installed package!")
                                    return False
                        else:
                            console.print("⚠️ Could not verify installed package")
                    except Exception as e:
                        console.print(f"⚠️ Could not verify installation: {e}")
                    
                    # Ensure wrapper script exists
                    wrapper_path = Path.home() / ".local" / "bin" / "2do"
                    if not wrapper_path.exists():
                        console.print("🔧 Creating wrapper script...")
                        wrapper_path.parent.mkdir(parents=True, exist_ok=True)
                        wrapper_content = f"#!/bin/bash\n# 2DO wrapper script\nexec {venv_path}/bin/python -m twodo.cli \"$@\""
                        wrapper_path.write_text(wrapper_content)
                        wrapper_path.chmod(0o755)
                    
                    return True
                else:
                    console.print(f"❌ Update failed: {result.stderr}")
                    return False
                
        except Exception as e:
            console.print(f"❌ Update failed: {e}")
            return False
    
    def update_via_pip(self) -> bool:
        """Update using pip from GitHub"""
        try:
            console.print("🚀 Updating via pip...")
            
            # First, ensure critical dependencies are installed
            console.print("🔧 Installing critical dependencies...")
            critical_deps = [
                "python-dotenv>=1.0.0",
                "croniter>=6.0.0", 
                "apscheduler>=3.11.0"
            ]
            
            for dep in critical_deps:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True)
            
            # Update from GitHub repository
            repo_url = f"git+https://github.com/{self.repo_owner}/{self.repo_name}.git"
            
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", repo_url
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ Update completed successfully!")
                return True
            else:
                console.print(f"❌ Update failed: {result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Update failed: {e}")
            return False
    
    def update_source_installation(self) -> bool:
        """Update source installation by pulling latest changes"""
        try:
            console.print("🚀 Updating source installation...")
            
            # Get the repository root
            current_dir = Path(__file__).parent.parent
            
            # Pull latest changes
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=current_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                console.print(f"❌ Git pull failed: {result.stderr}")
                return False
            
            # Reinstall in development mode
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", "."
            ], cwd=current_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ Update completed successfully!")
                return True
            else:
                console.print(f"❌ Reinstallation failed: {result.stderr}")
                return False
                
        except Exception as e:
            console.print(f"❌ Update failed: {e}")
            return False
    
    def perform_update(self, backup_path: Optional[str] = None) -> bool:
        """Perform the actual update based on installation method"""
        success = False
        
        if self.install_method == "installer_script":
            success = self.update_via_installer_script()
        elif self.install_method == "pip":
            success = self.update_via_pip()
        elif self.install_method == "source":
            success = self.update_source_installation()
        else:
            console.print(f"❌ Unknown installation method: {self.install_method}")
            return False
        
        # If update failed and we have a backup, offer to restore
        if not success and backup_path:
            if Confirm.ask("❌ Update failed. Would you like to restore from backup?"):
                return self.restore_backup(backup_path)
        
        return success
    
    def setup_global_path(self) -> bool:
        """Ensure 2do is accessible globally by adding to PATH"""
        try:
            # Get the 2do binary path
            twodo_bin = Path.home() / ".2do" / "bin" / "2do"
            if not twodo_bin.exists():
                console.print("⚠️ 2do binary not found, skipping PATH setup")
                return False
            
            # Check if already in PATH
            try:
                result = subprocess.run(["which", "2do"], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print("✅ 2do is already accessible globally")
                    return True
            except:
                pass
            
            # Determine OS and setup PATH accordingly
            system = platform.system().lower()
            
            if system in ["darwin", "linux"]:
                return self._setup_unix_path(twodo_bin)
            elif system == "windows":
                return self._setup_windows_path(twodo_bin)
            else:
                console.print(f"⚠️ Unsupported OS: {system}")
                return False
                
        except Exception as e:
            console.print(f"⚠️ Error setting up global PATH: {e}")
            return False
    
    def _setup_unix_path(self, twodo_bin: Path) -> bool:
        """Setup PATH for macOS and Linux"""
        try:
            bin_dir = twodo_bin.parent
            
            # Common shell config files
            shell_configs = [
                Path.home() / ".bashrc",
                Path.home() / ".bash_profile", 
                Path.home() / ".zshrc",
                Path.home() / ".profile"
            ]
            
            path_line = f'export PATH="{bin_dir}:$PATH"  # Added by 2do installer'
            
            # Find existing shell config or create .profile
            config_file = None
            for config in shell_configs:
                if config.exists():
                    # Check if already added
                    content = config.read_text()
                    if str(bin_dir) in content and "2do" in content:
                        console.print("✅ PATH already configured")
                        return True
                    config_file = config
                    break
            
            if not config_file:
                config_file = Path.home() / ".profile"
            
            # Add to shell config
            with open(config_file, "a") as f:
                f.write(f"\n{path_line}\n")
            
            # Create symlink in /usr/local/bin if possible (common on macOS)
            local_bin = Path("/usr/local/bin/2do")
            if not local_bin.exists():
                try:
                    local_bin.symlink_to(twodo_bin)
                    console.print("✅ Created symlink in /usr/local/bin")
                except (PermissionError, OSError):
                    pass  # Fallback to shell config only
            
            system_name = "macOS" if platform.system() == "Darwin" else "Linux"
            console.print(Panel(
                f"🎉 2do has been added to your global PATH on {system_name}!\n\n"
                f"📝 Added to: {config_file}\n"
                f"💡 Restart your terminal or run: source {config_file}\n"
                f"🚀 You can now use '2do' from anywhere!",
                title="Global PATH Setup Complete",
                style="green"
            ))
            return True
            
        except Exception as e:
            console.print(f"⚠️ Error setting up Unix PATH: {e}")
            return False
    
    def _setup_windows_path(self, twodo_bin: Path) -> bool:
        """Setup PATH for Windows"""
        try:
            bin_dir = str(twodo_bin.parent)
            
            # Try to add to user PATH via registry
            import winreg
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            if bin_dir not in current_path:
                new_path = f"{current_path};{bin_dir}" if current_path else bin_dir
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                
                console.print(Panel(
                    f"🎉 2do has been added to your global PATH on Windows!\n\n"
                    f"💡 Restart your command prompt or PowerShell\n"
                    f"🚀 You can now use '2do' from anywhere!",
                    title="Global PATH Setup Complete",
                    style="green"
                ))
            else:
                console.print("✅ PATH already configured")
            
            winreg.CloseKey(key)
            return True
            
        except ImportError:
            console.print("⚠️ Windows registry access not available")
            return False
        except Exception as e:
            console.print(f"⚠️ Error setting up Windows PATH: {e}")
            return False
    
    def run_update_process(self, force: bool = False) -> bool:
        """Run the complete update process"""
        console.print(Panel.fit("🔄 2DO Update Manager", style="bold blue"))
        
        if force:
            console.print("🔄 Force update requested...")
            console.print("🌿 Using latest code from main branch (development version)")
            # Skip release check for force updates - go straight to main branch
            update_info = {
                'update_available': True,
                'current_version': self.current_version,
                'latest_version': 'main-branch',
                'install_method': self.install_method,
                'force_main_branch': True
            }
        else:
            console.print("🔍 Checking for updates...")
            # Check for updates from releases
            update_info = self.check_for_updates()
            self.display_update_info(update_info)
            
            if update_info.get('error') or update_info.get('message'):
                # No proper releases available
                return False
            
            if not update_info['update_available']:
                return True
        
        # Ask for confirmation
        if not force:
            if not Confirm.ask("📥 Would you like to update now?"):
                console.print("ℹ️ Update cancelled by user")
                return False
        
        # Show update method information
        method_info = {
            "installer_script": "Original installer script (recommended for stability)",
            "pip": "Pip installation (faster, requires git)",
            "source": "Source installation (development mode)",
            "unknown": "Unknown method - manual update required"
        }
        
        console.print(f"🔧 Update method: {method_info.get(self.install_method, 'Unknown')}")
        
        if self.install_method == "unknown":
            console.print(Panel(
                "❌ Cannot determine installation method.\n\n"
                "Please update manually using one of these methods:\n"
                "1. Run the installer script again\n"
                "2. Use: pip install --upgrade git+https://github.com/STAFE-GROUP-AB/2do-developer.git\n"
                "3. If installed from source: git pull && pip install -e .",
                title="Manual Update Required",
                style="red"
            ))
            return False
        
        # Create backup if possible
        backup_path = None
        if self.install_method == "installer_script":
            backup_path = self.create_backup()
        
        # Perform update with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Updating 2DO...", total=None)
            success = self.perform_update(backup_path)
        
        if success:
            console.print(Panel(
                f"🎉 2DO successfully updated!\n\n"
                f"📦 Previous version: {update_info['current_version']}\n"
                f"🆕 New version: {update_info['latest_version']}\n\n"
                f"💡 You may need to restart your terminal to use the updated version.",
                title="Update Complete",
                style="green"
            ))
            
            # Setup global PATH access
            console.print("🔧 Setting up global PATH access...")
            self.setup_global_path()
            
            # Clean up backup if update was successful
            if backup_path and Path(backup_path).exists():
                try:
                    shutil.rmtree(backup_path)
                    console.print("🧹 Cleaned up backup files")
                except Exception:
                    pass
        else:
            console.print(Panel(
                "❌ Update failed. Your installation should be unchanged.\n\n"
                "💡 Try updating manually or check the project repository for help.",
                title="Update Failed",
                style="red"
            ))
        
        return success
    
    def check_only(self) -> Dict:
        """Just check for updates without updating"""
        update_info = self.check_for_updates()
        self.display_update_info(update_info)
        return update_info