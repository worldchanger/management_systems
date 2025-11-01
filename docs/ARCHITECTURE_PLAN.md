# Hosting Management System - Complete Architecture Plan

**Date**: October 31, 2025  
**Status**: Phase 4 Complete - Database-First Architecture Implemented

## 🚨 CRITICAL: DATABASE-FIRST ARCHITECTURE

**ALL configuration and secrets are stored in and loaded from the `hosting_production` PostgreSQL database.**

- ❌ NO .env files on server
- ❌ NO .secrets.json files on server  
- ❌ NO config.json files on server
- ✅ ALL secrets in database tables
- ✅ Secrets injected as Environment= variables in systemd service files
- ✅ Infrastructure as code

## 🎯 **System Overview**

### Two-Part System

**1. Local CLI Client (Developer Laptop)**
- File: `manager.py`
- Purpose: Initial provisioning, bulk operations, scripting
- Communication: HTTPS API calls to remote server

**2. Remote Web Interface (hosting.remoteds.us)**
- Location: `web/` directory (deployed to `/opt/hosting-api/`)
- Technology: FastAPI + Jinja2 templates
- Purpose: Web dashboard + REST API for management
- Features:
  - Password-protected web UI
  - Manage all Rails apps
  - View logs (app logs, Nginx logs)
  - View/edit Nginx configs
  - Run troubleshooting scripts
  - Deploy/update itself

## 📁 **Repository Structure**

```
hosting-management-system/
├── manager.py              # LOCAL: CLI client for laptop
├── web/                    # REMOTE: Web interface (deployed to server)
│   ├── app.py             # FastAPI application
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── web_routes.py  # HTML pages
│   │   ├── api_routes.py  # REST API endpoints
│   │   └── auth.py        # Authentication
│   ├── services/
│   │   ├── app_manager.py # Deploy, start, stop, restart apps
│   │   ├── log_viewer.py  # View logs (app + nginx)
│   │   ├── config_manager.py # View/edit nginx configs
│   │   └── script_runner.py # Execute troubleshooting scripts
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── layout.html
│   │   ├── dashboard.html
│   │   ├── logs.html
│   │   ├── configs.html
│   │   └── scripts.html
│   └── static/            # CSS, JS, images
├── templates/             # Server config templates
│   ├── nginx-ssl.conf.tpl
│   ├── puma.rb.tpl
│   ├── puma.service.tpl
│   └── hosting-api.service.tpl
├── remote_cli_tools/      # Troubleshooting scripts
│   ├── parse_logs.sh
│   ├── check_status.sh
│   ├── restart_service.sh
│   └── check_disk_space.sh
├── tests/                 # Pytest test suite
│   ├── test_manager.py    # Test local CLI
│   ├── test_web_api.py    # Test remote API
│   ├── test_auth.py       # Test authentication
│   └── test_services.py   # Test service modules
├── db_config.py           # Database configuration loader
├── deploy-secure-sync.py  # Deploys secrets from database to systemd
├── requirements.txt
└── DEPLOYMENT_LOG.md
```

## 🔐 **Database-First Secret Management**

### **Database Tables**

