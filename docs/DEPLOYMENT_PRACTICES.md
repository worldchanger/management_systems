# Hosting Management System - Deployment Practices and Methods

**Document Version**: 1.0  
**Last Updated**: October 28, 2025  
**Status**: ✅ **ACTIVE** - Must be followed for all deployments

## 🚨 **CRITICAL SECURITY RULES**

### **NEVER VIOLATE THESE PROTOCOLS**
1. **❌ NEVER copy .secrets.json to remote server** - This violates security protocols
2. **❌ NEVER commit secrets to git** - .secrets.json is excluded in .gitignore for security
3. **❌ NEVER use hardcoded credentials** - Always use environment variables
4. **✅ ALWAYS use deploy-secure-sync.py for secrets management** - Only approved method
5. **✅ ALWAYS verify .env file permissions** - Must be 600 with www-data:www-data ownership

---

## 📋 **Standard Deployment Methods**

### **Method 1: Full System Deployment**
```bash
# Bootstrap deploy with secrets management
python manager.py deploy-hosting-api --project-dir /opt/hosting-api

# Followed by secure secrets sync
python deploy-secure-sync.py
```

### **Method 2: Code-only Updates**
```bash
# Deploy code changes only (preserves existing secrets)
python manager.py deploy-hosting-api --project-dir /opt/hosting-api

# Use this when ONLY code changes, no secrets modifications
```

### **Method 3: Secrets-only Updates**
```bash
# Update secrets without redeploying code
python deploy-secure-sync.py

# Use this when ONLY secrets/credentials need updating
```

### **Method 4: Makefile Pipeline (Code + Service Deploy)**
```bash
# From repository root
# 1) Run unit tests locally
make test

# 2) Commit and push
make push m="Deploy hosting-api: kanban DnD fix; apps control; docs"

# 3) Deploy to remote (rsync code, ensure venv/deps, restart service, health checks)
make deploy

# 4) (If secrets changed) sync secrets and restart
python hosting-management-system/deploy-secure-sync.py
```
Notes:
- This uses hosting-management-system/scripts/deploy_hosting_api.sh to rsync, ensure venv, restart uvicorn/systemd, and run health checks.
- Continue to use deploy-secure-sync.py for secrets; never copy .secrets.json to remote.

---

## 🔒 **Secure Secrets Management Protocol**

### **Required Tools**
1. **Local Source**: `/Users/bpauley/Projects/mangement-systems/.secrets.json`
2. **Remote Target**: `/opt/hosting-api/.env` (600 permissions)
3. **Sync Script**: `deploy-secure-sync.py`

### **Command Sequence**
```bash
# 1. Commit code changes first
git add -A
git commit -m "Description of changes"
git push origin main

# 2. Deploy code changes
python manager.py deploy-hosting-api --project-dir /opt/hosting-api

# 3. Sync secrets securely
python deploy-secure-sync.py

# 4. Verify service status
ssh root@asterra.remoteds.us "systemctl status hms-api --no-pager"
```

---

## 🌐 **Authentication System Architecture**

### **Environment Variables Required**
```bash
# /opt/hosting-api/.env (NEVER commit to git)
HMS_ADMIN_USER=admin
HMS_ADMIN_PASSWORD=<secure_password>
HMS_JWT_SECRET=<secure_jwt_secret>
HMS_API_TOKEN=<secure_api_token>
HMS_JWT_ACCESS_EXPIRATION_MINUTES=15
HMS_JWT_REFRESH_EXPIRATION_DAYS=7
```

### **Two Authentication Methods**
1. **Web Interface**: Cookie-based JWT with redirect to `/login`
2. **API Endpoints**: Authorization header Bearer token

### **Authentication Dependencies**
- **Web Routes**: Use `get_current_user_web()` 
- **API Routes**: Use `get_current_user()`
- **Import From**: `auth_utils.py` (to avoid circular imports)

---

## 📁 **File Structure and Template Locations**

### **Critical Directory Structure**
```
/opt/hosting-api/
├── app_fastapi.py              # Main FastAPI application
├── auth_utils.py               # Authentication utilities
├── core/
│   └── todos.py               # TODO management core
├── routes/
│   └── todo_routes.py         # Web interface and API routes
├── web/
│   ├── static/                # CSS/JS files
│   └── templates/             # ALL Jinja2 templates
│       ├── layout.html        # Base layout template
│       ├── login.html         # Login interface
│       ├── admin_tasks.html   # TODO kanban board
│       └── admin_tasks_lanes.html # Kanban lane components
├── .env                       # Environment variables (600 permissions)
└── TODO.md                    # Task data file
```

### **Template Directory Rules**
- **✅ Use**: `web/templates/` for all Jinja2 templates
- **❌ Never**: Use root `templates/` directory
- **✅ Include**: `layout.html` for consistent UI
- **✅ Extends**: All templates must extend from layout.html

---

## 🛠️ **Development vs Production Deployment**

### **Development Environment**
```bash
# Local testing with mock environment
export HMS_ADMIN_USER=admin
export HMS_ADMIN_PASSWORD=admin
export HMS_JWT_SECRET=dev-secret
python -m uvicorn app_fastapi:app --reload
```

### **Production Environment**
```bash
# Must use secure deployment method
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
python deploy-secure-sync.py
```

---

## 🔄 **Service Management Commands**

