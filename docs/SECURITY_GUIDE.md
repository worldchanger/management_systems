# 🔒 Hosting Management System Security Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Security Architecture](#security-architecture)
- [Deployment Process](#deployment-process)
- [Authentication & Authorization](#authentication--authorization)
- [Environment Variables](#environment-variables)
- [File Permissions](#file-permissions)
- [Backup & Recovery](#backup--recovery)
- [Maintenance & Operations](#maintenance--operations)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Hosting Management System uses a **secure environment variable approach** for credential management, eliminating the security risks associated with secrets files in production deployments.

### **Key Security Features**
- ✅ Environment variables instead of secrets files
- ✅ Restricted file permissions (600)
- ✅ Principle of least privilege
- ✅ Automated secrets synchronization
- ✅ JWT-based authentication
- ✅ Secure logout functionality

---

## 🏗️ Security Architecture

### **Before (Insecure)**
```
/opt/hosting-api/
├── .secrets.json  ← Contains ALL secrets for ALL apps
├── app_fastapi.py
└── web/
```

### **After (Secure)**
```
/opt/hosting-api/
├── .env           ← Contains ONLY HMS secrets (600 permissions)
├── app_fastapi.py
└── web/

Development Machine:
├── .secrets.json  ← Stays LOCAL, never deployed
└── deployment scripts
```

### **Security Improvements**
| **Aspect** | **Before** | **After** | **Improvement** |
|------------|------------|-----------|-----------------|
| **Secrets Exposure** | 11 secrets exposed | 4 secrets exposed | **64% reduction** |
| **File Access** | Default permissions | 600 permissions | **Restricted access** |
| **Backup Risk** | All secrets included | Only HMS secrets | **Minimized exposure** |
| **Version Control** | Risk of committing | .env excluded | **No git risk** |

---

## 🚀 Deployment Process

### **Automated Secure Deployment**

Use the provided deployment script for secure, automated deployments:

```bash
# Deploy with automatic secrets sync
python deploy-secure-sync.py
```

### **Manual Deployment Steps**

If manual deployment is needed:

1. **Deploy Application Code**
   ```bash
   python manager.py deploy-hosting-api --project-dir /opt/hosting-api --port 5051
   ```

2. **Sync Environment Variables**
   ```bash
   python deploy-secure-sync.py
   ```

3. **Verify Deployment**
   ```bash
   python manager.py hms-api-service status
   ```

### **What Gets Deployed**

- ✅ Application code without secrets
- ✅ Environment file with HMS-specific secrets only
- ✅ Updated systemd service configuration
- ✅ Proper file permissions and ownership

---

## 🔐 Authentication & Authorization

### **JWT Configuration**
- **Algorithm**: HS256
- **Access Token Expiry**: 15 minutes
- **Refresh Token Expiry**: 7 days
- **Cookie Settings**: HTTP-only, secure flag for production

### **Login Process**
```bash
# Test login functionality
curl -X POST https://hosting.remoteds.us/login \
  -d "username=admin&password=your-password" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

### **Logout Process**
```bash
# Test logout functionality (GET request)
curl -b cookies.txt https://hosting.remoteds.us/logout
```

### **Environment Variables for Authentication**
```bash
HMS_ADMIN_USER=admin
HMS_ADMIN_PASSWORD=your-secure-password
HMS_JWT_SECRET=your-jwt-secret-min-32-chars
HMS_API_TOKEN=your-api-token
```

---

## 🌍 Environment Variables

### **Required Variables**
| **Variable** | **Description** | **Example** |
|--------------|-----------------|-------------|
| `HMS_ADMIN_USER` | Admin username | `admin` |
| `HMS_ADMIN_PASSWORD` | Admin password | `secure-password-123` |
| `HMS_JWT_SECRET` | JWT signing secret | `random-32-char-string` |
| `HMS_API_TOKEN` | API authentication token | `api-token-string` |
| `HMS_JWT_ACCESS_EXPIRATION_MINUTES` | Token expiry time | `15` |
| `HMS_JWT_REFRESH_EXPIRATION_DAYS` | Refresh token expiry | `7` |

### **Environment File Template**
```bash
# /opt/hosting-api/.env
# Hosting Management System Environment Variables
# Auto-generated from root .secrets.json
# DO NOT commit to version control

# Authentication Configuration
HMS_ADMIN_USER=admin
HMS_ADMIN_PASSWORD=your-secure-password-here
HMS_JWT_SECRET=your-jwt-secret-here-min-32-chars
HMS_API_TOKEN=your-api-token-here

# JWT Configuration
HMS_JWT_ACCESS_EXPIRATION_MINUTES=15
HMS_JWT_REFRESH_EXPIRATION_DAYS=7
```

---

## 🔒 File Permissions

### **Secure File Setup**
```bash
# Environment file permissions
chmod 600 /opt/hosting-api/.env
chown www-data:www-data /opt/hosting-api/.env

# Verification
ls -la /opt/hosting-api/.env
# Output: -rw------- 1 www-data www-data 440 Oct 28 02:39 .env
```

### **Directory Structure**
```bash
/opt/hosting-api/
├── .env              ← 600 permissions, www-data:www-data
├── env.template      ← 644 permissions, reference only
├── app_fastapi.py    ← Application code
└── web/              ← Templates and static files
```

---

## 💾 Backup & Recovery

### **Safe Backup Process**
```bash
# Backup code (without secrets)
tar -czf hms-code-backup.tar.gz \
  --exclude='.env' \
  --exclude='.secrets.json' \
  /opt/hosting-api/

# Backup environment separately (if needed)
gpg --symmetric --cipher-algo AES256 /opt/hosting-api/.env
```

### **Recovery Process**
1. Restore application code
2. Run secure deployment script to recreate environment
3. Restart service
4. Verify functionality

---

## 🔧 Maintenance & Operations

### **Credential Rotation**
```bash
# Update root .secrets.json locally
# Then run deployment script
python deploy-secure-sync.py
```

### **Service Management**
```bash
# Check service status
python manager.py hms-api-service status

# Restart service
python manager.py hms-api-service restart

# View logs
python manager.py tail-logs --unit hms-api
```

### **Monitoring**
```bash
# Check environment variables
sudo cat /opt/hosting-api/.env

# Verify file permissions
ls -la /opt/hosting-api/.env

# Monitor service logs
sudo journalctl -u hms-api -f
```

---

## 🛠️ Troubleshooting

### **Common Issues**

#### **1. Service Won't Start**
```bash
# Check if environment file exists
ls -la /opt/hosting-api/.env

# Check file permissions
sudo chmod 600 /opt/hosting-api/.env
sudo chown www-data:www-data /opt/hosting-api/.env

# Check service logs
python manager.py tail-logs --unit hms-api
```

#### **2. Authentication Fails**
```bash
# Verify environment variables
sudo cat /opt/hosting-api/.env

# Test environment loading
cd /opt/hosting-api
source .env
echo $HMS_ADMIN_USER
echo $HMS_ADMIN_PASSWORD
```

#### **3. Logout Returns 405 Error**
```bash
# Ensure logout route is GET, not POST
# Check app_fastapi.py for:
@app.get("/logout")  # Should be GET, not POST
```

### **Debug Commands**
```bash
# Test login with curl
curl -X POST https://hosting.remoteds.us/login \
  -d "username=admin&password=your-password" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -i

# Test dashboard access
curl -b cookies.txt https://hosting.remoteds.us/ | grep "<title>"

# Check service status
python manager.py hms-api-service status
```

---

## 📊 Security Checklist

### **Deployment Security**
- [ ] `.secrets.json` never deployed to production
- [ ] Environment file has 600 permissions
- [ ] Only www-data user can read environment file
- [ ] JWT secrets are at least 32 characters
- [ ] HTTPS is enabled in production

### **Operational Security**
- [ ] Regular credential rotation
- [ ] Environment file excluded from backups
- [ ] Service logs monitored for authentication failures
- [ ] File permissions checked regularly
- [ ] No secrets in version control

### **Compliance**
- [ ] Principle of least privilege implemented
- [ ] Audit trail for configuration changes
- [ ] Secure backup procedures
- [ ] Documentation maintained
- [ ] Security review completed

---

## 🎯 Best Practices

### **Development**
- Keep `.secrets.json` in project root only
- Never commit secrets to version control
- Use environment variables for all configuration
- Test deployment process regularly

### **Production**
- Use secure deployment script for all updates
- Monitor service logs for security issues
- Regular security audits
- Keep documentation updated

### **Security**
- Rotate credentials regularly
- Use strong, unique passwords
- Enable HTTPS in production
- Monitor for unauthorized access

---

## 📞 Support

For security issues or questions:
1. Check this documentation first
2. Review service logs
3. Verify environment configuration
4. Test with provided debug commands

---

## 📈 Security Evolution

This security implementation represents a significant improvement over the previous secrets file approach:

- **64% reduction** in exposed secrets
- **Industry-standard** environment variable approach
- **Automated** deployment and synchronization
- **Compliance-ready** security posture
- **Maintainable** long-term solution

**The system is now secure, maintainable, and ready for production use!** 🚀🔒
