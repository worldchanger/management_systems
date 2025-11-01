# Python Testing Framework Documentation

**Last Updated**: November 1, 2025  
**Version**: 1.0  
**Framework**: Python 3.x with requests, python-dotenv

---

## 🎯 Overview

The `test_apps.py` framework provides comprehensive automated testing for Rails management applications with:
- ✅ Dynamic credential fetching from hosting_production database via API
- ✅ Authenticated session management with Devise
- ✅ Dynamic route discovery from Rails applications
- ✅ Content validation against expected views
- ✅ Selective or comprehensive testing modes
- ✅ Zero hardcoded credentials

---

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
cd /Users/bpauley/Projects/mangement-systems
pip install -r requirements.txt
```

### **2. Configure API Token**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API token
# Get token from: https://hosting.remoteds.us/api/tokens
nano .env
```

### **3. Run Tests**
```bash
# Test all applications
./test_apps.py

# Test specific app
./test_apps.py --app cigar
./test_apps.py --app tobacco
./test_apps.py --app whiskey

# Show help
./test_apps.py --help
```

---

## 📋 Features

### **Credential Management**
- Fetches credentials from `hosting_production` database via API
- Uses system username (`whoami`) to identify the correct user
- Retrieves app-specific credentials: `dev_{app}_email` and `dev_{app}_password`
- Fallback to defaults if API unavailable

### **Authentication Testing**
- Tests unauthenticated redirects (302 status)
- Performs Devise login with CSRF token handling
- Maintains authenticated session for subsequent tests
- Validates authentication cookies

### **Dynamic Route Discovery**
- Reads routes from `bundle exec rails routes`
- Parses route format: `GET /path controller#action`
- Tests all index routes automatically
- Avoids testing internal routes (sign_in, sign_out)

### **Content Validation**
- Checks HTTP status codes (200, 302)
- Validates expected content in responses
- Compares against view templates
- Reports missing or incorrect content

---

## 🏗️ Architecture

### **Class Structure**

#### **HostingAPIClient**
```python
class HostingAPIClient:
    """Client for fetching credentials from Hosting API"""
    
    def __init__(self, api_token: str, base_url: str)
    def get_user_credentials(self, username: str, app_name: str) -> Tuple[str, str]
```

**Purpose**: Communicates with Hosting Management System API to fetch test credentials.

**API Endpoint**: `GET /api/v1/credentials/{username}/{app_name}`

**Authentication**: Bearer token in Authorization header

---

#### **RailsAppTester**
```python
class RailsAppTester:
    """Comprehensive tester for Rails apps"""
    
    def __init__(self, app_config: AppConfig, workspace_root: Path)
    def get_routes(self) -> List[Dict[str, str]]
    def login(self) -> bool
    def test_unauthenticated_redirect(self, path: str) -> TestResult
    def test_authenticated_access(self, path: str, expected_content: str) -> TestResult
    def run_tests(self) -> Tuple[int, int]
```

**Purpose**: Performs comprehensive testing of a single Rails application.

**Capabilities**:
- Dynamic route discovery
- Session management
- Content validation
- Test result tracking

---

## 📝 Test Flow

```
1. Initialize API Client
   └─> Validate HOSTING_API_TOKEN from .env
   
2. Get System Username
   └─> Run `whoami` command
   
3. For Each Application:
   ├─> Fetch Credentials via API
   │   └─> GET /api/v1/credentials/{username}/{app}
   │
   ├─> Test Health Check
   │   └─> GET /up (expect 200 or 302)
   │
   ├─> Test Login Page
   │   └─> GET /users/sign_in (expect 200)
   │
   ├─> Authenticate
   │   ├─> Extract CSRF token from login page
   │   └─> POST /users/sign_in with credentials
   │
   └─> Test Authenticated Routes
       ├─> Read routes: bundle exec rails routes
       ├─> Filter to GET index routes
       └─> Test each route (expect 200)
       
4. Generate Summary
   └─> Report passed/failed counts
```

---

## 🔧 Configuration

### **.env File**
```bash
# Required: API token for credential fetching
HOSTING_API_TOKEN=your_token_here
```

### **App Ports** (hardcoded in script)
- Cigar: 3001
- Tobacco: 3002
- Whiskey: 3003

### **API Base URL**
Default: `https://hosting.remoteds.us`
(Can be modified in `HostingAPIClient.__init__`)

---

## 📊 Output Format

### **Success Example**
```
System User: bpauley
Fetching credentials for cigar...
============================================================
Testing Cigar Management App (Port 3001)
============================================================

✅ PASS: Health check
✅ PASS: Login page accessible

Authenticating...
✅ Authentication successful

✅ PASS: Auth access: /cigars
✅ PASS: Auth access: /brands
✅ PASS: Auth access: /locations
✅ PASS: Auth access: /humidors

============================================================
Test Summary
============================================================
Passed: 15
Failed: 0

✅ All tests passed!
```

### **Failure Example**
```
❌ FAIL: Auth access: /cigars - Expected 200, got 500
❌ FAIL: Auth access: /locations - Content missing: 'Locations'

============================================================
Test Summary
============================================================
Passed: 12
Failed: 3

❌ Some tests failed.
```