### **Service Control**
```bash
# Check service status
ssh root@asterra.remoteds.us "systemctl status hms-api --no-pager"

# Restart service after deployment
ssh root@asterra.remoteds.us "systemctl restart hms-api"

# View service logs
ssh root@asterra.remoteds.us "journalctl -u hms-api -n 50 --no-pager"
```

### **Log Monitoring**
```bash
# Real-time log monitoring
ssh root@asterra.remoteds.us "journalctl -u hms-api -f"

# Check for errors in last 100 lines
ssh root@asterra.remoteds.us "journalctl -u hms-api -n 100 --no-pager | grep -i error"
```

---

## 📊 **Pre-deployment Checklist**

### **Code Quality Checks**
- [ ] All unit tests passing (`python -m pytest tests/ -v`)
- [ ] No circular imports
- [ ] All environment variables referenced
- [ ] Template paths correct (`web/templates/`)
- [ ] Authentication dependencies correct

### **Security Verification**
- [ ] No hardcoded credentials in code
- [ ] `.secrets.json` NOT in deployment package
- [ ] `.env` file permissions set to 600
- [ ] www-data:www-data ownership on `.env`
- [ ] HTTPS URLs in production

### **Functionality Testing**
- [ ] Login page accessible
- [ ] Authentication redirects working
- [ ] TODO interface loads after login
- [ ] API endpoints require authentication
- [ ] Drag-and-drop functionality working

---

## 🚨 **Troubleshooting Common Issues**

### **Issue: Circular Import Error**
**Solution**: Use `auth_utils.py` for shared authentication functions
```python
# ❌ NEVER DO THIS
from app_fastapi import get_current_user_web

# ✅ ALWAYS DO THIS
from auth_utils import get_current_user_web
```

### **Issue: Template Not Found Error**
**Solution**: Ensure templates are in `web/templates/` not `templates/`
```python
# ❌ WRONG
templates = Jinja2Templates(directory="templates")

# ✅ CORRECT
templates = Jinja2Templates(directory="web/templates")
```

### **Issue: Authentication Not Working**
**Solution**: Verify .env file exists and has correct permissions
```bash
ssh root@asterra.remoteds.us "ls -la /opt/hosting-api/.env"
# Should show: -rw------- 1 www-data www-data

# Fix if needed:
ssh root@asterra.remoteds.us "chmod 600 /opt/hosting-api/.env"
ssh root@asterra.remoteds.us "chown www-data:www-data /opt/hosting-api/.env"
```

### **Issue: Service Fails to Start**
**Solution**: Check service logs for specific error
```bash
ssh root@asterra.remoteds.us "journalctl -u hms-api -n 20 --no-pager"
```

---

## 📚 **Required Reading**

### **Before Any Deployment**
1. **SECURITY_GUIDE.md** - Complete security protocols
2. **[agents.md](../agents.md)** - AI agent protocols, system architecture, and authoritative documentation links
3. **[ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)** - Complete system architecture and technical specifications
4. **This Document** - Deployment practices (you are here)

### **Cross-Reference Documents**
- **[agents.md](../agents.md)**: AI agent protocols, system architecture, and authoritative documentation links
- **[ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)**: Complete system architecture and technical specifications
- **[SECURITY_GUIDE.md](SECURITY_GUIDE.md)**: Detailed security protocols and compliance requirements
- **[COMPLETE_DEPLOYMENT_GUIDE.md](COMPLETE_DEPLOYMENT_GUIDE.md)**: Application-specific deployment procedures
- **README.md**: System overview and access instructions
- **CHANGELOG.md**: Version history and feature tracking

**📖 Authoritative Documentation**: This document is part of the authoritative documentation set. See [agents.md](../agents.md) for the complete documentation hierarchy and reading requirements.

---

## 🎯 **Deployment Success Criteria**

### **Must Pass All Checks**
- [ ] Service status: `active (running)`
- [ ] No error messages in logs
- [ ] Login page accessible at `/login`
- [ ] TODO interface accessible after authentication
- [ ] All API endpoints require authentication
- [ ] Template rendering successful
- [ ] Environment variables loaded correctly

### **Performance Requirements**
- [ ] Page load time < 2 seconds
- [ ] API response time < 500ms
- [ ] Memory usage < 100MB
- [ ] No startup errors

---

## 📞 **Emergency Procedures**

### **If Deployment Fails**
1. **Stop**: Identify error from service logs
2. **Rollback**: Use `git checkout <previous_commit>` if needed
3. **Fix**: Address root cause (check this document for solutions)
4. **Redeploy**: Follow standard deployment procedure

### **Quick Rollback Commands**
```bash
# Roll to previous commit
git checkout HEAD~1
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
python deploy-secure-sync.py
```

---

## ✅ **Certification**

**I have read and understand these deployment protocols. I will:**

- [ ] **NEVER** copy .secrets.json to remote servers
- [ ] **ALWAYS** use deploy-secure-sync.py for secrets management  
- [ ] **ALWAYS** verify .env file permissions (600, www-data:www-data)
- [ ] **ALWAYS** use correct template paths (web/templates/)
- [ ] **ALWAYS** follow pre-deployment checklist
- [ ] **NEVER** commit secrets to version control

**Violations of these protocols will break authentication and create security vulnerabilities.**

---

**Document Maintenance**: This document must be updated whenever deployment procedures change. All team members must re-read and re-certify when updated.

**Last Updated**: October 28, 2025  
**Next Review**: January 28, 2026
