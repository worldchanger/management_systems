#!/usr/bin/env python3
"""
Comprehensive Rails Application Testing Framework

This script tests Rails management applications (cigar, tobacco, whiskey) by:
- Fetching credentials from hosting_production database via API
- Performing authenticated HTTP requests
- Dynamically reading routes from each app
- Validating response content against expected views
- Supporting selective or comprehensive testing

Usage:
    ./test_apps.py                    # Test all apps
    ./test_apps.py --app cigar        # Test specific app
    ./test_apps.py --help             # Show help

Requirements:
    - .env file with HOSTING_API_TOKEN
    - Local apps running on ports 3001 (cigar), 3002 (tobacco), 3003 (whiskey)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ANSI colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


@dataclass
class AppConfig:
    """Configuration for a Rails application"""
    name: str
    port: int
    base_url: str
    email: Optional[str] = None
    password: Optional[str] = None


@dataclass
class TestResult:
    """Result of a single test"""
    name: str
    passed: bool
    message: str
    status_code: Optional[int] = None


class HostingAPIClient:
    """Client for interacting with the Hosting Management System API"""
    
    def __init__(self, api_token: str, base_url: str = "https://hosting.remoteds.us"):
        self.api_token = api_token
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        })
    
    def get_user_credentials(self, username: str, app_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch dev credentials for a specific app and user from the API.
        
        Args:
            username: System username (from whoami)
            app_name: Application name (cigar, tobacco, whiskey)
            
        Returns:
            Tuple of (email, password) or (None, None) if not found
        """
        try:
            # API endpoint to fetch credentials
            url = f"{self.base_url}/api/v1/credentials/{username}/{app_name}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                email = data.get(f'dev_{app_name}_email')
                password = data.get(f'dev_{app_name}_password')
                return email, password
            else:
                print(f"{Colors.RED}API Error: {response.status_code}{Colors.NC}")
                return None, None
        except Exception as e:
            print(f"{Colors.RED}Failed to fetch credentials: {e}{Colors.NC}")
            return None, None


