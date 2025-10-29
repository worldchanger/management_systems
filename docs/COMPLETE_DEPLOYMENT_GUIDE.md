# 🚀 Complete Deployment Guide - All Applications

**Document Version**: 2.0  
**Last Updated**: October 28, 2025  
**Status**: ✅ **ACTIVE** - Must be followed for all deployments

---

## 📋 **Application Overview**

We have **THREE** distinct applications that require different deployment methods:

### **1. Hosting Management System**
- **Location**: `/opt/hosting-api/`
- **Purpose**: Main hosting management with TODO system
- **Service**: `hms-api.service`
- **Deploy Method**: `manager.py deploy-hosting-api`
- **Credentials**: From `.secrets.json` hosting_management section

### **2. Cigar Application** 
- **Location**: `/var/www/cigar/`
- **Purpose**: Cigar inventory management
- **Service**: `cigar.service`
- **Deploy Method**: Separate cigar deployment scripts
- **Credentials**: From `.secrets.json` cigar section

### **3. Tobacco Application**
- **Location**: `/var/www/tobacco/`  
- **Purpose**: Tobacco inventory management
- **Service**: `tobacco.service`
- **Deploy Method**: Separate tobacco deployment scripts
- **Credentials**: From `.secrets.json` tobacco section

---

## 🔒 **CRITICAL SECURITY RULES - ALL APPLICATIONS**

### **NEVER VIOLATE THESE PROTOCOLS**
1. **❌ NEVER copy .secrets.json to any remote server** - Security violation
2. **❌ NEVER commit secrets to git** - .secrets.json excluded in .gitignore
3. **❌ NEVER use hardcoded credentials** - Always use environment variables
4. **✅ ALWAYS use application-specific secure sync scripts**
5. **✅ ALWAYS verify .env file permissions - 600 with correct ownership**

---

## 🏗️ **Method 1: Hosting Management System Deployment**

### **Use When**: Deploying the main hosting system with TODO management

#### **Step 1: Code Deployment**
```bash
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system

# Commit any changes first
git add -A
git commit -m "Description of hosting changes"
git push origin main

# Deploy code to server
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
```

#### **Step 2: Secure Secrets Deployment**
```bash
# Sync secrets from local .secrets.json to remote .env
python deploy-secure-sync.py

# This script automatically:
# ✅ Creates /opt/hosting-api/.env with secure permissions
# ✅ Sets chmod 600 /opt/hosting-api/.env
# ✅ Sets chown www-data:www-data /opt/hosting-api/.env  
# ✅ Restarts hms-api.service
# ✅ Verifies service status
```

#### **Step 3: Verification**
```bash
# Check service status
ssh root@asterra.remoteds.us "systemctl status hms-api --no-pager"

# Verify .env permissions
ssh root@asterra.remoteds.us "ls -la /opt/hosting-api/.env"

# Test authentication
curl -s "https://hosting.remoteds.us/login" | grep -i login
```

#### **Login Credentials**:
- **URL**: `https://hosting.remoteds.us/login`
- **Username**: `admin`
- **Password**: From `.secrets.json` → `hosting_management` → `admin_password`

---

## 🚬 **Method 2: Cigar Application Deployment**

### **Use When**: Deploying the cigar inventory management system

#### **Step 1: Code Deployment**
```bash
cd /Users/bpauley/Projects/mangement-systems/cigar-app

# Commit changes
git add -A
git commit -m "Description of cigar changes"
git push origin main

# Deploy cigar application (use cigar-specific deployment script)
python deploy-cigar.py --project-dir /var/www/cigar
```

#### **Step 2: Secure Secrets Deployment**
```bash
# Sync cigar-specific secrets
python deploy-cigar-secrets.py

# This automatically:
# ✅ Creates /var/www/cigar/.env with secure permissions
# ✅ Sets chmod 600 /var/www/cigar/.env
# ✅ Sets chown www-data:www-data /var/www/cigar/.env
# ✅ Restarts cigar.service
```

#### **Step 3: Verification**
```bash
# Check cigar service
ssh root@asterra.remoteds.us "systemctl status cigar --no-pager"

# Verify .env permissions
ssh root@asterra.remoteds.us "ls -la /var/www/cigar/.env"
```

---

## 🍂 **Method 3: Tobacco Application Deployment**

### **Use When**: Deploying the tobacco inventory management system

