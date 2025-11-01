# Hosting Management System (HMS) - Testing Strategy

**Last Updated**: November 1, 2025  
**Version**: 2.0 (Refactored - Links to Tests)  
**Application**: Hosting Management System  
**Production URL**: https://hosting.remoteds.us  
**Framework**: Python FastAPI with pytest

---

## 📋 Testing Status

**Note**: HMS uses Python/FastAPI, not Rails. Testing framework is pytest instead of RSpec.

**Test Command**: `cd hosting-management-system && pytest`

---

## 🎯 Overview

HMS is the deployment and management system for Rails applications. It handles:
- Application deployment via `manager.py`
- Database configuration storage
- Service management (systemd)
- Nginx configuration
- SSL certificate management
- Health monitoring

---

## 🧪 Test Files and GitHub Links

### **Core Functionality Tests**

#### Deployment Manager Tests
- **File**: `tests/test_manager.py` (to be created)
- **Tests Needed**:
  - Deploy command with --local flag
  - Deploy command with --setup flag
  - Migration-only deploys
  - Service restart logic
  - Database secret retrieval

#### Database Configuration Tests
- **File**: `tests/test_database.py` (to be created)
- **Tests Needed**:
  - Secret retrieval from hosting_production database
  - App configuration storage
  - HMS configuration storage

#### Service Management Tests
- **File**: `tests/test_services.py` (to be created)
- **Tests Needed**:
  - Systemd service file generation
  - Service start/stop/restart
  - Service status checking

---

## 🧰 Testing Dependencies

### **Required Python Packages**
```
pytest
pytest-cov
pytest-asyncio
httpx (for FastAPI testing)
```

### **Test Database**
- Uses separate test database or mocking
- Should not affect production hosting_production database

---

## 🚀 Manager.py Commands

### **Deployment Commands**

#### Deploy with Local Flag (Safe Redeploy)
```bash
cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --local
```
- Pulls latest code from GitHub
- Runs bundle install
- Runs migrations (safe, no db wipe)
- Compiles assets
- Restarts service

#### Deploy with Setup Flag (First Time)
```bash
cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --setup --local
```
- Creates database
- Sets up user
- Full initial deployment

#### Health Check
```bash
cd /opt/hosting-api && .venv/bin/python manager.py health-check --app cigar
```
- Checks service status
- Verifies database connectivity
- Confirms app responsiveness

---

## 🔍 Testing Deployment Process

### **Local Testing (Darwin/Mac)**
```bash
# Test manager.py help
python manager.py --help

# Test deploy command (dry run if available)
python manager.py deploy --app cigar --local --dry-run
```

### **Remote Testing (Linux/Production)**
```bash
# SSH to server
ssh root@asterra.remoteds.us

# Test deployment
cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --local

# Verify service status
systemctl status puma-cigar

# Check logs
journalctl -u puma-cigar -n 50
```

---

## 🗄️ Database Testing

### **Hosting Production Database**
- **Host**: asterra.remoteds.us
- **Database**: hosting_production
- **Tables**:
  - `apps` - Rails application secrets
  - `hms_config` - HMS configuration

### **Test Queries**
```sql
-- Verify app secrets exist
SELECT app_name, secret_key_base FROM apps WHERE app_name = 'cigar';

-- Verify HMS config
SELECT * FROM hms_config WHERE key = 'database_host';
```

---

## 📊 Health Check Tests

### **Service Status Check**
```bash
# Check all Rails app services
for app in cigar tobacco whiskey; do
  echo "=== $app ===" 
  systemctl status puma-$app --no-pager | grep "Active:"
done
```

### **HTTP Accessibility Check**
```bash
# Test all apps respond
for app in cigars tobacco whiskey; do
  echo "Testing $app..."
  curl -sk -w "\nHTTP:%{http_code}\n" https://$app.remoteds.us/up
done
```

### **Database Connectivity Check**
```bash
# Test Rails console access
ssh root@asterra.remoteds.us "cd /var/www/cigar/current && RAILS_ENV=production bundle exec rails runner 'puts Cigar.count'"
```

---

## 🔐 Security Testing

### **Secrets Management**
- Verify secrets are NOT in .env files on production
- Confirm secrets are in systemd service files
- Check database contains all required secrets

### **Access Control**
- Verify only root can access /opt/hosting-api
- Confirm database credentials are properly secured
- Check systemd service files have correct permissions

---

## ✅ Deployment Verification Checklist

After each deployment:
- [ ] Service is active and running
- [ ] App responds to HTTP requests
- [ ] Login page loads correctly
- [ ] Database migrations applied
- [ ] Assets compiled successfully
- [ ] Logs show no errors
- [ ] Authentication working
- [ ] Health check endpoint returns 200

---

## 🚨 Rollback Procedure

If deployment fails:
```bash
# Check service status
systemctl status puma-{app}

# View recent logs
journalctl -u puma-{app} -n 100

# Restart service
systemctl restart puma-{app}

# If needed, rollback git
cd /var/www/{app}/current
git log -n 5  # Find previous commit
git checkout {previous-commit-hash}
systemctl restart puma-{app}
```

---

## 📚 Related Documentation

- [Complete Deployment Guide](../deployment-guides/COMPLETE_DEPLOYMENT_GUIDE.md)
- [Deployment Quick Reference](../deployment-guides/DEPLOYMENT_QUICK_REFERENCE.md)
- [Cigar Deployment Guide](../deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md)
- [Tobacco Deployment Guide](../deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md)
- [Main Project README](../../README.md)