**`apps` table** - Rails application configuration:
```sql
CREATE TABLE apps (
    app_key VARCHAR(50) PRIMARY KEY,
    app_name VARCHAR(100) NOT NULL,
    subdomain VARCHAR(100) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    github_repo VARCHAR(500) NOT NULL,
    document_root VARCHAR(500) NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    database_username VARCHAR(100) NOT NULL,
    database_password TEXT NOT NULL,
    secret_key_base TEXT NOT NULL,
    api_token VARCHAR(255) NOT NULL,
    json_api_url TEXT,
    openrouter_api_key TEXT,
    cert_path VARCHAR(500),
    key_path VARCHAR(500),
    port INTEGER DEFAULT 3000,
    enabled BOOLEAN DEFAULT true,
    backup_enabled BOOLEAN DEFAULT false,
    backup_schedule VARCHAR(50) DEFAULT '0 2 * * *',
    backup_retention_days INTEGER DEFAULT 30,
    local_code_path VARCHAR(500),
    deployed_server VARCHAR(255) DEFAULT 'asterra.remoteds.us',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**`hms_config` table** - HMS configuration:
```sql
CREATE TABLE hms_config (
    subdomain VARCHAR(100),
    domain VARCHAR(255),
    database_name VARCHAR(100),
    database_username VARCHAR(100),
    database_password TEXT,
    database_port INTEGER,
    database_host VARCHAR(255),
    admin_username VARCHAR(100),
    admin_password TEXT,
    jwt_secret TEXT,
    api_token VARCHAR(255),
    ...
);
```

### **Secret Deployment Flow**

1. Secrets stored in database
2. `deploy-secure-sync.py` reads from database
3. Writes secrets as `Environment=` variables to systemd service files:
   - `/etc/systemd/system/puma-{app}.service` for Rails apps
   - `/etc/systemd/system/hms-api.service` for HMS
4. Services restart with new environment variables
5. NO files containing secrets on disk

### **SSL Certificates**

Let's Encrypt certificates managed automatically:
- Stored in `/etc/letsencrypt/live/{domain}/`
- Paths saved in database `cert_path` and `key_path` fields
- Auto-renewal handled by certbot

## 🌐 **Remote Web Interface Features**

### Dashboard View (`/`)
- Status of all Rails apps (running/stopped)
- Quick actions: Start, Stop, Restart
- Recent activity log
- System resource usage (disk, memory)

### Logs View (`/logs`)
- **App Logs**: View logs for any Rails app
  - Filter by app (cigar, tobacco)
  - Filter by date range
  - Search for errors
  - Real-time tail option
- **Nginx Logs**: View access and error logs
  - Combined view or separate
  - Search and filter capabilities

### Configs View (`/configs`)
- View all Nginx configuration files
- Edit configs with syntax highlighting
- Test config before applying (`nginx -t`)
- Reload Nginx after changes
- Backup/restore configs

### Scripts View (`/scripts`)
- List all troubleshooting scripts in `remote_cli_tools/`
- Execute scripts with parameters
- View script output in real-time
- Save script results
- Script examples:
  - Parse logs for errors
  - Check service status
  - Check disk space
  - Database connection test
  - SSL certificate check

### Deployment View (`/deploy`)
- Deploy/update Rails apps
- Deploy/update hosting management system itself
- View deployment history
- Rollback capability

### API Endpoints

#### Authentication
- `POST /api/auth/login` - Get JWT token
- `POST /api/auth/refresh` - Refresh token

#### App Management
- `GET /api/apps` - List all apps and their status
- `POST /api/apps/{app}/start` - Start an app
- `POST /api/apps/{app}/stop` - Stop an app
- `POST /api/apps/{app}/restart` - Restart an app
- `POST /api/apps/{app}/deploy` - Deploy/update an app

#### Logs
- `GET /api/logs/{app}` - Get app logs
- `GET /api/logs/nginx/access` - Get Nginx access logs
- `GET /api/logs/nginx/error` - Get Nginx error logs

#### Configs
- `GET /api/configs/nginx` - List all Nginx configs
- `GET /api/configs/nginx/{site}` - Get specific config
- `PUT /api/configs/nginx/{site}` - Update config
- `POST /api/configs/nginx/test` - Test Nginx config
- `POST /api/configs/nginx/reload` - Reload Nginx

#### Scripts
- `GET /api/scripts` - List available scripts
- `POST /api/scripts/{script}/run` - Execute a script

## 🚀 **Deployment Strategy**

### Initial Deployment (Chicken & Egg Problem Solved)

**Problem**: How to deploy the management system when it doesn't exist yet?

**Solution**: Bootstrap via local CLI, then self-manage

```bash
# 1. First-time deployment (from laptop using Fabric)
python manager.py provision           # Install system packages
python manager.py deploy-hosting-api  # Deploy web interface (new command)

