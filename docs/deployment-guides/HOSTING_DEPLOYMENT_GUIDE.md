# Hosting Management System Deployment Guide

**Version**: 3.0  
**Last Updated**: October 29, 2025  
**Status**: ✅ **ACTIVE** - Consolidated deployment procedures

---

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Prerequisites](#prerequisites)
- [Security Protocols](#security-protocols)
- [Deployment Methods](#deployment-methods)
- [SSL Certificate Setup](#ssl-certificate-setup)
- [Service Management](#service-management)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## 🎯 System Overview

The Hosting Management System (HMS) is a Python FastAPI application that provides:
- Web-based dashboard for monitoring Rails applications
- REST API for programmatic management
- TODO/Kanban system for task tracking
- Log viewing and service control capabilities

### **Architecture**
```
Local Development (Laptop)          Remote Server (asterra.remoteds.us)
├── manager.py (CLI tool)          ├── /opt/hosting-api/ (FastAPI app)
├── .secrets.json (credentials)    ├── hms-api.service (systemd)
└── deployment scripts             └── Nginx reverse proxy
```

### **Services**
- **Application**: FastAPI web server on port 5051
- **Service Name**: `hms-api.service`
- **Domain**: `https://hosting.remoteds.us`
- **Database**: SQLite for lightweight data storage

---

## 🚀 Prerequisites

### **System Requirements**
- Ubuntu 25.04 LTS server
- Python 3.12+ on development machine
- SSH key access to production server
- Domain names pointing to server IP

### **Required Files**
```bash
# Local workspace structure
/Users/bpauley/Projects/mangement-systems/
├── .secrets.json          # Credentials (NEVER commit)
├── config.json            # Public configuration
├── agents.md              # Master rules document
├── docs/                  # All documentation
└── hosting-management-system/
    ├── manager.py         # CLI deployment tool
    ├── app_fastapi.py     # FastAPI application
    └── web/               # Templates and static files
```

---

## 🔒 Security Protocols (CRITICAL)

### **NEVER VIOLATE THESE RULES**
1. **❌ NEVER copy .secrets.json to any remote server**
2. **❌ NEVER commit secrets to version control**
3. **❌ NEVER use hardcoded credentials in code**
4. **✅ ALWAYS use environment variables for production**
5. **✅ ALWAYS verify file permissions (600)**
6. **✅ ALWAYS use www-data:www-data ownership**

### **Environment Variables**
```bash
# /opt/hosting-api/.env (production only)
HMS_ADMIN_USER=admin
HMS_ADMIN_PASSWORD=<secure-password>
HMS_JWT_SECRET=<32-character-secret>
HMS_API_TOKEN=<api-token>
HMS_JWT_ACCESS_EXPIRATION_MINUTES=15
HMS_JWT_REFRESH_EXPIRATION_DAYS=7
```

---

## 🚀 Deployment Methods

### **Method 1: Full Deployment (Recommended)**
```bash
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system

# 1. Commit any code changes
git add -A
git commit -m "Deployment description"
git push origin main

# 2. Deploy application code
python manager.py deploy-hosting-api --project-dir /opt/hosting-api

# 3. Sync secrets securely (INCLUDES API TOKENS)
python deploy-secure-sync.py
# This deploys:
# - HMS admin credentials
# - JWT secrets
# - Database credentials
# - Rails app API tokens (CIGAR_API_TOKEN, TOBACCO_API_TOKEN)

# 4. Verify service status
python manager.py hms-api-service status

# 5. Run deployment verification (CRITICAL - DO NOT SKIP)
# Verifies all endpoints, checks for 500/404/auth errors
python scripts/verify_deployment.py --username admin --password <admin-password>
```

**⚠️ IMPORTANT**: If step 5 verification fails, **DO NOT CONSIDER DEPLOYMENT COMPLETE**. 
- Check logs for errors: `ssh root@asterra.remoteds.us "journalctl -u hms-api -n 100"`
- Fix the root cause (code bug, missing dependency, config error)
- Commit the fix and repeat steps 1-5
- **Never** skip verification - it catches Internal Server Errors, 404s, auth issues

**🔑 API Token Deployment Note**:
- The `deploy-secure-sync.py` script now automatically deploys Rails API tokens
- Tokens are written to systemd service files as Environment variables
- This ensures secure, non-plain-text storage of API credentials
- After running deploy-secure-sync.py, Rails apps MUST be restarted to pick up new tokens

### **Method 2: Code-Only Updates**
```bash
# When ONLY code changes, no secrets updates needed
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
```

### **Method 3: Secrets-Only Updates**
```bash
# When ONLY credentials need updating
python deploy-secure-sync.py
```

### **Method 4: Makefile Pipeline (Code + Service Deploy)**
```bash
# From repository root
# 1) Run unit tests locally
make test

# 2) Commit and push
make push m="Deploy: kanban DnD fix; apps start/stop/restart; docs"

# 3) Deploy to remote (rsync code, ensure venv/deps, restart service, health checks)
make deploy

# 4) (If secrets changed) sync secrets and restart
python hosting-management-system/deploy-secure-sync.py
```
Notes:
- The Makefile calls hosting-management-system/scripts/deploy_hosting_api.sh which performs:
  - rsync of the hosting-management-system to /opt/hosting-api (excludes .venv, .git, __pycache__)
  - creates/uses venv at /opt/hosting-api/.venv and installs requirements.txt
  - restarts uvicorn (or systemd if present)
  - runs /health and /api/v1/kanban/health checks
- Continue using deploy-secure-sync.py for secrets rotation; never copy .secrets.json to remote.

---

## 🚂 Rails Application Deployment

### **Critical Deployment Order**
For Cigar and Tobacco Rails applications, always follow this order:
1. **Deploy Secrets FIRST** (API tokens via systemd)
2. **Deploy Application Code**
3. **Restart Services**
4. **Verify Deployment**

### **Full Rails App Deployment Process**

#### **Step 1: Deploy Secrets (API Tokens)**
```bash
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system

# Deploy API tokens to systemd service files
python deploy-secure-sync.py

# This automatically:
# - Adds/updates CIGAR_API_TOKEN in cigar-management-system.service
# - Adds/updates TOBACCO_API_TOKEN in tobacco-management-system.service
# - Reloads systemd daemon
# - Does NOT restart apps yet (do that after code deploy)
```

#### **Step 2: Deploy Application Code**
```bash
# For Cigar App
cd /Users/bpauley/Projects/mangement-systems/cigar-management-system
git add -A
git commit -m "Deploy: description"
git push origin main

# Deploy to production
# (Use your deployment method - rsync, Capistrano, etc.)

# For Tobacco App
cd /Users/bpauley/Projects/mangement-systems/tobacco-management-system
git add -A
git commit -m "Deploy: description"
git push origin main

# Deploy to production
```

#### **Step 3: Restart Rails Services**
```bash
# SSH to server
ssh root@asterra.remoteds.us

# Restart both apps to pick up new code and API tokens
sudo systemctl restart cigar-management-system
sudo systemctl restart tobacco-management-system

# Verify services are running
sudo systemctl status cigar-management-system
sudo systemctl status tobacco-management-system
```

#### **Step 4: Comprehensive Verification**

**A. Check API Endpoints with Tokens**
```bash
# Test Cigar API
curl -s "https://cigars.remoteds.us/api/inventory/cigar_9ZRTs_jAOtP-y_F3a1sozNrGJQpB28DvZemv-_sD_2E" | python3 -m json.tool | head -20

# Test Tobacco API
curl -s "https://tobacco.remoteds.us/api/inventory/tobacco_Ng0UtgzQDSfqMjGgiCOjcmxj2A34q-anqQ1ebh6iTmA" | python3 -m json.tool | head -20

# Both should return JSON inventory data
# If you get 401/403, tokens are not set correctly
# If you get 500, check application logs
```

**B. Check Routes Without Authentication**
```bash
# Should redirect to login (302)
curl -I https://cigars.remoteds.us/cigars
curl -I https://tobacco.remoteds.us/locations

# Should NOT return 404 or 500
```

**C. Test Authenticated Routes**
```bash
# Login and test pages manually:
# 1. Visit https://cigars.remoteds.us
# 2. Login with credentials
# 3. Navigate to all major pages:
#    - Dashboard
#    - Cigars index
#    - Humidors index
#    - Brands index
#    - Locations index
#    - Click "View" on individual items
# 4. Check browser console for JS errors
# 5. Check for layout/styling issues
```

**D. Check Application Logs**
```bash
# Cigar app logs
sudo journalctl -u cigar-management-system -n 100 --no-pager

# Tobacco app logs
sudo journalctl -u tobacco-management-system -n 100 --no-pager

# Look for:
# - 500 errors
# - Missing method errors
# - Template errors
# - Database connection errors
# - Asset loading errors
```

**E. Check Nginx Logs**
```bash
# Access logs
sudo tail -50 /var/log/nginx/cigars.remoteds.us.access.log
sudo tail -50 /var/log/nginx/tobacco.remoteds.us.access.log

# Error logs
sudo tail -50 /var/log/nginx/cigars.remoteds.us.error.log
sudo tail -50 /var/log/nginx/tobacco.remoteds.us.error.log
```

### **Deployment Verification Checklist**

Use this checklist after EVERY deployment:

- [ ] API endpoints return valid JSON (not 401/500)
- [ ] Unauthenticated routes redirect to login (302, not 404/500)
- [ ] Login page loads without errors
- [ ] Can successfully login with credentials
- [ ] Dashboard loads with real data
- [ ] All index pages load (cigars, humidors, brands, locations, etc.)
- [ ] Can view individual item show pages
- [ ] Can create new items (if applicable)
- [ ] Can edit existing items
- [ ] Application logs show no errors after page loads
- [ ] Nginx logs show 200/302 responses (no 500s)
- [ ] Browser console shows no JavaScript errors
- [ ] Images load correctly (if applicable)
- [ ] API URLs in config.json match production endpoints

### **Common Deployment Issues**

**Issue**: API returns `{"error": "Invalid API token"}`
- **Cause**: Token not set in systemd service file
- **Fix**: Run `deploy-secure-sync.py` and restart service

**Issue**: API returns `{"error": "API not configured"}`
- **Cause**: ENV variable not loading
- **Fix**: Check service file has `Environment="CIGAR_API_TOKEN=..."` and restart

**Issue**: Routes return 500 Internal Server Error
- **Cause**: Application code error
- **Fix**: Check logs with `journalctl -u <service> -n 100`

**Issue**: Routes return 404 Not Found
- **Cause**: Routing or nginx configuration issue
- **Fix**: Verify routes.rb and nginx config

**Issue**: Cannot login / Devise errors
- **Cause**: Database migration not run, secret_key_base issue
- **Fix**: Run migrations, check .env file on server

---

## 🔐 SSL Certificate Setup

### **Automated SSL with Let's Encrypt**
```bash
# 1. Install Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. Obtain certificate
sudo certbot --nginx -d hosting.remoteds.us

# 3. Test renewal
sudo certbot renew --dry-run
```

### **SSL Configuration**
```nginx
# Nginx configuration (auto-updated by Certbot)
server {
    listen 443 ssl;
    server_name hosting.remoteds.us;
    
    ssl_certificate /etc/letsencrypt/live/hosting.remoteds.us/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hosting.remoteds.us/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    
    location / {
        proxy_pass http://127.0.0.1:5051;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔧 Service Management

### **Service Control Commands**
```bash
# Check service status
ssh root@asterra.remoteds.us "systemctl status hms-api --no-pager"

# Restart service
ssh root@asterra.remoteds.us "systemctl restart hms-api"

# View logs
ssh root@asterra.remoteds.us "journalctl -u hms-api -n 50 --no-pager"

# Real-time log monitoring
ssh root@asterra.remoteds.us "journalctl -u hms-api -f"
```

### **Local Management Commands**
```bash
# From development machine
python manager.py hms-api-service status
python manager.py hms-api-service restart
python manager.py tail-logs --unit hms-api
```

---

## 🧪 Verification Checklist

### **Post-Deployment Verification**
- [ ] Service status: `active (running)`
- [ ] HTTPS accessible: `https://hosting.remoteds.us`
- [ ] Login page loads: `/login`
- [ ] Authentication works
- [ ] Dashboard accessible after login
- [ ] TODO system functional
- [ ] API endpoints require authentication
- [ ] No errors in service logs

### **Security Verification**
- [ ] `.env` file permissions: `600`
- [ ] `.env` ownership: `www-data:www-data`
- [ ] No secrets in code repository
- [ ] HTTPS redirect working
- [ ] SSL certificate valid

---

## 🚨 Troubleshooting

### **Common Issues and Solutions**

#### **Service Won't Start**
```bash
# Check environment file
ssh root@asterra.remoteds.us "ls -la /opt/hosting-api/.env"

# Check logs for errors
ssh root@asterra.remoteds.us "journalctl -u hms-api -n 20 --no-pager"

# Fix permissions if needed
ssh root@asterra.remoteds.us "chmod 600 /opt/hosting-api/.env"
ssh root@asterra.remoteds.us "chown www-data:www-data /opt/hosting-api/.env"
```

#### **Authentication Fails**
```bash
# Verify environment variables
ssh root@asterra.remoteds.us "grep HMS_ADMIN /opt/hosting-api/.env"

# Resync secrets
python deploy-secure-sync.py

# Restart service
ssh root@asterra.remoteds.us "systemctl restart hms-api"
```

#### **SSL Certificate Issues**
```bash
# Check certificate status
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run

# Reissue certificate if needed
sudo certbot delete --cert-name hosting.remoteds.us
sudo certbot --nginx -d hosting.remoteds.us
```

---

## 🔄 Maintenance Procedures

### **Regular Maintenance**
```bash
# Check SSL certificate expiration
echo | openssl s_client -connect hosting.remoteds.us:443 2>/dev/null | openssl x509 -noout -dates

# Monitor disk space
ssh root@asterra.remoteds.us "df -h /opt/hosting-api"

# Update system packages
ssh root@asterra.remoteds.us "apt update && apt upgrade -y"
```

### **Credential Rotation**
```bash
# 1. Update local .secrets.json
# 2. Run secure sync
python deploy-secure-sync.py
# 3. Restart service
python manager.py hms-api-service restart
```

### **Backup Procedures**
```bash
# Backup application code (without secrets)
tar -czf hms-backup-$(date +%Y%m%d).tar.gz \
  --exclude='.env' \
  --exclude='__pycache__' \
  /opt/hosting-api/
```

---

## 📊 Performance Monitoring

### **Key Metrics**
- Response time < 500ms
- Memory usage < 100MB
- CPU usage < 25%
- Disk space > 1GB free

### **Monitoring Commands**
```bash
# Check resource usage
ssh root@asterra.remoteds.us "ps aux | grep app_fastapi"
ssh root@asterra.remoteds.us "free -h"
ssh root@asterra.remoteds.us "df -h"
```

---

## 📞 Emergency Procedures

### **Service Recovery**
```bash
# Quick service restart
ssh root@asterra.remoteds.us "systemctl restart hms-api"

# Full service reset
ssh root@asterra.remoteds.us "systemctl stop hms-api"
ssh root@asterra.remoteds.us "systemctl start hms-api"

# Emergency rollback
git checkout HEAD~1
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
python deploy-secure-sync.py
```

### **Contact Information**
- **Admin Email**: brian@thinkcreatebuildit.com
- **Repository**: hosting-management-system
- **Documentation**: See [agents.md](agents.md) for complete system rules

---

## ✅ Deployment Success Criteria

### **Must Pass All Checks**
- [ ] Service running without errors
- [ ] HTTPS accessible with valid certificate
- [ ] Authentication functional
- [ ] Dashboard loads correctly
- [ ] TODO system operational
- [ ] API endpoints secured
- [ ] Logs clean of errors
- [ ] Security protocols followed

---

**Document Maintenance**: Update when deployment procedures change. All team members must re-read and re-certify when updated.

**Last Updated**: October 29, 2025  
**Next Review**: January 29, 2026

---

## 🔗 Related Documentation

- **[agents.md](agents.md)** - Master rules and architecture
- **[CIGAR_DEPLOYMENT_GUIDE.md](CIGAR_DEPLOYMENT_GUIDE.md)** - Cigar app deployment
- **[TOBACCO_DEPLOYMENT_GUIDE.md](TOBACCO_DEPLOYMENT_GUIDE.md)** - Tobacco app deployment
- **[README.md](../README.md)** - System overview
