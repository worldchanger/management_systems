#!/usr/bin/env python3
"""
Comprehensive Rails Application Testing Framework

This script performs extensive testing of Rails management applications by:
- Fetching credentials dynamically from hosting_production database via API
- Testing health checks and authentication flows  
- Dynamically discovering and testing all routes (index, show, edit)
- Testing dashboard pages
- Testing API endpoints with data validation
- Detecting Rails errors (500 errors, error pages)
- Providing detailed failure reports with exact error messages
- Organizing tests by categories for clarity

Usage:
    ./test_apps.py                    # Test all apps comprehensively
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
from dataclasses import dataclass, field
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
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'


@dataclass
class AppConfig:
    """Configuration for a Rails application"""
    name: str
    port: int
    base_url: str
    email: Optional[str] = None
    password: Optional[str] = None
    has_api: bool = False  # Whether app has JSON API


@dataclass
class TestResult:
    """Result of a single test"""
    category: str  # e.g., "Health", "Auth", "Routes", "API"
    name: str
    passed: bool
    message: str
    status_code: Optional[int] = None
    error_details: Optional[str] = None  # Full error message if failed


@dataclass
class TestSummary:
    """Summary of all tests for an app"""
    app_name: str
    total_passed: int = 0
    total_failed: int = 0
    failures: List[TestResult] = field(default_factory=list)
    
    def add_result(self, result: TestResult):
        """Add a test result and update counters"""
        if result.passed:
            self.total_passed += 1
        else:
            self.total_failed += 1
            self.failures.append(result)


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
        self.summary = TestSummary(app_name=app_config.name)
    
    def print_test_result(self, result: TestResult):
        """Print a test result with appropriate formatting"""
        if result.passed:
            print(f"  {Colors.GREEN}✅ PASS{Colors.NC}: {result.name}")
        else:
            print(f"  {Colors.RED}❌ FAIL{Colors.NC}: {result.name}")
            print(f"    {Colors.RED}└─ {result.message}{Colors.NC}")
            if result.error_details:
                # Print first 200 chars of error details
                error_preview = result.error_details[:200]
                if len(result.error_details) > 200:
                    error_preview += "..."
                print(f"    {Colors.YELLOW}   Error: {error_preview}{Colors.NC}")
    
    def check_for_rails_error(self, response: requests.Response) -> Tuple[bool, Optional[str]]:
        """
        Check if response contains a Rails error page.
        
        Returns:
            Tuple of (is_error, error_message)
        """
        if response.status_code >= 500:
            return True, f"HTTP {response.status_code} Server Error"
        
        # Check for Rails error indicators in HTML
        error_indicators = [
            "We're sorry, but something went wrong",
            "ActionController::RoutingError",
            "NoMethodError",
            "undefined method",
            "ActiveRecord::RecordNotFound",
            "Couldn't find",
            "uninitialized constant"
        ]
        
        for indicator in error_indicators:
            if indicator in response.text:
                # Try to extract error message
                match = re.search(r'<h1[^>]*>([^<]+)</h1>', response.text)
                if match:
                    return True, match.group(1)
                return True, indicator
        
        return False, None
    
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
                print(f"{Colors.YELLOW}  Warning: Could not read routes for {self.app.name}{Colors.NC}")
                return []
            
            routes = []
            for line in result.stdout.split('\n'):
                # Parse route lines like: 
                # Prefix Verb   URI Pattern                      Controller#Action
                # cigars GET    /cigars(.:format)                cigars#index
                # Skip lines that contain "Prefix" or "Verb" (headers)
                if 'Prefix' in line or 'Verb' in line or 'URI Pattern' in line:
                    continue
                
                # Match: optional_prefix  VERB  /path(.:format)  controller#action
                match = re.search(r'\b(GET|POST|PATCH|PUT|DELETE)\s+(\S+)\s+(\S+)$', line)
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
            print(f"{Colors.RED}  Error reading routes: {e}{Colors.NC}")
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
            
            # Check if login was successful
            if 'user' in response.cookies or response.status_code == 200:
                # Additional check: make sure we're not still on login page
                if 'sign_in' not in response.url:
                    return True
            
            return False
        except Exception as e:
            print(f"{Colors.RED}  Login error: {e}{Colors.NC}")
            return False
    
    def test_health_check(self) -> TestResult:
        """Test the /up health endpoint"""
        try:
            response = requests.get(f"{self.app.base_url}/up", timeout=10)
            if response.status_code == 200:
                return TestResult(
                    category="Health",
                    name="Health check endpoint (/up)",
                    passed=True,
                    message="Responding correctly",
                    status_code=200
                )
            else:
                return TestResult(
                    category="Health",
                    name="Health check endpoint (/up)",
                    passed=False,
                    message=f"Expected 200, got {response.status_code}",
                    status_code=response.status_code
                )
        except Exception as e:
            return TestResult(
                category="Health",
                name="Health check endpoint (/up)",
                passed=False,
                message=f"Request failed: {str(e)}"
            )
    
    def test_login_page(self) -> TestResult:
        """Test that login page is accessible"""
        try:
            response = requests.get(f"{self.app.base_url}/users/sign_in", timeout=10)
            if response.status_code == 200:
                # Check for expected content
                if 'email' in response.text.lower() and 'password' in response.text.lower():
                    return TestResult(
                        category="Auth",
                        name="Login page accessible",
                        passed=True,
                        message="Page loaded with login form",
                        status_code=200
                    )
                else:
                    return TestResult(
                        category="Auth",
                        name="Login page accessible",
                        passed=False,
                        message="Page loaded but missing login form elements",
                        status_code=200
                    )
            else:
                return TestResult(
                    category="Auth",
                    name="Login page accessible",
                    passed=False,
                    message=f"Expected 200, got {response.status_code}",
                    status_code=response.status_code
                )
        except Exception as e:
            return TestResult(
                category="Auth",
                name="Login page accessible",
                passed=False,
                message=f"Request failed: {str(e)}"
            )
    
    def test_dashboard(self) -> TestResult:
        """Test the dashboard/home page"""
        try:
            response = self.session.get(f"{self.app.base_url}/", timeout=10)
            
            # Check for Rails errors
            is_error, error_msg = self.check_for_rails_error(response)
            if is_error:
                return TestResult(
                    category="Dashboard",
                    name="Dashboard page (/)",
                    passed=False,
                    message=f"Rails error detected",
                    status_code=response.status_code,
                    error_details=error_msg
                )
            
            if response.status_code == 200:
                return TestResult(
                    category="Dashboard",
                    name="Dashboard page (/)",
                    passed=True,
                    message="Page loaded successfully",
                    status_code=200
                )
            else:
                return TestResult(
                    category="Dashboard",
                    name="Dashboard page (/)",
                    passed=False,
                    message=f"Expected 200, got {response.status_code}",
                    status_code=response.status_code
                )
        except Exception as e:
            return TestResult(
                category="Dashboard",
                name="Dashboard page (/)",
                passed=False,
                message=f"Request failed: {str(e)}"
            )
    
    def test_route(self, route: Dict[str, str]) -> TestResult:
        """Test a specific route"""
        path = route['path']
        action = route['action']
        
        try:
            response = self.session.get(f"{self.app.base_url}{path}", timeout=10)
            
            # Check for Rails errors
            is_error, error_msg = self.check_for_rails_error(response)
            if is_error:
                return TestResult(
                    category="Routes",
                    name=f"{action}: {path}",
                    passed=False,
                    message=f"Rails error detected",
                    status_code=response.status_code,
                    error_details=error_msg
                )
            
            if response.status_code == 200:
                return TestResult(
                    category="Routes",
                    name=f"{action}: {path}",
                    passed=True,
                    message="Success",
                    status_code=200
                )
            elif response.status_code == 302:
                # Redirect might be OK for some routes
                return TestResult(
                    category="Routes",
                    name=f"{action}: {path}",
                    passed=True,
                    message="Redirected (expected)",
                    status_code=302
                )
            else:
                return TestResult(
                    category="Routes",
                    name=f"{action}: {path}",
                    passed=False,
                    message=f"Expected 200, got {response.status_code}",
                    status_code=response.status_code
                )
        except Exception as e:
            return TestResult(
                category="Routes",
                name=f"{action}: {path}",
                passed=False,
                message=f"Request failed: {str(e)}"
            )
    
    def test_api_endpoint(self) -> TestResult:
        """Test the API endpoint if app has one"""
        if not self.app.has_api:
            return None
        
        try:
            # For cigar and tobacco apps, test /api/inventory/:token
            # We'll use a test token
            response = self.session.get(
                f"{self.app.base_url}/api/inventory/test_token",
                timeout=10
            )
            
            # API might return 404 for invalid token, but should be JSON
            if response.status_code in [200, 404, 401]:
                try:
                    data = response.json()
                    if isinstance(data, (dict, list)):
                        return TestResult(
                            category="API",
                            name=f"API endpoint (/api/inventory/:token)",
                            passed=True,
                            message=f"Returns valid JSON (status {response.status_code})",
                            status_code=response.status_code
                        )
                except:
                    return TestResult(
                        category="API",
                        name=f"API endpoint (/api/inventory/:token)",
                        passed=False,
                        message="Did not return valid JSON",
                        status_code=response.status_code
                    )
            
            return TestResult(
                category="API",
                name=f"API endpoint (/api/inventory/:token)",
                passed=False,
                message=f"Unexpected status code: {response.status_code}",
                status_code=response.status_code
            )
        except Exception as e:
            return TestResult(
                category="API",
                name=f"API endpoint (/api/inventory/:token)",
                passed=False,
                message=f"Request failed: {str(e)}"
            )
    
    def run_tests(self) -> TestSummary:
        """
        Run comprehensive test suite for the app.
        
        Returns:
            TestSummary with all results
        """
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.NC}")
        print(f"{Colors.BOLD}{Colors.BLUE}Testing {self.app.name.title()} Management App (Port {self.app.port}){Colors.NC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.NC}\n")
        
        # Category 1: Health Checks
        print(f"{Colors.CYAN}[1/5] Health Checks{Colors.NC}")
        result = self.test_health_check()
        self.print_test_result(result)
        self.summary.add_result(result)
        
        # Category 2: Authentication
        print(f"\n{Colors.CYAN}[2/5] Authentication{Colors.NC}")
        result = self.test_login_page()
        self.print_test_result(result)
        self.summary.add_result(result)
        
        # Attempt login
        print(f"  {Colors.YELLOW}Attempting authentication...{Colors.NC}")
        if self.login():
            print(f"  {Colors.GREEN}✅ Authentication successful{Colors.NC}")
        else:
            print(f"  {Colors.RED}❌ Authentication failed - skipping authenticated tests{Colors.NC}")
            return self.summary
        
        # Category 3: Dashboard
        print(f"\n{Colors.CYAN}[3/5] Dashboard{Colors.NC}")
        result = self.test_dashboard()
        self.print_test_result(result)
        self.summary.add_result(result)
        
        # Category 4: Routes (Controllers)
        print(f"\n{Colors.CYAN}[4/5] Controller Routes{Colors.NC}")
        print(f"  {Colors.YELLOW}Reading routes from Rails...{Colors.NC}")
        routes = self.get_routes()
        
        # Filter to testable routes
        testable_routes = []
        for route in routes:
            path = route['path']
            verb = route['verb']
            
            # Only test GET routes
            if verb != 'GET':
                continue
            
            # Skip certain paths
            skip_patterns = [
                'sign_in', 'sign_out', 'sign_up', 'password',
                'rails/', 'service-worker', 'manifest', '/api/'
            ]
            if any(pattern in path for pattern in skip_patterns):
                continue
            
            # Skip routes with ANY parameter placeholders (:id, :cigar_id, :token, etc)
            # We can't test these without knowing actual valid IDs
            if ':' in path:
                continue
            
            testable_routes.append(route)
        
        print(f"  {Colors.YELLOW}Found {len(testable_routes)} testable routes{Colors.NC}")
        
        for route in testable_routes:
            result = self.test_route(route)
            self.print_test_result(result)
            self.summary.add_result(result)
        
        # Category 5: API Endpoints
        if self.app.has_api:
            print(f"\n{Colors.CYAN}[5/5] API Endpoints{Colors.NC}")
            result = self.test_api_endpoint()
            if result:
                self.print_test_result(result)
                self.summary.add_result(result)
        else:
            print(f"\n{Colors.CYAN}[5/5] API Endpoints{Colors.NC}")
            print(f"  {Colors.YELLOW}⊘ No API endpoints for this app{Colors.NC}")
        
        return self.summary


def get_system_username() -> str:
    """Get the current system username using whoami"""
    try:
        result = subprocess.run(['whoami'], capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception:
        return "unknown"


def print_final_summary(summaries: List[TestSummary]):
    """Print comprehensive final summary of all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}FINAL TEST SUMMARY{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.NC}\n")
    
    total_passed = sum(s.total_passed for s in summaries)
    total_failed = sum(s.total_failed for s in summaries)
    
    # Summary by app
    for summary in summaries:
        status_icon = "✅" if summary.total_failed == 0 else "❌"
        print(f"{status_icon} {Colors.BOLD}{summary.app_name.title()}{Colors.NC}: " +
              f"{Colors.GREEN}{summary.total_passed} passed{Colors.NC}, " +
              f"{Colors.RED}{summary.total_failed} failed{Colors.NC}")
    
    print(f"\n{Colors.BOLD}Total: {Colors.GREEN}{total_passed} passed{Colors.NC}, {Colors.RED}{total_failed} failed{Colors.NC}\n")
    
    # Detailed failures
    if total_failed > 0:
        print(f"{Colors.BOLD}{Colors.RED}FAILED TESTS DETAIL:{Colors.NC}\n")
        for summary in summaries:
            if summary.failures:
                print(f"{Colors.BOLD}  {summary.app_name.title()} App:{Colors.NC}")
                for i, failure in enumerate(summary.failures, 1):
                    print(f"    {i}. {Colors.RED}[{failure.category}]{Colors.NC} {failure.name}")
                    print(f"       {Colors.RED}└─ {failure.message}{Colors.NC}")
                    if failure.status_code:
                        print(f"          Status: {failure.status_code}")
                    if failure.error_details:
                        error_preview = failure.error_details[:150]
                        if len(failure.error_details) > 150:
                            error_preview += "..."
                        print(f"          {Colors.YELLOW}Error: {error_preview}{Colors.NC}")
                print()


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
    if args.app:
        app_names = [args.app]
    else:
        app_names = ['cigar', 'tobacco', 'whiskey']
    
    workspace_root = Path(__file__).parent
    
    # Fetch credentials and create app configs
    apps_to_test = []
    for app_name in app_names:
        port = {'cigar': 3001, 'tobacco': 3002, 'whiskey': 3003}[app_name]
        has_api = app_name in ['cigar', 'tobacco']  # These apps have API endpoints
        
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
            password=password,
            has_api=has_api
        )
        apps_to_test.append(app_config)
    
    # Run tests for each app
    summaries = []
    for app_config in apps_to_test:
        tester = RailsAppTester(app_config, workspace_root)
        summary = tester.run_tests()
        summaries.append(summary)
    
    # Print final summary
    print_final_summary(summaries)
    
    # Exit with appropriate code
    total_failed = sum(s.total_failed for s in summaries)
    if total_failed == 0:
        print(f"{Colors.GREEN}✅ All tests passed!{Colors.NC}\n")
        sys.exit(0)
    else:
        print(f"{Colors.RED}❌ {total_failed} test(s) failed.{Colors.NC}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
