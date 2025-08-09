"""
Enhanced Permission Manager - Session-based permission management for 2DO operations
"""

import os
import stat
import tempfile
import json
import time
from pathlib import Path
from typing import Optional, Union, Dict, List, Set
from rich.console import Console
from rich.prompt import Confirm

console = Console()

class PermissionSet:
    """Represents a set of file operation permissions for a session"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{int(time.time())}"
        self.allowed_paths: Set[str] = set()
        self.allowed_patterns: Set[str] = set()
        self.read_permissions: Set[str] = set()
        self.write_permissions: Set[str] = set()
        self.execute_permissions: Set[str] = set()
        self.created_at = time.time()
        self.last_used = time.time()
        
    def add_path_permission(self, path: Union[str, Path], 
                          read: bool = False, write: bool = False, execute: bool = False):
        """Add permission for a specific path"""
        path_str = str(Path(path).resolve())
        self.allowed_paths.add(path_str)
        
        if read:
            self.read_permissions.add(path_str)
        if write:
            self.write_permissions.add(path_str)
        if execute:
            self.execute_permissions.add(path_str)
            
        self.last_used = time.time()
    
    def add_pattern_permission(self, pattern: str,
                             read: bool = False, write: bool = False, execute: bool = False):
        """Add permission for a file pattern (e.g., '*.py', '/project/**')"""
        self.allowed_patterns.add(pattern)
        
        if read:
            self.read_permissions.add(pattern)
        if write:
            self.write_permissions.add(pattern)
        if execute:
            self.execute_permissions.add(pattern)
            
        self.last_used = time.time()
    
    def has_permission(self, path: Union[str, Path], operation: str) -> bool:
        """Check if path has permission for operation (read/write/execute)"""
        path_str = str(Path(path).resolve())
        
        # Check direct path permissions
        if path_str in self.allowed_paths:
            if operation == 'read' and path_str in self.read_permissions:
                return True
            elif operation == 'write' and path_str in self.write_permissions:
                return True
            elif operation == 'execute' and path_str in self.execute_permissions:
                return True
        
        # Check pattern permissions
        for pattern in self.allowed_patterns:
            if self._matches_pattern(path_str, pattern):
                if operation == 'read' and pattern in self.read_permissions:
                    return True
                elif operation == 'write' and pattern in self.write_permissions:
                    return True
                elif operation == 'execute' and pattern in self.execute_permissions:
                    return True
        
        return False
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Simple pattern matching for file paths"""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'allowed_paths': list(self.allowed_paths),
            'allowed_patterns': list(self.allowed_patterns),
            'read_permissions': list(self.read_permissions),
            'write_permissions': list(self.write_permissions),
            'execute_permissions': list(self.execute_permissions),
            'created_at': self.created_at,
            'last_used': self.last_used
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PermissionSet':
        """Create from dictionary"""
        perm_set = cls(data['session_id'])
        perm_set.allowed_paths = set(data.get('allowed_paths', []))
        perm_set.allowed_patterns = set(data.get('allowed_patterns', []))
        perm_set.read_permissions = set(data.get('read_permissions', []))
        perm_set.write_permissions = set(data.get('write_permissions', []))
        perm_set.execute_permissions = set(data.get('execute_permissions', []))
        perm_set.created_at = data.get('created_at', time.time())
        perm_set.last_used = data.get('last_used', time.time())
        return perm_set