# 2. After initial deployment, web interface can self-update
# Via web UI: https://hosting.remoteds.us/deploy
# Or via API: curl -X POST https://hosting.remoteds.us/api/hosting/deploy
```

### Updating the Hosting Management System

Three methods:

**Method 1: Via Web Interface**
```
1. Login to hosting.remoteds.us
2. Navigate to /deploy
3. Click "Update Hosting System"
4. System pulls latest code from Git
5. Restarts itself gracefully
```

**Method 2: Via API (from laptop)**
```bash
python manager.py update-hosting-api
# Uses API: POST /api/hosting/deploy
```

**Method 3: Via SSH (emergency)**
```bash
ssh root@asterra.remoteds.us
cd /opt/hosting-api
git pull origin main
pip install -r requirements.txt
systemctl restart hosting-api
```

## 🔄 **System Flow Examples**

### Example 1: Restart Cigar App via Web UI
```
User → hosting.remoteds.us/dashboard
     → Click "Restart" on Cigar app
     → POST /api/apps/cigar/restart
     → Execute: systemctl restart cigar.service
     → Return status to UI
```

### Example 2: View Logs via CLI
```
Laptop → python manager.py logs --app cigar --lines 100
       → HTTP GET https://hosting.remoteds.us/api/logs/cigar?lines=100
       → Execute: journalctl -u cigar.service -n 100
       → Return logs to CLI
       → Display in terminal
```

### Example 3: Run Troubleshooting Script
```
User → hosting.remoteds.us/scripts
     → Select "parse_logs.sh"
     → Enter parameters: app=cigar, pattern=ERROR
     → POST /api/scripts/parse_logs/run
     → Execute: /usr/local/bin/parse_logs.sh cigar ERROR
     → Stream output to browser
```

## 🧪 **Testing Strategy**

### Test Categories

**1. Unit Tests** (`tests/test_services.py`)
- Test each service module independently
- Mock external dependencies
- Test error handling

**2. API Tests** (`tests/test_web_api.py`)
- Test all API endpoints
- Test authentication/authorization
- Test input validation
- Test error responses

**3. Integration Tests** (`tests/test_integration.py`)
- Test full workflows (deploy → start → stop)
- Test with real systemctl commands (in test environment)
- Test Nginx config changes

**4. CLI Tests** (`tests/test_manager.py`)
- Test CLI commands
- Test API communication
- Test error handling

**5. Security Tests** (`tests/test_auth.py`)
- Test authentication
- Test JWT token validation
- Test rate limiting
- Test password requirements

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_web_api.py -v

# Run with coverage
pytest --cov=web --cov-report=html

# Run integration tests (requires test server)
pytest tests/test_integration.py -m integration
```

### Test Requirements
- ✅ All tests must pass before deployment
- ✅ Minimum 80% code coverage
- ✅ No hardcoded credentials in tests
- ✅ Use fixtures for test data
- ✅ Clean up test data after tests

## 📋 **Implementation Phases**

### Phase 1: Core Infrastructure (Week 1)
- [x] Update .secrets.json format
- [x] Create web/ directory structure
- [x] Implement basic FastAPI app with authentication
- [x] Create dashboard HTML template
- [x] Deploy to server (bootstrap method)
- [x] Write tests for authentication

### Phase 2: App Management (Week 2) - ✅ COMPLETE
- [x] Implement app status checking
- [x] Implement start/stop/restart functionality
- [x] Create app management UI
- [x] Add API endpoints for app control
- [x] Write tests for app management
- [x] Test with cigar and tobacco apps

### Phase 2a: ACME/SSL (Let’s Encrypt)
- [x] Add `letsencrypt_email` to `config.json` (contact for LE terms)
- [x] Install Certbot + nginx plugin on remote host
- [x] Issue staging certs for: hosting.remoteds.us, cigars.remoteds.us, tobacco.remoteds.us
- [x] Switch to production issuance for all three domains
- [ ] Verify auto-renew timer and dry-run; confirm Nginx reload on renew
- [x] Update `ssl_config` to LE live paths (if not already)

