#!/usr/bin/env python3
"""
Test script for 2DO installation system.
Tests the curl-based installation functionality.
"""

import subprocess
import tempfile
import os
import sys
import shutil
from pathlib import Path

def run_command(command, shell=True, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_installation_scripts():
    """Test the installation scripts."""
    print("🧪 Testing 2DO Installation System")
    print("=" * 50)
    
    repo_root = Path(__file__).parent
    install_sh = repo_root / "install.sh"
    install_ps1 = repo_root / "install.ps1"
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Check files exist
    total_tests += 1
    print(f"\n{total_tests}. Testing installation files exist...")
    if install_sh.exists() and install_sh.is_file():
        print("   ✅ install.sh exists")
        if os.access(install_sh, os.X_OK):
            print("   ✅ install.sh is executable")
            tests_passed += 1
        else:
            print("   ❌ install.sh is not executable")
    else:
        print("   ❌ install.sh not found")
    
    if install_ps1.exists():
        print("   ✅ install.ps1 exists")
    else:
        print("   ❌ install.ps1 not found")
    
    # Test 2: Syntax validation
    total_tests += 1
    print(f"\n{total_tests}. Testing script syntax...")
    success, stdout, stderr = run_command(f"bash -n {install_sh}")
    if success:
        print("   ✅ install.sh syntax is valid")
        tests_passed += 1
    else:
        print(f"   ❌ install.sh syntax error: {stderr}")
    
    # Test 3: Test function extraction
    total_tests += 1
    print(f"\n{total_tests}. Testing function definitions...")
    
    # Extract functions without running the script
    test_script = '''
    source install.sh
    
    # Override main to prevent execution
    main() { :; }
    
    # Test functions exist
    if declare -f detect_os >/dev/null; then
        echo "detect_os function defined"
    fi
    
    if declare -f check_python >/dev/null; then
        echo "check_python function defined"
    fi
    
    if declare -f install_2do >/dev/null; then
        echo "install_2do function defined"
    fi
    
    # Test OS detection
    os_type=$(detect_os)
    echo "detected_os: $os_type"
    '''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        success, stdout, stderr = run_command(f"cd {repo_root} && bash {test_file}")
        if success and "detect_os function defined" in stdout:
            print("   ✅ Installation script functions are properly defined")
            tests_passed += 1
        else:
            print(f"   ❌ Function test failed: {stderr}")
    finally:
        os.unlink(test_file)
    
    # Test 4: Package configuration
    total_tests += 1
    print(f"\n{total_tests}. Testing package configuration...")
    pyproject_toml = repo_root / "pyproject.toml"
    
    if pyproject_toml.exists():
        content = pyproject_toml.read_text()
        if 'name = "2do"' in content and '[project.scripts]' in content:
            print("   ✅ pyproject.toml is correctly configured")
            tests_passed += 1
        else:
            print("   ❌ pyproject.toml missing required sections")
    else:
        print("   ❌ pyproject.toml not found")
    
    # Test 5: Documentation
    total_tests += 1
    print(f"\n{total_tests}. Testing documentation...")
    readme = repo_root / "README.md"
    
    if readme.exists():
        content = readme.read_text()
        if "curl" in content and "install.sh" in content and "iwr" in content and "install.ps1" in content:
            print("   ✅ README contains installation instructions")
            tests_passed += 1
        else:
            print("   ❌ README missing curl installation instructions")
    else:
        print("   ❌ README.md not found")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        print("\n📋 Installation commands ready:")
        print("\n   🐧 Unix/Linux/macOS:")
        print("   curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash")
        print("\n   🪟 Windows (PowerShell):")
        print("   iwr -useb https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.ps1 | iex")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = test_installation_scripts()
    sys.exit(0 if success else 1)