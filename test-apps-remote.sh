#!/bin/bash
# Remote App Testing Script (Linux - Production Environment)
# Tests all Rails apps on production with https

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
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((FAILED_TESTS++))
    fi
}

# Test a URL and check for expected status
test_url() {
    local url=$1
    local expected_status=$2
    local description=$3
    local follow_redirects=${4:-false}
    
    if [ "$follow_redirects" = "true" ]; then
        response=$(curl -skL -w "%{http_code}" -o /dev/null "$url" 2>/dev/null || echo "000")
    else
        response=$(curl -sk -w "%{http_code}" -o /dev/null "$url" 2>/dev/null || echo "000")
    fi
    
    if [ "$response" = "$expected_status" ]; then
        test_result 0 "$description (Status: $response)"
    else
        test_result 1 "$description (Expected: $expected_status, Got: $response)"
    fi
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Remote App Testing (Production)${NC}"
echo -e "${BLUE}  Environment: https://*.remoteds.us${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# CIGAR APP TESTS
echo -e "${YELLOW}📦 Testing Cigar Management App${NC}"
echo ""

test_url "https://cigars.remoteds.us/up" "200" "Cigar - Health check"
test_url "https://cigars.remoteds.us/users/sign_in" "200" "Cigar - Login page accessible"
test_url "https://cigars.remoteds.us/dashboard" "302" "Cigar - Dashboard requires auth (redirect)"
test_url "https://cigars.remoteds.us/cigars" "302" "Cigar - Cigars index requires auth"
test_url "https://cigars.remoteds.us/brands" "302" "Cigar - Brands index requires auth"
test_url "https://cigars.remoteds.us/humidors" "302" "Cigar - Humidors index requires auth"
test_url "https://cigars.remoteds.us/locations" "302" "Cigar - Locations index requires auth"

echo ""

# TOBACCO APP TESTS
echo -e "${YELLOW}🌿 Testing Tobacco Management App${NC}"
echo ""

test_url "https://tobacco.remoteds.us/up" "200" "Tobacco - Health check"
test_url "https://tobacco.remoteds.us/users/sign_in" "200" "Tobacco - Login page accessible"
test_url "https://tobacco.remoteds.us/dashboard" "302" "Tobacco - Dashboard requires auth (redirect)"
test_url "https://tobacco.remoteds.us/tobacco_products" "302" "Tobacco - Products index requires auth"
test_url "https://tobacco.remoteds.us/brands" "302" "Tobacco - Brands index requires auth"
test_url "https://tobacco.remoteds.us/storages" "302" "Tobacco - Storages index requires auth"
test_url "https://tobacco.remoteds.us/locations" "302" "Tobacco - Locations index requires auth"

echo ""

# WHISKEY APP TESTS
echo -e "${YELLOW}🥃 Testing Whiskey Management App${NC}"
echo ""

test_url "https://whiskey.remoteds.us/up" "200" "Whiskey - Health check"
test_url "https://whiskey.remoteds.us/users/sign_in" "200" "Whiskey - Login page accessible"
test_url "https://whiskey.remoteds.us/dashboard" "302" "Whiskey - Dashboard requires auth (redirect)"
test_url "https://whiskey.remoteds.us/whiskeys" "302" "Whiskey - Whiskeys index requires auth"
test_url "https://whiskey.remoteds.us/brands" "302" "Whiskey - Brands index requires auth"
test_url "https://whiskey.remoteds.us/whiskey_types" "302" "Whiskey - Types index requires auth"
test_url "https://whiskey.remoteds.us/locations" "302" "Whiskey - Locations index requires auth"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  Passed: $PASSED_TESTS${NC}"
echo -e "${RED}  Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All remote tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review errors above.${NC}"
    exit 1
fi
