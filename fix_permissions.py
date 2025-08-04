#!/usr/bin/env python3
"""
2DO Permission Fix Script
Ensures proper file permissions for the 2DO application
"""

import os
import sys
import stat
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def fix_directory_permissions(directory: Path, dir_mode: int = 0o755, file_mode: int = 0o644) -> bool:
    """Fix permissions for a directory and all its contents"""
    if not directory.exists():
        console.print(f"📁 Directory does not exist: {directory}")
        return True
    
    try:
        # Fix directory permission
        os.chmod(directory, dir_mode)
        
        # Recursively fix all subdirectories and files
        for root, dirs, files in os.walk(directory):
            root_path = Path(root)
            
            # Fix subdirectory permissions
            for dir_name in dirs:
                dir_path = root_path / dir_name
                try:
                    os.chmod(dir_path, dir_mode)
                except (OSError, PermissionError) as e:
                    console.print(f"⚠️ Cannot fix directory permissions for {dir_path}: {e}")
            
            # Fix file permissions
            for file_name in files:
                file_path = root_path / file_name
                try:
                    os.chmod(file_path, file_mode)
                except (OSError, PermissionError) as e:
                    console.print(f"⚠️ Cannot fix file permissions for {file_path}: {e}")
        
        console.print(f"✅ Fixed permissions for {directory}")
        return True
        
    except (OSError, PermissionError) as e:
        console.print(f"❌ Cannot fix permissions for {directory}: {e}")
        return False

def create_2do_directories():
    """Create necessary 2DO directories with proper permissions"""
    directories = [
        Path.home() / ".2do",
        Path.home() / ".2do" / "todos",
        Path.home() / ".2do" / "memory",
        Path.home() / ".2do" / "logs",
    ]
    
    # Check if we're in a git repository
    current_dir = Path.cwd()
    if (current_dir / ".git").exists():
        # Add local project directories
        directories.extend([
            current_dir / "2DO",
            current_dir / "2DO" / ".2do",
            current_dir / "2DO" / ".2do" / "todos",
            current_dir / "2DO" / ".2do" / "memory",
            current_dir / "2DO" / ".2do" / "logs",
        ])
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            os.chmod(directory, 0o755)
            console.print(f"✅ Created/verified directory: {directory}")
        except (OSError, PermissionError) as e:
            console.print(f"⚠️ Cannot create directory {directory}: {e}")

def fix_2do_permissions():
    """Fix permissions for all 2DO related directories and files"""
    console.print("🔧 Fixing 2DO file permissions...")
    
    # List of directories to fix
    directories_to_fix = [
        Path.home() / ".2do",
    ]
    
    # Check if we're in a git repository
    current_dir = Path.cwd()
    if (current_dir / ".git").exists():
        project_2do = current_dir / "2DO"
        if project_2do.exists():
            directories_to_fix.append(project_2do)
    
    success_count = 0
    total_count = len(directories_to_fix)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fixing permissions...", total=total_count)
        
        for directory in directories_to_fix:
            if fix_directory_permissions(directory):
                success_count += 1
            progress.advance(task)
    
    console.print(f"\n📊 Fixed permissions for {success_count}/{total_count} directories")
    return success_count == total_count

def check_python_executable_permissions():
    """Check if the Python executable has proper permissions"""
    python_path = Path(sys.executable)
    try:
        # Check if Python executable is accessible
        if not os.access(python_path, os.X_OK):
            console.print(f"⚠️ Python executable lacks execute permissions: {python_path}")
            return False
        
        console.print(f"✅ Python executable permissions OK: {python_path}")
        return True
        
    except Exception as e:
        console.print(f"❌ Error checking Python executable: {e}")
        return False

def check_write_permissions():
    """Check write permissions in key locations"""
    test_locations = [
        Path.home(),
        Path.cwd(),
        Path("/tmp") if Path("/tmp").exists() else Path.home(),
    ]
    
    console.print("🔍 Checking write permissions...")
    
    for location in test_locations:
        test_file = location / ".2do_permission_test"
        try:
            test_file.touch()
            test_file.unlink()
            console.print(f"✅ Write access OK: {location}")
        except (OSError, PermissionError):
            console.print(f"❌ No write access: {location}")

def main():
    """Main function to fix all 2DO permissions"""
    console.print("🚀 2DO Permission Fix Tool")
    console.print("=" * 50)
    
    # Check current user and permissions
    console.print(f"👤 Running as user: {os.getenv('USER', 'unknown')}")
    if hasattr(os, 'getuid'):
        console.print(f"🆔 User ID: {os.getuid()}")
        console.print(f"🆔 Effective User ID: {os.geteuid()}")
    
    console.print()
    
    # Step 1: Check write permissions
    check_write_permissions()
    console.print()
    
    # Step 2: Check Python executable
    check_python_executable_permissions()
    console.print()
    
    # Step 3: Create necessary directories
    console.print("📁 Creating 2DO directories...")
    create_2do_directories()
    console.print()
    
    # Step 4: Fix existing permissions
    success = fix_2do_permissions()
    console.print()
    
    # Step 5: Final verification
    console.print("🔍 Final verification...")
    
    # Import and run the permission manager diagnostics
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from twodo.permission_manager import diagnose_permissions
        diagnose_permissions()
    except ImportError as e:
        console.print(f"⚠️ Cannot import permission manager: {e}")
        console.print("💡 Make sure you're running this from the 2DO project directory")
    
    console.print()
    
    if success:
        console.print("🎉 Permission fix completed successfully!")
        console.print("💡 You can now run 2DO with proper file permissions")
    else:
        console.print("⚠️ Some permission issues could not be resolved")
        console.print("💡 You may need to run with elevated privileges or contact your system administrator")
    
    console.print("\n📋 Next steps:")
    console.print("  1. Try running: python -m twodo")
    console.print("  2. If issues persist, check your system's file permission settings")
    console.print("  3. Consider running this script with sudo if necessary (use with caution)")

if __name__ == "__main__":
    main()
