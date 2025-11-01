# Hosting Management System (HMS) - Testing Strategy

**Last Updated**: November 1, 2025  
**Version**: 1.0  
**Application**: Hosting Management System (HMS)  
**Production URL**: https://hosting.remoteds.us  
**Framework**: Python FastAPI with PostgreSQL

---

## 📋 Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Test Coverage Requirements](#test-coverage-requirements)
- [Unit Testing](#unit-testing)
- [API Testing](#api-testing)
- [Deployment Script Testing](#deployment-script-testing)
- [Database Testing](#database-testing)
- [Integration Testing](#integration-testing)
- [Deployment Verification](#deployment-verification)

---

## 🎯 Overview

The Hosting Management System (HMS) is a FastAPI-based application that manages deployment, monitoring, and control of Rails applications. It provides both a web UI and CLI tools for managing the cigar, tobacco, and whiskey applications.

### **Key Features to Test**
- FastAPI web application and REST API
- Deployment automation (manager.py)
- Secrets management (deploy-secure-sync.py)
- Health check system
- Database operations (hosting_production PostgreSQL)
- App configuration management
- Backup and restore functionality
- Decommission procedures

---

## 🗄️ System Architecture

### **Components**
1. **FastAPI Web Application** (`/opt/hosting-api/web/`)
   - REST API endpoints
   - Web UI for app management
   - Real-time status monitoring

2. **CLI Tools** (`/opt/hosting-api/`)
   - `manager.py` - Primary deployment and management tool
   - `deploy-secure-sync.py` - Secrets deployment
   - `decommission-app.py` - App removal

3. **Database** (`hosting_production` on asterra.remoteds.us)
   - `apps` table - Application configurations
   - `hms_config` table - HMS configuration
   - App secrets and credentials

---

## 📊 Test Coverage Requirements

### **Target Coverage**
- **Overall**: 80%+ code coverage
- **API Endpoints**: 100% (all endpoints must be tested)
- **Deployment Scripts**: 80%+ (critical automation)
- **Database Operations**: 90%+ (data integrity)
- **Security Functions**: 100% (secrets management)

### **Testing Framework**
```python
# requirements-dev.txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
httpx==0.25.2  # For FastAPI testing
faker==20.1.0
factory-boy==3.3.0
```

---

## 🧪 Unit Testing

### **manager.py Testing** (`tests/test_manager.py`)

```python
import pytest
from unittest.mock import Mock, patch
import manager

class TestManagerDeploy:
    """Test deployment functions"""
    
    def test_deploy_with_setup_flag(self, mock_db_connection):
        """Test new deployment with --setup flag"""
        with patch('manager.ssh_command') as mock_ssh:
            result = manager.deploy_app('cigar', setup=True, local=True)
            assert result['success'] is True
            assert 'database_user_created' in result
            
    def test_deploy_migrate_only(self, mock_db_connection):
        """Test redeployment with --migrate-only flag"""
        with patch('manager.ssh_command') as mock_ssh:
            result = manager.deploy_app('cigar', migrate_only=True)
            assert result['success'] is True
            mock_ssh.assert_called_with(contains='db:migrate')
            
    def test_deploy_invalid_app(self):
        """Test deployment with invalid app name"""
        with pytest.raises(ValueError, match='Unknown app'):
            manager.deploy_app('invalid_app')

    def test_health_check_passing(self, mock_running_app):
        """Test health check on running app"""
        result = manager.health_check('cigar')
        assert result['service_active'] is True
        assert result['http_accessible'] is True
        assert result['auth_required'] is True
        assert result['database_connected'] is True

    def test_health_check_failing_service(self, mock_stopped_app):
        """Test health check when service is down"""
        result = manager.health_check('cigar')
        assert result['service_active'] is False
        assert result['errors'] contains 'Service not running'

class TestManagerSecrets:
    """Test secrets management"""
    
    def test_read_secrets_from_database(self, mock_db):
        """Test reading secrets from hosting_production database"""
        secrets = manager.get_app_secrets('cigar')
        assert 'secret_key_base' in secrets
        assert 'database_password' in secrets
        assert 'api_token' in secrets
        
    def test_write_secrets_to_systemd(self, mock_ssh):
        """Test writing secrets to systemd service file"""
        secrets = {'SECRET_KEY_BASE': 'test123'}
        result = manager.write_secrets_to_service('cigar', secrets)
        assert result is True
        mock_ssh.assert_called_with(contains='Environment=SECRET_KEY_BASE')

class TestManagerBackup:
    """Test backup and restore functions"""
    
    def test_create_backup(self, mock_app_db):
        """Test database backup creation"""
        result = manager.backup_app('cigar')
        assert result['success'] is True
        assert result['backup_file'] endswith('.sql.gz')
        
    def test_restore_backup(self, mock_backup_file):
        """Test database restore"""
        result = manager.restore_app('cigar', mock_backup_file)
        assert result['success'] is True
        assert result['rows_restored'] > 0
```

### **deploy-secure-sync.py Testing** (`tests/test_deploy_secure_sync.py`)

```python
import pytest
from unittest.mock import Mock, patch
import deploy_secure_sync as dss

class TestDeploySecureSync:
    """Test secrets deployment"""
    
    def test_load_secrets_from_database(self, mock_db):
        """Test loading secrets from hosting_production"""
        secrets = dss.load_secrets_from_db('cigar')
        assert isinstance(secrets, dict)
        assert len(secrets) > 0
        assert 'SECRET_KEY_BASE' in secrets
        
    def test_deploy_rails_secrets(self, mock_ssh):
        """Test deploying Rails app secrets"""
        secrets = {'SECRET_KEY_BASE': 'abc123', 'CIGAR_API_TOKEN': 'token123'}
        result = dss.deploy_rails_secrets('cigar', secrets)
        assert result is True
        
    def test_deploy_hms_secrets(self, mock_ssh):
        """Test deploying HMS secrets"""
        secrets = {'ADMIN_EMAIL': 'admin@example.com', 'JWT_SECRET': 'secret'}
        result = dss.deploy_hms_secrets(secrets)
        assert result is True
        
    def test_no_env_files_created(self, mock_ssh, tmpdir):
        """Test that no .env files are created on Linux"""
        with patch('platform.system', return_value='Linux'):
            dss.deploy_secrets('cigar')
            # Verify no .env files exist
            assert not any(f.endswith('.env') for f in os.listdir('/var/www/cigar'))
```

### **decommission-app.py Testing** (`tests/test_decommission.py`)

```python
import pytest
from unittest.mock import Mock, patch
import decommission_app

class TestDecommission:
    """Test app decommissioning"""
    
    def test_decommission_with_force_flag(self, mock_running_app):
        """Test decommissioning with --force flag"""
        with patch('decommission_app.confirm_decommission', return_value=True):
            result = decommission_app.decommission('cigar', force=True)
            assert result['success'] is True
            assert result['service_stopped'] is True
            assert result['files_removed'] is True
            assert result['database_removed'] is True
            
    def test_decommission_without_force_fails(self):
        """Test that decommission requires --force flag"""
        with pytest.raises(ValueError, match='force flag required'):
            decommission_app.decommission('cigar', force=False)
            
    def test_decommission_preserves_backups(self, mock_app):
        """Test that decommission keeps database backups"""
        result = decommission_app.decommission('cigar', force=True)
        assert result['backups_preserved'] is True
        backup_dir = '/opt/backups/postgresql/cigar'
        assert os.path.exists(backup_dir)
```

---

## 🌐 API Testing

### **FastAPI Endpoints** (`tests/test_api.py`)

```python
from fastapi.testclient import TestClient
from web.app import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test HMS API endpoints"""
    
    def test_get_apps_list(self, auth_token):
        """Test GET /api/apps"""
        response = client.get(
            "/api/apps",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'apps' in data
        assert len(data['apps']) >= 3  # cigar, tobacco, whiskey
        
    def test_get_app_status(self, auth_token):
        """Test GET /api/apps/{app}/status"""
        response = client.get(
            "/api/apps/cigar/status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'service_status' in data
        assert 'health_check' in data
        
    def test_deploy_app(self, auth_token):
        """Test POST /api/apps/{app}/deploy"""
        response = client.post(
            "/api/apps/cigar/deploy",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"migrate_only": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        
    def test_health_check_endpoint(self, auth_token):
        """Test POST /api/apps/{app}/health-check"""
        response = client.post(
            "/api/apps/cigar/health-check",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'service_active' in data
        assert 'http_accessible' in data
        
    def test_unauthorized_access(self):
        """Test that endpoints require authentication"""
        response = client.get("/api/apps")
        assert response.status_code == 401
```

---

## 🗄️ Database Testing

### **Database Operations** (`tests/test_database.py`)

```python
import pytest
from sqlalchemy import create_engine
from web.database import get_app_config, update_app_config

class TestDatabase:
    """Test database operations"""
    
    def test_get_app_config(self, db_session):
        """Test retrieving app configuration"""
        config = get_app_config('cigar')
        assert config is not None
        assert config['app_name'] == 'cigar'
        assert 'domain' in config
        assert 'port' in config
        
    def test_get_app_secrets(self, db_session):
        """Test retrieving app secrets"""
        secrets = get_app_secrets('cigar')
        assert 'secret_key_base' in secrets
        assert 'database_password' in secrets
        # Verify secrets are not empty
        assert len(secrets['secret_key_base']) > 20
        
    def test_update_app_config(self, db_session):
        """Test updating app configuration"""
        result = update_app_config('cigar', {'port': 3099})
        assert result is True
        config = get_app_config('cigar')
        assert config['port'] == 3099
        
    def test_database_connection(self):
        """Test database connectivity"""
        engine = create_engine(get_db_url())
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
```

---

## 🔗 Integration Testing

### **End-to-End Deployment** (`tests/integration/test_deployment.py`)

```python
import pytest
import subprocess

class TestIntegrationDeployment:
    """Integration tests for full deployment workflow"""
    
    @pytest.mark.slow
    def test_full_deployment_workflow(self):
        """Test complete deployment from scratch"""
        # 1. Deploy app
        result = subprocess.run([
            'ssh', 'root@asterra.remoteds.us',
            'cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --setup --local'
        ], capture_output=True, text=True)
        assert result.returncode == 0
        
        # 2. Run health check
        result = subprocess.run([
            'ssh', 'root@asterra.remoteds.us',
            'cd /opt/hosting-api && .venv/bin/python manager.py health-check --app cigar'
        ], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'service_active: true' in result.stdout
        
        # 3. Verify HTTP access
        result = subprocess.run([
            'curl', '-I', 'https://cigars.remoteds.us'
        ], capture_output=True, text=True)
        assert '200 OK' in result.stdout
        
    @pytest.mark.slow
    def test_redeployment_workflow(self):
        """Test redeployment of existing app"""
        result = subprocess.run([
            'ssh', 'root@asterra.remoteds.us',
            'cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --migrate-only'
        ], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'Migration successful' in result.stdout
```

---

## ✅ Deployment Verification

### **Automated Health Check System**

The HMS implements a comprehensive health check that verifies:

#### **1. Service Status**
```python
def check_service_status(app_name):
    """Check if systemd service is active"""
    result = subprocess.run([
        'systemctl', 'status', f'puma-{app_name}', '--no-pager'
    ], capture_output=True, text=True)
    return 'active (running)' in result.stdout
```

#### **2. HTTP Accessibility**
```python
def check_http_access(app_domain):
    """Check if app responds to HTTP requests"""
    response = requests.get(f'https://{app_domain}', allow_redirects=False)
    return response.status_code in [200, 302]
```

#### **3. Authentication Enforcement**
```python
def check_auth_required(app_domain, protected_path='/cigars'):
    """Verify authentication is enforced"""
    response = requests.get(f'https://{app_domain}{protected_path}', allow_redirects=False)
    return response.status_code == 302  # Redirect to login
```

#### **4. Database Connectivity**
```python
def check_database_connection(app_name):
    """Verify database is accessible"""
    result = subprocess.run([
        'ssh', 'root@asterra.remoteds.us',
        f'cd /var/www/{app_name}/current && RAILS_ENV=production bundle exec rails runner "puts ActiveRecord::Base.connection.active?"'
    ], capture_output=True, text=True)
    return 'true' in result.stdout.lower()
```

#### **5. API Endpoint Check** (for apps with APIs)
```python
def check_api_endpoint(app_name, api_token):
    """Test API endpoints are functional"""
    if app_name == 'cigar':
        response = requests.get(f'https://cigars.remoteds.us/api/inventory/{api_token}')
        return response.status_code == 200 and 'cigars' in response.json()
    return True  # Skip for apps without APIs
```

### **Health Check Command**
```bash
# Run comprehensive health check
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py health-check --app cigar"

# Expected output:
# ✅ Service Status: ACTIVE
# ✅ HTTP Access: OK (200)
# ✅ Authentication: ENFORCED
# ✅ Database: CONNECTED
# ✅ API Endpoints: FUNCTIONAL
# 
# Overall Health: HEALTHY
```

---

## 🚨 Critical Testing Rules

### **Decommission Testing**
```python
# NEVER run without --force flag
# ALWAYS verify backups are preserved
# ALWAYS confirm with user before execution

def test_decommission_safety():
    """Verify decommission safety checks"""
    # Should fail without force flag
    with pytest.raises(SystemExit):
        decommission_app.main(['--app', 'cigar'])
    
    # Should succeed with force flag
    result = decommission_app.main(['--app', 'cigar', '--force'])
    assert result == 0
    
    # Verify backups still exist
    assert os.path.exists('/opt/backups/postgresql/cigar')
```

---

## 📚 Related Documentation

- **[Architecture Plan](../architecture-security/ARCHITECTURE_PLAN.md)** - System architecture
- **[Security Guide](../architecture-security/SECURITY_GUIDE.md)** - Security requirements
- **[Deployment Guides](../deployment-guides/)** - All deployment procedures
- **[Testing Strategies Index](README.md)** - Testing overview

---

**Last Updated**: November 1, 2025  
**Maintained By**: Development Team
