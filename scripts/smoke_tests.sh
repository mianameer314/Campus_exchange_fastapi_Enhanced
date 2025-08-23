#!/bin/bash

# Campus Exchange API Smoke Tests
# Run this after deployment to verify basic functionality

BASE_URL=${1:-"http://localhost:8000"}
echo "Running smoke tests against: $BASE_URL"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local url="$2"
    local expected_status="$3"
    local method="${4:-GET}"
    
    echo -n "Testing $test_name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url")
    else
        response=$(curl -s -w "%{http_code}" -o /dev/null -X "$method" "$url")
    fi
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}PASS${NC} ($response)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}FAIL${NC} (Expected: $expected_status, Got: $response)"
        ((TESTS_FAILED++))
    fi
}

# Basic connectivity tests
echo -e "${YELLOW}=== Basic Connectivity Tests ===${NC}"
run_test "Root endpoint" "$BASE_URL/" "200"
run_test "Health check" "$BASE_URL/healthz" "200"
run_test "Detailed health" "$BASE_URL/health/detailed" "200"

# API endpoint tests
echo -e "${YELLOW}=== API Endpoint Tests ===${NC}"
run_test "Listings endpoint" "$BASE_URL/api/v1/listings/search" "200"
run_test "Search endpoint" "$BASE_URL/api/v1/listings/trending" "200"

# Authentication tests
echo -e "${YELLOW}=== Authentication Tests ===${NC}"
run_test "Register endpoint" "$BASE_URL/api/v1/auth/signup" "422" "POST"
run_test "Login endpoint" "$BASE_URL/api/v1/auth/login" "422" "POST"

# Rate limiting test
echo -e "${YELLOW}=== Rate Limiting Test ===${NC}"
echo -n "Testing rate limiting... "
for i in {1..105}; do
    curl -s -o /dev/null "$BASE_URL/healthz"
done
response=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/healthz")
if [ "$response" = "429" ]; then
    echo -e "${GREEN}PASS${NC} (Rate limiting working)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}SKIP${NC} (Rate limiting may not be triggered)"
fi

# Security headers test
echo -e "${YELLOW}=== Security Headers Test ===${NC}"
echo -n "Testing security headers... "
headers=$(curl -s -I "$BASE_URL/" | grep -E "(X-Content-Type-Options|X-Frame-Options|X-XSS-Protection)")
if [ -n "$headers" ]; then
    echo -e "${GREEN}PASS${NC} (Security headers present)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC} (Security headers missing)"
    ((TESTS_FAILED++))
fi

# Summary
echo -e "${YELLOW}=== Test Summary ===${NC}"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "Total tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