class SessionPermissionManager:
    """Enhanced permission manager with session-based permissions"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".2do"
        self.sessions_file = self.config_dir / "permission_sessions.json"
        self.current_session: Optional[PermissionSet] = None
        self.sessions: Dict[str, PermissionSet] = {}
        self._load_sessions()
    
    def _load_sessions(self):
        """Load saved permission sessions and set most recent as current"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    data = json.load(f)
                    
                for session_data in data.get('sessions', []):
                    perm_set = PermissionSet.from_dict(session_data)
                    self.sessions[perm_set.session_id] = perm_set
                
                # Set most recently used session as current
                if self.sessions:
                    most_recent = max(self.sessions.values(), key=lambda s: s.last_used)
                    self.current_session = most_recent
                    console.print(f"🔄 Loaded {len(self.sessions)} sessions, current: {most_recent.session_id}")
                    
        except Exception as e:
            console.print(f"⚠️ Could not load permission sessions: {e}")
    
    def _save_sessions(self):
        """Save permission sessions to disk"""
        try:
            # Ensure config directory exists
            PermissionManager.ensure_directory_permissions(self.config_dir)
            
            # Clean up old sessions (older than 30 days)
            cutoff_time = time.time() - (30 * 24 * 60 * 60)
            active_sessions = {
                sid: session for sid, session in self.sessions.items()
                if session.last_used > cutoff_time
            }
            
            data = {
                'sessions': [session.to_dict() for session in active_sessions.values()],
                'last_cleanup': time.time()
            }
            
            with open(self.sessions_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.sessions = active_sessions
            
        except Exception as e:
            console.print(f"⚠️ Could not save permission sessions: {e}")
    
    def create_session(self, session_id: str = None) -> PermissionSet:
        """Create a new permission session"""
        perm_set = PermissionSet(session_id)
        self.sessions[perm_set.session_id] = perm_set
        self.current_session = perm_set
        return perm_set
    
    def get_session(self, session_id: str) -> Optional[PermissionSet]:
        """Get an existing permission session"""
        return self.sessions.get(session_id)
    
    def set_current_session(self, session_id: str) -> bool:
        """Set the current active session"""
        if session_id in self.sessions:
            self.current_session = self.sessions[session_id]
            self.current_session.last_used = time.time()
            return True
        return False
    
    def request_permission(self, path: Union[str, Path], operation: str, 
                         auto_approve: bool = False, reason: str = "") -> bool:
        """
        Request permission for a file operation with interactive approval
        
        Args:
            path: File or directory path
            operation: 'read', 'write', or 'execute'
            auto_approve: Skip interactive prompt if True
            reason: Explanation for the permission request
            
        Returns:
            bool: True if permission granted
        """
        if not self.current_session:
            self.create_session()
        
        path_obj = Path(path).resolve()
        path_str = str(path_obj)
        
        # Check if permission already exists
        if self.current_session.has_permission(path_str, operation):
            return True
        
        # Interactive permission request (unless auto-approved)
        if not auto_approve:
            try:
                if not self._can_interact_with_user():
                    # If we can't interact, default to deny for security
                    console.print(f"❌ Permission denied for {operation} access to {path_str}")
                    console.print("💡 Run in interactive mode to grant permissions")
                    return False
                
                # Show permission request
                console.print(f"\n🔐 Permission Request")
                console.print(f"Operation: {operation.upper()}")
                console.print(f"Path: {path_str}")
                if reason:
                    console.print(f"Reason: {reason}")
                
                # Check if it's a sensitive path
                if self._is_sensitive_path(path_obj):
                    console.print(f"⚠️ This is a sensitive system path!")
                
                approved = Confirm.ask(f"Grant {operation} permission?", default=False)
                
                if not approved:
                    console.print(f"❌ Permission denied")
                    return False
                    
                # Ask about scope
                grant_parent = False
                if path_obj.is_file() and path_obj.parent != path_obj:
                    grant_parent = Confirm.ask(
                        f"Grant {operation} permission to parent directory as well?", 
                        default=False
                    )
                
            except (KeyboardInterrupt, EOFError):
                console.print(f"\n❌ Permission request cancelled")
                return False
        else:
            approved = True
            grant_parent = False
        
        if approved:
            # Grant the permission
            perm_operations = {operation: True}
            self.current_session.add_path_permission(path_str, **perm_operations)
            
            if grant_parent:
                self.current_session.add_path_permission(
                    str(path_obj.parent), **perm_operations
                )
            
            # Save sessions
            self._save_sessions()
            
            console.print(f"✅ {operation.capitalize()} permission granted for {path_str}")
            return True
        
        return False
    
    def grant_project_permissions(self, project_path: Union[str, Path], 
                                auto_approve: bool = False) -> bool:
        """Grant standard permissions for a project directory"""
        project_path = Path(project_path).resolve()
        
        if not auto_approve:
            if not self._can_interact_with_user():
                return False
                
            console.print(f"\n📁 Project Permission Setup")
            console.print(f"Project: {project_path}")
            console.print("This will grant read/write access to the project directory")
            
            if not Confirm.ask("Grant project permissions?", default=True):
                return False
        
        if not self.current_session:
            self.create_session()
        
        # Grant permissions for common project patterns
        project_patterns = [
            str(project_path / "**/*"),  # All files in project
            str(project_path / ".*"),    # Hidden files in project root
        ]
        
        for pattern in project_patterns:
            self.current_session.add_pattern_permission(pattern, read=True, write=True)
        
        # Also grant explicit permission to project root
        self.current_session.add_path_permission(project_path, read=True, write=True)
        
        self._save_sessions()
        console.print(f"✅ Project permissions granted for {project_path}")
        return True
    
    def _can_interact_with_user(self) -> bool:
        """Check if we can interact with the user for permission requests"""
        # Check if we have a controlling terminal
        if os.isatty(1) and os.isatty(2):
            # Check if we're NOT in a CI environment
            if not any(env in os.environ for env in ['CI', 'GITHUB_ACTIONS', 'JENKINS_URL']):
                # Try to access controlling terminal
                return os.path.exists('/dev/tty')
        return False
    
    def _is_sensitive_path(self, path: Path) -> bool:
        """Check if a path is sensitive (system directories, etc.)"""
        sensitive_patterns = [
            '/etc/**',
            '/usr/bin/**',
            '/usr/local/bin/**',
            '/bin/**',
            '/sbin/**',
            '/usr/sbin/**',
            '/var/log/**',
            '/var/lib/**',
            '/sys/**',
            '/proc/**',
            '/dev/**',
            str(Path.home() / '.ssh/**'),
            str(Path.home() / '.aws/**'),
            str(Path.home() / '.config/**'),
        ]
        
        path_str = str(path)
        for pattern in sensitive_patterns:
            if self.current_session._matches_pattern(path_str, pattern):
                return True
        return False
    
    def list_permissions(self) -> Dict[str, any]:
        """List current session permissions"""
        if not self.current_session:
            return {}
        
        return {
            'session_id': self.current_session.session_id,
            'created_at': self.current_session.created_at,
            'last_used': self.current_session.last_used,
            'allowed_paths': list(self.current_session.allowed_paths),
            'allowed_patterns': list(self.current_session.allowed_patterns),
            'read_permissions': list(self.current_session.read_permissions),
            'write_permissions': list(self.current_session.write_permissions),
            'execute_permissions': list(self.current_session.execute_permissions),
        }
    
    def clear_session(self, session_id: str = None):
        """Clear a specific session or current session"""
        if session_id:
            if session_id in self.sessions:
                del self.sessions[session_id]
                if self.current_session and self.current_session.session_id == session_id:
                    self.current_session = None
        else:
            if self.current_session:
                session_id = self.current_session.session_id
                if session_id in self.sessions:
                    del self.sessions[session_id]
                self.current_session = None
        
        self._save_sessions()
        console.print(f"✅ Session cleared: {session_id}")


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
    
    # Check session permissions
    console.print("\n🔐 Session Permission Status:")
    try:
        session_manager = SessionPermissionManager()
        if session_manager.current_session:
            perms = session_manager.list_permissions()
            console.print(f"  Active session: {perms['session_id']}")
            console.print(f"  Allowed paths: {len(perms['allowed_paths'])}")
            console.print(f"  Allowed patterns: {len(perms['allowed_patterns'])}")
            console.print(f"  Read permissions: {len(perms['read_permissions'])}")
            console.print(f"  Write permissions: {len(perms['write_permissions'])}")
        else:
            console.print("  No active session")
    except Exception as e:
        console.print(f"  ❌ Error checking sessions: {e}")
    
    console.print("\n💡 Recommendations:")
    if not status['home_writable']:
        console.print("  - Check home directory permissions")
        console.print("  - Consider running: chmod 755 ~")
    
    if not status['temp_writable']:
        console.print("  - Check temp directory permissions")
        console.print("  - May need system administrator assistance")
    
    console.print("  - 2DO will automatically use fallback directories if needed")
    console.print("  - Run '2do --fix-permissions' to attempt automatic fixes")
    console.print("  - Use session permissions for enhanced security")


def get_session_permission_manager(config_dir: Optional[Path] = None) -> SessionPermissionManager:
    """Get a session-based permission manager instance"""
    return SessionPermissionManager(config_dir)


if __name__ == "__main__":
    diagnose_permissions()