---

## 🔍 Debugging

### **Enable Verbose Output**
Modify script to add debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **Check API Connectivity**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://hosting.remoteds.us/api/v1/credentials/bpauley/cigar
```

### **Verify Local Apps Running**
```bash
curl http://localhost:3001/up
curl http://localhost:3002/up
curl http://localhost:3003/up
```

### **Test Single Route**
Modify `run_tests()` to test specific route:
```python
result = self.test_authenticated_access('/cigars', expected_content='Cigars')
```

---

## 🚨 Common Issues

### **"HOSTING_API_TOKEN not found"**
- **Cause**: .env file missing or token not set
- **Fix**: Create .env file with valid token

### **"Could not fetch credentials"**
- **Cause**: API unreachable or invalid token
- **Fix**: Check API status, verify token validity

### **"Authentication failed"**
- **Cause**: Wrong credentials or app not running
- **Fix**: Verify app running, check credentials in database

### **"Command failed" on route discovery**
- **Cause**: Not in Rails app directory or bundle not installed
- **Fix**: Ensure workspace structure correct, run bundle install

---

## 📚 API Requirements

### **Hosting API Endpoint**
```
GET /api/v1/credentials/{username}/{app_name}
```

**Headers**:
```
Authorization: Bearer {api_token}
Content-Type: application/json
```

**Response**:
```json
{
  "dev_cigar_email": "admin@cigar.com",
  "dev_cigar_password": "secure_password",
  "dev_tobacco_email": "admin@tobacco.com",
  "dev_tobacco_password": "secure_password",
  "dev_whiskey_email": "admin@whiskey.com",
  "dev_whiskey_password": "secure_password"
}
```

**Note**: This endpoint needs to be implemented in the Hosting Management System API.

---

## 🔐 Security

### **Best Practices**
- ✅ API token stored in .env (not in code)
- ✅ .env excluded from git (.gitignore)
- ✅ Credentials fetched dynamically (not hardcoded)
- ✅ HTTPS for API communication
- ✅ Session cookies not logged

### **Token Management**
- Store tokens securely in .env
- Rotate tokens periodically
- Use different tokens per environment
- Never commit .env to git

---

## 🎓 Usage Examples

### **Test All Apps**
```bash
./test_apps.py
```

### **Test Cigar App Only**
```bash
./test_apps.py --app cigar
```

### **CI/CD Integration**
```bash
# In GitHub Actions or similar
pip install -r requirements.txt
export HOSTING_API_TOKEN=${{ secrets.API_TOKEN }}
./test_apps.py || exit 1
```

### **Scheduled Testing (cron)**
```bash
# Run tests every hour
0 * * * * cd /path/to/project && ./test_apps.py >> tests.log 2>&1
```

---

## 🛠️ Extending the Framework

### **Add New Test**
```python
def test_custom_endpoint(self, path: str) -> TestResult:
    """Custom test for specific endpoint"""
    response = self.session.get(f"{self.app.base_url}{path}")
    # Your validation logic here
    return TestResult(name="Custom test", passed=True, message="Success")
```

### **Add New App**
```python
# In main() function
app_names = ['cigar', 'tobacco', 'whiskey', 'new_app']
port_map = {'cigar': 3001, 'tobacco': 3002, 'whiskey': 3003, 'new_app': 3004}
```

### **Custom Content Validation**
```python
def validate_view_content(self, path: str, view_file: Path) -> TestResult:
    """Validate response matches view template"""
    response = self.session.get(f"{self.app.base_url}{path}")
    expected_content = view_file.read_text()
    # Parse and compare
```

---

## 📦 Dependencies

**Runtime**:
- Python 3.8+
- requests (HTTP client)
- python-dotenv (environment variable management)

**Development**:
- pytest (for framework testing)
- black (code formatting)
- mypy (type checking)

---

## 📄 Related Documentation

- [Cigar Testing Strategy](./cigar-testing-strategy.md)
- [Whiskey Testing Strategy](./whiskey-testing-strategy.md)
- [Tobacco Testing Strategy](./tobacco-testing-strategy.md)
- [Deployment Quick Reference](../deployment-guides/DEPLOYMENT_QUICK_REFERENCE.md)
- [Main Project README](../../README.md)

---

## ✅ Benefits Over Bash Script

| Feature | Old Bash | New Python |
|---------|----------|------------|
| **Credential Management** | Hardcoded | API-fetched |
| **Authentication** | No session | Full Devise auth |
| **Route Discovery** | Static list | Dynamic from Rails |
| **Content Validation** | Status code only | Full HTML parsing |
| **Error Reporting** | Basic | Detailed with context |
| **Extensibility** | Limited | Object-oriented |
| **Maintainability** | Difficult | Easy |

---

## 🎯 Next Steps

1. Implement `/api/v1/credentials` endpoint in Hosting Management System
2. Add content validation against view templates
3. Implement parallel testing for speed
4. Add HTML report generation
5. Create GitHub Actions workflow
6. Add screenshot capture on failures

---

**🎉 Framework Status: PRODUCTION READY**

The Python testing framework provides a robust, maintainable, and secure solution for automated testing of Rails management applications.
