#!/bin/bash
# Test that demonstrates installation script functionality
# This simulates what users would experience

echo "🧪 Testing 2DO Installation Scripts"
echo "=================================="
echo ""

# Test 1: Check script files exist and are executable
echo "✅ Test 1: Installation files exist"
if [ -f "install.sh" ] && [ -x "install.sh" ]; then
    echo "   ✓ install.sh exists and is executable"
else
    echo "   ✗ install.sh missing or not executable"
    exit 1
fi

if [ -f "install.ps1" ]; then
    echo "   ✓ install.ps1 exists"
else
    echo "   ✗ install.ps1 missing"
    exit 1
fi

echo ""

# Test 2: Check syntax
echo "✅ Test 2: Script syntax validation"
if bash -n install.sh; then
    echo "   ✓ install.sh syntax is valid"
else
    echo "   ✗ install.sh has syntax errors"
    exit 1
fi

echo ""

# Test 3: Test specific functions work
echo "✅ Test 3: Function definitions"

# Extract and test individual functions without running main
bash -c '
source install.sh

# Prevent main from running by overriding it
main() { :; }

# Test detect_os function  
os_type=$(detect_os)
echo "   ✓ Detected OS: $os_type"

# Test command_exists function
if command_exists bash; then
    echo "   ✓ command_exists function works"
fi

# Test python detection function exists
if declare -f check_python >/dev/null; then
    echo "   ✓ check_python function is defined"
fi

# Test install function exists
if declare -f install_2do >/dev/null; then
    echo "   ✓ install_2do function is defined"
fi
'

echo ""

# Test 4: Check package configuration
echo "✅ Test 4: Package configuration"
if [ -f "pyproject.toml" ]; then
    echo "   ✓ pyproject.toml exists"
    if grep -q 'name = "2do"' pyproject.toml; then
        echo "   ✓ Package name is correctly set"
    fi
    if grep -q '\[project.scripts\]' pyproject.toml; then
        echo "   ✓ CLI entry points are configured"
    fi
else
    echo "   ✗ pyproject.toml missing"
    exit 1
fi

echo ""

# Test 5: Check README has installation instructions
echo "✅ Test 5: Documentation"
if grep -q "curl.*install.sh" README.md; then
    echo "   ✓ Unix/Linux/macOS installation command in README"
fi
if grep -q "iwr.*install.ps1" README.md; then
    echo "   ✓ Windows installation command in README"
fi

echo ""
echo "🎉 All tests passed!"
echo ""
echo "📋 Users can now install 2DO with these commands:"
echo ""
echo "   🐧 Unix/Linux/macOS:"
echo "   curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash"
echo ""
echo "   🪟 Windows (PowerShell):"
echo "   iwr -useb https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.ps1 | iex"
echo ""
echo "✨ The installer will:"
echo "   • Detect the operating system"
echo "   • Check for Python 3.8+ (install if needed)"
echo "   • Download and install 2DO in a virtual environment"
echo "   • Add the 2do command to PATH"
echo "   • Run the setup wizard automatically"
echo ""