#### **Step 1: Code Deployment**
```bash
cd /Users/bpauley/Projects/mangement-systems/tobacco-app

# Commit changes
git add -A
git commit -m "Description of tobacco changes"
git push origin main

# Deploy tobacco application (use tobacco-specific deployment script)
python deploy-tobacco.py --project-dir /var/www/tobacco
```

#### **Step 2: Secure Secrets Deployment**
```bash
# Sync tobacco-specific secrets
python deploy-tobacco-secrets.py

# This automatically:
# ✅ Creates /var/www/tobacco/.env with secure permissions
# ✅ Sets chmod 600 /var/www/tobacco/.env
# ✅ Sets chown www-data:www-data /var/www/tobacco/.env
# ✅ Restarts tobacco.service
```

#### **Step 3: Verification**
```bash
# Check tobacco service
ssh root@asterra.remoteds.us "systemctl status tobacco --no-pager"

# Verify .env permissions
ssh root@asterra.remoteds.us "ls -la /var/www/tobacco/.env"
```

---

## 🔄 **Combined Deployment Methods**

### **Option A: Deploy All Applications**
```bash
# 1. Deploy Hosting System
cd hosting-management-system && python manager.py deploy-hosting-api --project-dir /opt/hosting-api
python deploy-secure-sync.py

# 2. Deploy Cigar App
cd ../cigar-app && python deploy-cigar.py --project-dir /var/www/cigar
python deploy-cigar-secrets.py

# 3. Deploy Tobacco App  
cd ../tobacco-app && python deploy-tobacco.py --project-dir /var/www/tobacco
python deploy-tobacco-secrets.py
```

### **Option B: Code-only Updates (No Secrets Changes)**
```bash
# Use when ONLY code changes, no credential updates needed
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
python deploy-cigar.py --project-dir /var/www/cigar
python deploy-tobacco.py --project-dir /var/www/tobacco
```

### **Option C: Secrets-only Updates (No Code Changes)**
```bash
# Use when ONLY credentials need updating
python deploy-secure-sync.py        # Hosting secrets
python deploy-cigar-secrets.py      # Cigar secrets
python deploy-tobacco-secrets.py    # Tobacco secrets
```

---

## 🔧 **Service Management Commands**

### **Hosting Management System**
```bash
# Service control
ssh root@asterra.remoteds.us "systemctl status hms-api --no-pager"
ssh root@asterra.remoteds.us "systemctl restart hms-api"
ssh root@asterra.remoteds.us "systemctl stop hms-api"

# Logs
ssh root@asterra.remoteds.us "journalctl -u hms-api -n 50 --no-pager"
ssh root@asterra.remoteds.us "journalctl -u hms-api -f"
```

### **Cigar Application**
```bash
# Service control
ssh root@asterra.remoteds.us "systemctl status cigar --no-pager"
ssh root@asterra.remoteds.us "systemctl restart cigar"
ssh root@asterra.remoteds.us "journalctl -u cigar -n 50 --no-pager"
```

### **Tobacco Application**
```bash
# Service control
ssh root@asterra.remoteds.us "systemctl status tobacco --no-pager"
ssh root@asterra.remoteds.us "systemctl restart tobacco"
ssh root@asterra.remoteds.us "journalctl -u tobacco -n 50 --no-pager"
```

---

## 📊 **Environment Variables by Application**

### **Hosting Management System** (`/opt/hosting-api/.env`)
```bash
# Authentication
HMS_ADMIN_USER=admin
HMS_ADMIN_PASSWORD=<from .secrets.json hosting_management>
HMS_JWT_SECRET=<from .secrets.json hosting_management>
HMS_API_TOKEN=<from .secrets.json hosting_management>

# JWT Configuration
HMS_JWT_ACCESS_EXPIRATION_MINUTES=15
HMS_JWT_REFRESH_EXPIRATION_DAYS=7

# Optional
HMS_DISABLE_RATELIMIT=0
```

### **Cigar Application** (`/var/www/cigar/.env`)
```bash
# Database
DATABASE_URL=postgresql://user:<from .secrets.json cigar>@localhost/cigar_db
SECRET_KEY_BASE=<from .secrets.json cigar>

# Rails/Rack Configuration
RAILS_ENV=production
RACK_ENV=production
```

### **Tobacco Application** (`/var/www/tobacco/.env`)
```bash
# Database  
DATABASE_URL=postgresql://user:<from .secrets.json tobacco>@localhost/tobacco_db
SECRET_KEY_BASE=<from .secrets.json tobacco>

# Rails/Rack Configuration
RAILS_ENV=production
RACK_ENV=production
```

