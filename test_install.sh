#!/bin/bash
# Test script for installation scripts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test shell script syntax
print_test "Testing install.sh syntax..."
if bash -n install.sh; then
    print_pass "install.sh syntax is valid"
else
    print_fail "install.sh has syntax errors"
    exit 1
fi

# Test PowerShell script syntax (if pwsh is available)
if command -v pwsh >/dev/null 2>&1; then
    print_test "Testing install.ps1 syntax..."
    if pwsh -Command "Get-Content install.ps1 | Out-String | Invoke-Expression -ErrorAction Stop" >/dev/null 2>&1; then
        print_pass "install.ps1 syntax is valid"
    else
        print_fail "install.ps1 has syntax errors"
    fi
else
    print_test "PowerShell not available, skipping install.ps1 syntax test"
fi

# Test that required functions exist in shell script
print_test "Testing install.sh function definitions..."
if grep -q "detect_os()" install.sh && \
   grep -q "check_python()" install.sh && \
   grep -q "install_2do()" install.sh && \
   grep -q "main()" install.sh; then
    print_pass "All required functions are defined in install.sh"
else
    print_fail "Missing required functions in install.sh"
    exit 1
fi

# Test that pyproject.toml exists and has correct content
print_test "Testing pyproject.toml..."
if [ -f "pyproject.toml" ]; then
    if grep -q '\[project\]' pyproject.toml && \
       grep -q 'name = "2do"' pyproject.toml && \
       grep -q '\[project.scripts\]' pyproject.toml; then
        print_pass "pyproject.toml is correctly configured"
    else
        print_fail "pyproject.toml is missing required sections"
        exit 1
    fi
else
    print_fail "pyproject.toml not found"
    exit 1
fi

# Test that README has installation instructions
print_test "Testing README.md installation instructions..."
if grep -q "curl.*install.sh" README.md && \
   grep -q "iwr.*install.ps1" README.md; then
    print_pass "README.md has curl installation instructions"
else
    print_fail "README.md is missing curl installation instructions"
    exit 1
fi

echo ""
print_pass "All tests passed! ✅"
echo ""
echo -e "${BLUE}Installation commands:${NC}"
echo -e "${YELLOW}Unix/Linux/macOS:${NC}"
echo "curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash"
echo ""
echo -e "${YELLOW}Windows (PowerShell):${NC}"
echo "iwr -useb https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.ps1 | iex"
echo ""