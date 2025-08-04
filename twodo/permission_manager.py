"""
Permission Manager - Ensures proper file permissions for 2DO operations
"""

import os
import stat
import tempfile
from pathlib import Path
from typing import Optional, Union
from rich.console import Console

console = Console()

class PermissionManager:
    """Manages file and directory permissions for 2DO operations"""
    
    @staticmethod
    def ensure_directory_permissions(directory_path: Union[str, Path], mode: int = 0o755) -> bool:
        """
        Ensure a directory exists with proper permissions
        
        Args:
            directory_path: Path to the directory
            mode: Permission mode (default: 0o755 - rwxr-xr-x)
            
        Returns:
            bool: True if directory is accessible, False otherwise
        """
        directory_path = Path(directory_path)
        
        try:
            # Create directory if it doesn't exist
            directory_path.mkdir(parents=True, exist_ok=True)
            
            # Set permissions
            os.chmod(directory_path, mode)
            
            # Test write access
            test_file = directory_path / ".2do_permission_test"
            try:
                test_file.touch()
                test_file.unlink()
                return True
            except (OSError, PermissionError):
                console.print(f"⚠️ Directory exists but lacks write permissions: {directory_path}")
                return False
                
        except (OSError, PermissionError) as e:
            console.print(f"❌ Cannot create or access directory {directory_path}: {e}")
            return False
    
    @staticmethod
    def ensure_file_permissions(file_path: Union[str, Path], mode: int = 0o644) -> bool:
        """
        Ensure a file has proper permissions
        
        Args:
            file_path: Path to the file
            mode: Permission mode (default: 0o644 - rw-r--r--)
            
        Returns:
            bool: True if file is accessible, False otherwise
        """
        file_path = Path(file_path)
        
        try:
            if file_path.exists():
                # Set permissions on existing file
                os.chmod(file_path, mode)
                
                # Test read/write access
                with open(file_path, 'a') as f:
                    pass  # Just test if we can open for append
                return True
            else:
                # Test if we can create the file
                try:
                    file_path.touch()
                    os.chmod(file_path, mode)
                    return True
                except (OSError, PermissionError):
                    return False
                    
        except (OSError, PermissionError) as e:
            console.print(f"❌ Cannot access file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_secure_directory(preferred_paths: list, fallback_name: str = "2do_fallback") -> Path:
        """
        Get a secure directory with write permissions, trying preferred paths first
        
        Args:
            preferred_paths: List of preferred directory paths to try
            fallback_name: Name for fallback directory in temp
            
        Returns:
            Path: A writable directory path
        """
        # Try preferred paths first
        for path in preferred_paths:
            path = Path(path)
            if PermissionManager.ensure_directory_permissions(path):
                console.print(f"✅ Using directory: {path}")
                return path
            else:
                console.print(f"⚠️ Cannot use preferred directory: {path}")
        
        # Try home directory fallback
        home_fallback = Path.home() / f".{fallback_name}"
        if PermissionManager.ensure_directory_permissions(home_fallback):
            console.print(f"📁 Using home fallback directory: {home_fallback}")
            return home_fallback
        
        # Final fallback to temp directory
        temp_fallback = Path(tempfile.gettempdir()) / fallback_name
        if PermissionManager.ensure_directory_permissions(temp_fallback):
            console.print(f"📁 Using temporary directory: {temp_fallback}")
            console.print("⚠️ Data may not persist between sessions")
            return temp_fallback
        
        # If all else fails, use system temp directly
        console.print("⚠️ Using system temp directory directly - data will not persist")
        return Path(tempfile.gettempdir())
    
    @staticmethod
    def fix_permissions_recursive(directory_path: Union[str, Path], 
                                dir_mode: int = 0o755, 
                                file_mode: int = 0o644) -> bool:
        """
        Recursively fix permissions for all files and directories
        
        Args:
            directory_path: Root directory to fix
            dir_mode: Permission mode for directories
            file_mode: Permission mode for files
            
        Returns:
            bool: True if successful, False otherwise
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            console.print(f"❌ Directory does not exist: {directory_path}")
            return False
        
        try:
            # Fix directory permissions
            for root, dirs, files in os.walk(directory_path):
                root_path = Path(root)
                
                # Fix directory permission
                try:
                    os.chmod(root_path, dir_mode)
                except (OSError, PermissionError) as e:
                    console.print(f"⚠️ Cannot fix directory permissions for {root_path}: {e}")
                
                # Fix file permissions
                for file in files:
                    file_path = root_path / file
                    try:
                        os.chmod(file_path, file_mode)
                    except (OSError, PermissionError) as e:
                        console.print(f"⚠️ Cannot fix file permissions for {file_path}: {e}")
            
            console.print(f"✅ Fixed permissions for {directory_path}")
            return True
            
        except Exception as e:
            console.print(f"❌ Error fixing permissions: {e}")
            return False
    
    @staticmethod
    def check_system_permissions() -> dict:
        """
        Check system-level permissions and capabilities
        
        Returns:
            dict: Permission status information
        """
        status = {
            "home_writable": False,
            "temp_writable": False,
            "current_dir_writable": False,
            "user_id": os.getuid() if hasattr(os, 'getuid') else None,
            "effective_user_id": os.geteuid() if hasattr(os, 'geteuid') else None,
        }
        
        # Check home directory
        try:
            test_file = Path.home() / ".2do_permission_test"
            test_file.touch()
            test_file.unlink()
            status["home_writable"] = True
        except (OSError, PermissionError):
            pass
        
        # Check temp directory
        try:
            test_file = Path(tempfile.gettempdir()) / ".2do_permission_test"
            test_file.touch()
            test_file.unlink()
            status["temp_writable"] = True
        except (OSError, PermissionError):
            pass
        
        # Check current directory
        try:
            test_file = Path.cwd() / ".2do_permission_test"
            test_file.touch()
            test_file.unlink()
            status["current_dir_writable"] = True
        except (OSError, PermissionError):
            pass
        
        return status
    
    @staticmethod
    def create_secure_file(file_path: Union[str, Path], content: str = "", mode: int = 0o644) -> bool:
        """
        Create a file with secure permissions and content
        
        Args:
            file_path: Path to the file to create
            content: Initial content for the file
            mode: Permission mode for the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = Path(file_path)
        
        try:
            # Ensure parent directory exists
            if not PermissionManager.ensure_directory_permissions(file_path.parent):
                return False
            
            # Create file with content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Set permissions
            os.chmod(file_path, mode)
            
            console.print(f"✅ Created secure file: {file_path}")
            return True
            
        except (OSError, PermissionError) as e:
            console.print(f"❌ Cannot create secure file {file_path}: {e}")
            return False


def diagnose_permissions():
    """Diagnose and report current permission status"""
    console.print("🔍 Diagnosing 2DO file permissions...")
    
    # Check system permissions
    status = PermissionManager.check_system_permissions()
    
    console.print("\n📊 System Permission Status:")
    console.print(f"  Home directory writable: {'✅' if status['home_writable'] else '❌'}")
    console.print(f"  Temp directory writable: {'✅' if status['temp_writable'] else '❌'}")
    console.print(f"  Current directory writable: {'✅' if status['current_dir_writable'] else '❌'}")
    
    if status['user_id'] is not None:
        console.print(f"  User ID: {status['user_id']}")
        console.print(f"  Effective User ID: {status['effective_user_id']}")
    
    # Check 2DO specific directories
    console.print("\n📁 2DO Directory Status:")
    
    # Check standard 2DO directories
    home_2do = Path.home() / ".2do"
    if home_2do.exists():
        writable = PermissionManager.ensure_directory_permissions(home_2do)
        console.print(f"  ~/.2do: {'✅ Writable' if writable else '❌ Not writable'}")
    else:
        console.print("  ~/.2do: 📝 Does not exist (will be created)")
    
    # Check current project 2DO directory if in a git repo
    current_dir = Path.cwd()
    git_dir = current_dir / ".git"
    if git_dir.exists():
        project_2do = current_dir / "2DO"
        if project_2do.exists():
            writable = PermissionManager.ensure_directory_permissions(project_2do)
            console.print(f"  ./2DO: {'✅ Writable' if writable else '❌ Not writable'}")
        else:
            console.print("  ./2DO: 📝 Does not exist (will be created)")
    
    console.print("\n💡 Recommendations:")
    if not status['home_writable']:
        console.print("  - Check home directory permissions")
        console.print("  - Consider running: chmod 755 ~")
    
    if not status['temp_writable']:
        console.print("  - Check temp directory permissions")
        console.print("  - May need system administrator assistance")
    
    console.print("  - 2DO will automatically use fallback directories if needed")
    console.print("  - Run '2do --fix-permissions' to attempt automatic fixes")


if __name__ == "__main__":
    diagnose_permissions()
