#!/bin/bash
# Test script to verify curl pipe execution works correctly
# This test ensures the fix for issue #19 continues to work

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

echo "🧪 Testing curl pipe execution for install.sh (Issue #19 fix)"
echo ""

# Test 1: Pipe execution - the main issue that was reported
print_test "Testing pipe execution (simulating 'curl | bash')..."
result=$(timeout 5 bash -c 'cat install.sh | bash' 2>&1 | head -5)
if echo "$result" | grep -q "2DO INSTALLER"; then
    print_pass "Pipe execution works - installer header found"
else
    print_fail "Pipe execution failed - this means the curl command won't work"
    echo "Output was: $result"
    exit 1
fi

# Test 2: Direct execution should still work
print_test "Testing direct file execution..."
result=$(timeout 5 bash install.sh 2>&1 | head -5)
if echo "$result" | grep -q "2DO INSTALLER"; then
    print_pass "Direct execution works - installer header found"
else
    print_fail "Direct execution failed"
    echo "Output was: $result"
    exit 1
fi

# Test 3: Sourcing protection - main should not run when sourced
print_test "Testing sourcing protection..."
result=$(timeout 3 bash -c 'source install.sh 2>&1; echo "SOURCED_COMPLETED"' 2>&1)
if echo "$result" | grep -q "2DO INSTALLER"; then
    print_fail "Sourcing protection failed - main function ran when sourced"
    exit 1
elif echo "$result" | grep -q "SOURCED_COMPLETED"; then
    print_pass "Sourcing protection works - main function did not run when sourced"
else
    print_fail "Sourcing test inconclusive"
    exit 1
fi

echo ""
print_pass "✅ All curl pipe execution tests passed!"
echo ""
echo "The following command should now work correctly on all platforms:"
echo "curl -fsSL https://raw.githubusercontent.com/STAFE-GROUP-AB/2do-developer/main/install.sh | bash"
echo ""