---

## 🚨 **Troubleshooting by Application**

### **Hosting Management System Issues**

#### **Authentication Fails**
```bash
# 1. Check .env file exists and has correct permissions
ssh root@asterra.remoteds.us "ls -la /opt/hosting-api/.env"

# 2. Check .env file content
ssh root@asterra.remoteds.us "grep HMS_ADMIN /opt/hosting-api/.env"

# 3. Resync secrets if needed
python deploy-secure-sync.py

# 4. Restart service
ssh root@asterra.remoteds.us "systemctl restart hms-api"
```

#### **Service Won't Start**
```bash
# Check logs for specific error
ssh root@asterra.remoteds.us "journalctl -u hms-api -n 20 --no-pager"

# Common issues:
# - Circular imports (check auth_utils.py usage)
# - Missing environment variables
# - Template path errors (should be web/templates/)
```

### **Cigar/Tobacco Application Issues**

#### **Database Connection Errors**
```bash
# Check .env file credentials
ssh root@asterra.remoteds.us "grep DATABASE_URL /var/www/cigar/.env"

# Verify database is running
ssh root@asterra.remoteds.us "systemctl status postgresql"

# Resync secrets if needed
python deploy-cigar-secrets.py  # or deploy-tobacco-secrets.py
```

---

## 📋 **Pre-deployment Checklist**

### **For All Applications**
- [ ] Code committed to git
- [ ] No hardcoded credentials in code
- [ ] All environment variables referenced
- [ ] Test environment variables updated if needed
- [ ] Backup of current system created

### **Hosting Management System Specific**
- [ ] Authentication dependencies use `auth_utils.py` (no circular imports)
- [ ] Templates in `web/templates/` directory
- [ ] TODO.md file exists and accessible
- [ ] Unit tests passing locally

### **Cigar/Tobacco Applications Specific**
- [ ] Database migrations planned
- [ ] Asset precompilation needed (Rails)
- [ ] Background job processes checked

---

## 📞 **Emergency Procedures**

### **Rollback All Applications**
```bash
# Hosting system
git checkout HEAD~1
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
python deploy-secure-sync.py

# Cigar app
cd ../cigar-app && git checkout HEAD~1
python deploy-cigar.py --project-dir /var/www/cigar
python deploy-cigar-secrets.py

# Tobacco app
cd ../tobacco-app && git checkout HEAD~1
python deploy-tobacco.py --project-dir /var/www/tobacco
python deploy-tobacco-secrets.py
```

### **Quick Service Recovery**
```bash
# Restart all services
ssh root@asterra.remoteds.us "systemctl restart hms-api cigar tobacco"

# Check all services status
ssh root@asterra.remoteds.us "systemctl status hms-api cigar tobacco --no-pager"
```

---

## ✅ **Certification Required**

**I have read and understand these deployment protocols. I will:**

- [ ] **NEVER** copy .secrets.json to any remote server
- [ ] **ALWAYS** use application-specific deployment scripts
- [ ] **ALWAYS** verify .env file permissions (600, correct ownership)
- [ ] **ALWAYS** use the correct deployment method for each application
- [ ] **NEVER** commit secrets to version control

---

## 🔗 **Quick Reference Commands**

| Application | Deploy Command | Secrets Command | Service Name | URL |
|-------------|----------------|-----------------|--------------|-----|
| Hosting | `python manager.py deploy-hosting-api --project-dir /opt/hosting-api` | `python deploy-secure-sync.py` | `hms-api` | `https://hosting.remoteds.us` |
| Cigar | `python deploy-cigar.py --project-dir /var/www/cigar` | `python deploy-cigar-secrets.py` | `cigar` | `https://cigar.remoteds.us` |
| Tobacco | `python deploy-tobacco.py --project-dir /var/www/tobacco` | `python deploy-tobacco-secrets.py` | `tobacco` | `https://tobacco.remoteds.us` |

---

**Document Maintenance**: Update when deployment procedures change. All team members must re-certify when updated.

### **📖 Authoritative Documentation**
This document is part of the authoritative documentation set. See **[agents.md](../agents.md)** for:
- Complete documentation hierarchy and reading requirements
- AI agent protocols and security guidelines
- System architecture specifications
- Cross-references to all related documentation

**Last Updated**: October 28, 2025  
**Next Review**: January 28, 2026