### Phase 3: Log Viewing (Week 3) - ✅ COMPLETE
- [x] Implement log reading service
- [x] Create logs UI with filtering
- [x] Add Nginx log support
- [x] Implement real-time log tailing
- [x] Write tests for log viewing

### Phase 4: Config Management (Week 4)
- [ ] Implement config reading/writing
- [ ] Create config editing UI
- [ ] Add Nginx config validation
- [ ] Implement backup/restore
- [ ] Write tests for config management

### Phase 5: Script Execution (Week 5)
- [ ] Create troubleshooting scripts
- [ ] Implement script runner service
- [ ] Create scripts UI
- [ ] Add script output streaming
- [ ] Write tests for script execution

### Phase 6: Self-Management (Week 6)
- [ ] Implement self-update functionality
- [ ] Add deployment UI
- [ ] Test graceful restart
- [ ] Document update procedures
- [ ] Write tests for self-updates

## 📊 **Success Criteria**

### Phase 1 Complete When:
- ✅ Can access https://hosting.remoteds.us with password
- ✅ Dashboard shows all apps with status
- ✅ Authentication tests pass
- ✅ Deployed via bootstrap method

### Phase 2 Complete When: - ✅ COMPLETE
- ✅ Can start/stop/restart all Rails apps via web UI
- ✅ Can start/stop/restart via API from laptop
- ✅ All app management tests pass

### Phase 3 Complete When: - ✅ COMPLETE
- ✅ Can view logs for all Rails apps
- ✅ Can view Nginx access and error logs
- ✅ Can search and filter logs
- ✅ All log viewing tests pass

### Phase 4 Complete When:
- ✅ Can view all Nginx configs
- ✅ Can edit and test configs
- ✅ Changes are validated before applying
- ✅ All config management tests pass

### Phase 5 Complete When:
- ✅ Can list all troubleshooting scripts
- ✅ Can execute scripts with parameters
- ✅ Can view script output in real-time
- ✅ All script execution tests pass

### Phase 6 Complete When:
- ✅ Can update hosting system via web UI
- ✅ Updates are graceful (no downtime)
- ✅ Can rollback if needed
- ✅ All self-update tests pass

## 🔒 **Security Considerations**

1. **HTTPS Only**: All traffic encrypted
2. **Password Protection**: Strong password required
3. **JWT Authentication**: API requires valid token
4. **Rate Limiting**: Prevent brute force attacks
5. **Input Validation**: Sanitize all inputs
6. **Command Injection Prevention**: Validate script parameters
7. **Audit Logging**: Log all management actions
8. **Session Timeout**: Auto-logout after inactivity

## 📝 **Next Actions**

1. **Current**: Begin Phase 4 (Config Management)
2. **Next**: Implement config reading/writing service
3. **Then**: Create config editing UI with validation
4. **Test**: Write comprehensive config management tests
5. **Future**: Complete Phases 5-6 (Script Execution & Self-Management)

---

**Status**: Phase 3 Complete - Ready for Phase 4 implementation
**Priority**: High - Continue systematic feature development
**Owner**: AI Agent + User Review

## 📈 **Progress Summary**

### ✅ Completed Phases
- **Phase 1**: Core Infrastructure - Authentication, basic web interface
- **Phase 2**: App Management - Start/stop/restart functionality
- **Phase 3**: Log Viewing - Comprehensive log viewing with filtering

### 🚧 Current Phase
- **Phase 4**: Config Management - Nginx configuration editing

### 📋 Remaining Phases
- **Phase 5**: Script Execution - Troubleshooting script runner
- **Phase 6**: Self-Management - System updates and deployment

### 🧪 Test Coverage
- **Total Tests**: 89 passing tests
- **Log Viewer Tests**: 23 tests covering all functionality
- **API Routes Tests**: 26 tests covering all endpoints
- **Existing Tests**: 40 tests for core functionality