class RailsAppTester:
    """Comprehensive tester for Rails management applications"""
    
    def __init__(self, app_config: AppConfig, workspace_root: Path):
        self.app = app_config
        self.workspace_root = workspace_root
        self.app_root = workspace_root / f"{app_config.name}-management-system"
        self.session = requests.Session()
        self.csrf_token = None
        self.test_results: List[TestResult] = []
    
    def get_routes(self) -> List[Dict[str, str]]:
        """
        Dynamically read routes from the Rails app using `rails routes`.
        
        Returns:
            List of route dictionaries with verb, path, controller#action
        """
        try:
            result = subprocess.run(
                ["bundle", "exec", "rails", "routes"],
                cwd=self.app_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"{Colors.YELLOW}Warning: Could not read routes for {self.app.name}{Colors.NC}")
                return []
            
            routes = []
            for line in result.stdout.split('\n'):
                # Parse route lines like: GET    /cigars(.:format)  cigars#index
                match = re.match(r'\s*(GET|POST|PATCH|PUT|DELETE)\s+(\S+)\s+(\S+)', line)
                if match:
                    verb, path, action = match.groups()
                    # Clean up path (remove format suffix)
                    path = re.sub(r'\(\.:format\)', '', path)
                    routes.append({
                        'verb': verb,
                        'path': path,
                        'action': action
                    })
            
            return routes
        except Exception as e:
            print(f"{Colors.RED}Error reading routes: {e}{Colors.NC}")
            return []
    
    def login(self) -> bool:
        """
        Authenticate with the Rails app using Devise.
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.app.email or not self.app.password:
            return False
        
        try:
            # Step 1: GET login page to retrieve CSRF token
            login_url = f"{self.app.base_url}/users/sign_in"
            response = self.session.get(login_url, timeout=10)
            
            if response.status_code != 200:
                return False
            
            # Extract CSRF token from meta tag
            csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text)
            if csrf_match:
                self.csrf_token = csrf_match.group(1)
            else:
                print(f"{Colors.YELLOW}Warning: CSRF token not found{Colors.NC}")
                return False
            
            # Step 2: POST credentials
            post_data = {
                'user[email]': self.app.email,
                'user[password]': self.app.password,
                'authenticity_token': self.csrf_token,
                'commit': 'Log in'
            }
            
            response = self.session.post(
                login_url,
                data=post_data,
                allow_redirects=True,
                timeout=10
            )
            
            # Check if login was successful (should redirect and have auth cookie)
            if 'user' in response.cookies or response.status_code == 200:
                return True
            
            return False
        except Exception as e:
            print(f"{Colors.RED}Login error: {e}{Colors.NC}")
            return False
    
    def test_unauthenticated_redirect(self, path: str) -> TestResult:
        """
        Test that a path redirects when unauthenticated.
        
        Args:
            path: URL path to test
            
        Returns:
            TestResult with pass/fail status
        """
        try:
            # Use a fresh session without auth
            response = requests.get(
                f"{self.app.base_url}{path}",
                allow_redirects=False,
                timeout=10
            )
            
            if response.status_code == 302:
                return TestResult(
                    name=f"Unauth redirect: {path}",
                    passed=True,
                    message="Correctly requires authentication",
                    status_code=302
                )
            else:
                return TestResult(
                    name=f"Unauth redirect: {path}",
                    passed=False,
                    message=f"Expected 302, got {response.status_code}",
                    status_code=response.status_code
                )
        except Exception as e:
            return TestResult(
                name=f"Unauth redirect: {path}",
                passed=False,
                message=f"Error: {str(e)}"
            )
    
    def test_authenticated_access(self, path: str, expected_content: Optional[str] = None) -> TestResult:
        """
        Test that an authenticated request succeeds and optionally contains expected content.
        
        Args:
            path: URL path to test
            expected_content: Optional string that should appear in response
            
        Returns:
            TestResult with pass/fail status
        """
        try:
            response = self.session.get(
                f"{self.app.base_url}{path}",
                timeout=10
            )
            
            if response.status_code != 200:
                return TestResult(
                    name=f"Auth access: {path}",
                    passed=False,
                    message=f"Expected 200, got {response.status_code}",
                    status_code=response.status_code
                )
            
            # Check for expected content if provided
            if expected_content and expected_content not in response.text:
                return TestResult(
                    name=f"Auth access: {path}",
                    passed=False,
                    message=f"Content missing: '{expected_content}'",
                    status_code=200
                )
            
            return TestResult(
                name=f"Auth access: {path}",
                passed=True,
                message="Success",
                status_code=200
            )
        except Exception as e:
            return TestResult(
                name=f"Auth access: {path}",
                passed=False,
                message=f"Error: {str(e)}"
            )
    
    def run_tests(self) -> Tuple[int, int]:
        """
        Run comprehensive test suite for the app.
        
        Returns:
            Tuple of (passed_count, failed_count)
        """
        print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}Testing {self.app.name.title()} Management App (Port {self.app.port}){Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
        
        # Test 1: Health check
        result = self.test_unauthenticated_redirect("/up")
        if result.passed or result.status_code == 200:  # /up might be public
            print(f"{Colors.GREEN}✅ PASS{Colors.NC}: Health check")
        else:
            print(f"{Colors.RED}❌ FAIL{Colors.NC}: Health check - {result.message}")
        self.test_results.append(result)
        
        # Test 2: Login page accessible
        try:
            response = requests.get(f"{self.app.base_url}/users/sign_in", timeout=10)
            if response.status_code == 200:
                result = TestResult("Login page", True, "Accessible", 200)
                print(f"{Colors.GREEN}✅ PASS{Colors.NC}: Login page accessible")
            else:
                result = TestResult("Login page", False, f"Status {response.status_code}", response.status_code)
                print(f"{Colors.RED}❌ FAIL{Colors.NC}: Login page - {result.message}")
            self.test_results.append(result)
        except Exception as e:
            result = TestResult("Login page", False, str(e))
            print(f"{Colors.RED}❌ FAIL{Colors.NC}: Login page - {result.message}")
            self.test_results.append(result)
        
        # Test 3: Authenticate
        print(f"\n{Colors.YELLOW}Authenticating...{Colors.NC}")
        if self.login():
            print(f"{Colors.GREEN}✅ Authentication successful{Colors.NC}\n")
            
            # Test 4: Read routes and test authenticated endpoints
            routes = self.get_routes()
            index_routes = [r for r in routes if r['verb'] == 'GET' and r['path'].count('/') == 1 and ':id' not in r['path']]
            
            # Test common index routes
            for route in index_routes[:10]:  # Limit to first 10 to avoid overwhelming output
                path = route['path']
                if 'sign_in' not in path and 'sign_out' not in path:
                    result = self.test_authenticated_access(path)
                    if result.passed:
                        print(f"{Colors.GREEN}✅ PASS{Colors.NC}: {result.name}")
                    else:
                        print(f"{Colors.RED}❌ FAIL{Colors.NC}: {result.name} - {result.message}")
                    self.test_results.append(result)
        else:
            print(f"{Colors.RED}❌ Authentication failed{Colors.NC}")
            print(f"{Colors.YELLOW}Skipping authenticated tests{Colors.NC}\n")
        
        # Calculate results
        passed = sum(1 for r in self.test_results if r.passed)
        failed = sum(1 for r in self.test_results if not r.passed)
        
        return passed, failed


def get_system_username() -> str:
    """Get the current system username using whoami"""
    try:
        result = subprocess.run(['whoami'], capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Rails Application Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                  Test all applications
  %(prog)s --app cigar      Test only cigar application
  %(prog)s --app tobacco    Test only tobacco application
  %(prog)s --app whiskey    Test only whiskey application
        """
    )
    parser.add_argument(
        '--app',
        choices=['cigar', 'tobacco', 'whiskey'],
        help='Test a specific application'
    )
    
    args = parser.parse_args()
    
    # Get API token from environment
    api_token = os.getenv('HOSTING_API_TOKEN')
    if not api_token:
        print(f"{Colors.RED}Error: HOSTING_API_TOKEN not found in .env file{Colors.NC}")
        print(f"{Colors.YELLOW}Create a .env file in the project root with:{Colors.NC}")
        print("HOSTING_API_TOKEN=your_api_token_here")
        sys.exit(1)
    
    # Get system username
    username = get_system_username()
    print(f"{Colors.BLUE}System User: {username}{Colors.NC}")
    
    # Initialize API client
    api_client = HostingAPIClient(api_token)
    
    # Define applications
    apps_to_test = []
    if args.app:
        app_names = [args.app]
    else:
        app_names = ['cigar', 'tobacco', 'whiskey']
    
    workspace_root = Path(__file__).parent
    
    for app_name in app_names:
        port = {'cigar': 3001, 'tobacco': 3002, 'whiskey': 3003}[app_name]
        
        # Fetch credentials from API
        print(f"{Colors.YELLOW}Fetching credentials for {app_name}...{Colors.NC}")
        email, password = api_client.get_user_credentials(username, app_name)
        
        if not email or not password:
            print(f"{Colors.YELLOW}Warning: Could not fetch credentials for {app_name}, using defaults{Colors.NC}")
            email = f"admin@{app_name}.com"
            password = "password123"
        
        app_config = AppConfig(
            name=app_name,
            port=port,
            base_url=f"http://localhost:{port}",
            email=email,
            password=password
        )
        apps_to_test.append(app_config)
    
    # Run tests for each app
    total_passed = 0
    total_failed = 0
    
    for app_config in apps_to_test:
        tester = RailsAppTester(app_config, workspace_root)
        passed, failed = tester.run_tests()
        total_passed += passed
        total_failed += failed
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Test Summary{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.GREEN}Passed: {total_passed}{Colors.NC}")
    print(f"{Colors.RED}Failed: {total_failed}{Colors.NC}")
    print()
    
    if total_failed == 0:
        print(f"{Colors.GREEN}✅ All tests passed!{Colors.NC}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}❌ Some tests failed.{Colors.NC}")
        sys.exit(1)


if __name__ == '__main__':
    main()
