#!/bin/bash
# Local App Testing Script (Darwin/Mac - Development Environment)
# Tests all Rails apps on localhost with http

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FAILED_TESTS=0
PASSED_TESTS=0

# Test result tracking
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Test a URL and check for expected status or content
test_url() {
    local url=$1
    local expected_status=$2
    local description=$3
    local follow_redirects=${4:-false}
    
    if [ "$follow_redirects" = "true" ]; then
        response=$(curl -sL -w "%{http_code}" -o /dev/null "$url" 2>/dev/null || echo "000")
    else
        response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null || echo "000")
    fi
    
    if [ "$response" = "$expected_status" ]; then
        test_result 0 "$description (Status: $response)"
    else
        test_result 1 "$description (Expected: $expected_status, Got: $response)"
    fi
}

# Test that URL contains specific content
test_content() {
    local url=$1
    local search_string=$2
    local description=$3
    
    content=$(curl -sL "$url" 2>/dev/null || echo "")
    if echo "$content" | grep -q "$search_string"; then
        test_result 0 "$description"
    else
        test_result 1 "$description (Content not found: $search_string)"
    fi
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Local App Testing (Development)${NC}"
echo -e "${BLUE}  Environment: http://localhost${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# CIGAR APP TESTS
echo -e "${YELLOW}📦 Testing Cigar Management App (Port 3001)${NC}"
echo ""

test_url "http://localhost:3001/up" "200" "Cigar - Health check"
test_url "http://localhost:3001/users/sign_in" "200" "Cigar - Login page accessible"
test_url "http://localhost:3001/dashboard" "302" "Cigar - Dashboard requires auth (redirect)"
test_url "http://localhost:3001/cigars" "302" "Cigar - Cigars index requires auth"
test_url "http://localhost:3001/brands" "302" "Cigar - Brands index requires auth"
test_url "http://localhost:3001/humidors" "302" "Cigar - Humidors index requires auth"
test_url "http://localhost:3001/locations" "302" "Cigar - Locations index requires auth"

echo ""

# TOBACCO APP TESTS
echo -e "${YELLOW}🌿 Testing Tobacco Management App (Port 3002)${NC}"
echo ""

test_url "http://localhost:3002/up" "200" "Tobacco - Health check"
test_url "http://localhost:3002/users/sign_in" "200" "Tobacco - Login page accessible"
test_url "http://localhost:3002/dashboard" "302" "Tobacco - Dashboard requires auth (redirect)"
test_url "http://localhost:3002/tobacco_products" "302" "Tobacco - Products index requires auth"
test_url "http://localhost:3002/brands" "302" "Tobacco - Brands index requires auth"
test_url "http://localhost:3002/storages" "302" "Tobacco - Storages index requires auth"
test_url "http://localhost:3002/locations" "302" "Tobacco - Locations index requires auth"

echo ""

# WHISKEY APP TESTS
echo -e "${YELLOW}🥃 Testing Whiskey Management App (Port 3003)${NC}"
echo ""

test_url "http://localhost:3003/up" "200" "Whiskey - Health check"
test_url "http://localhost:3003/users/sign_in" "200" "Whiskey - Login page accessible"
test_url "http://localhost:3003/dashboard" "302" "Whiskey - Dashboard requires auth (redirect)"
test_url "http://localhost:3003/whiskeys" "302" "Whiskey - Whiskeys index requires auth"
test_url "http://localhost:3003/brands" "302" "Whiskey - Brands index requires auth"
test_url "http://localhost:3003/whiskey_types" "302" "Whiskey - Types index requires auth"
test_url "http://localhost:3003/locations" "302" "Whiskey - Locations index requires auth"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  Passed: $PASSED_TESTS${NC}"
echo -e "${RED}  Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All local tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review errors above.${NC}"
    exit 1
fi
