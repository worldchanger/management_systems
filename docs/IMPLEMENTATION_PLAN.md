# Deployment Process Fix Plan

**Date**: October 31, 2025 @ 22:45 UTC-04:00  
**Status**: 🔧 **IN PROGRESS**

---

## 🎯 **Objective**

Fix the `manager.py deploy` command to handle ALL deployment steps in a single command with proper `--setup` flag support for new deployments.

---

## 📋 **Issues Identified**

### **1. Debug Gem Loading in Production**
- ❌ **Problem**: Bundle install was loading development gems including `debug`
- ✅ **Fix**: Use `bundle install --without development test` to skip dev gems

### **2. Database Creation Process**
- ❌ **Problem**: Creating database when creating user
- ✅ **Fix**: Only create USER with CREATEDB privilege, let `rake db:create` handle database

### **3. Git Clone Method**
- ❌ **Problem**: Using HTTPS URL requires interactive authentication
- ✅ **Fix**: Use SSH URL format `git@github.com:worldchanger/repo.git`

### **4. Manual Commands**
- ❌ **Problem**: Required multiple manual commands to complete deployment
- ✅ **Fix**: Single `python manager.py deploy --app cigar --setup` command

### **5. Fabric Installation**
- ❌ **Problem**: Installing fabric every deployment
- ✅ **Fix**: Fabric already in requirements.txt, installed during provision

### **6. Missing Deployment Steps**
- ❌ **Problem**: Systemd/nginx configs not deployed automatically
- ✅ **Fix**: Deploy configs as part of deploy_app method

### **7. Secrets Deployment**
- ❌ **Problem**: deploy-secure-sync.py not integrated
- ✅ **Fix**: Call deploy-secure-sync.py from deploy_app method

### **8. SSL Certificate**
- ❌ **Problem**: Not issued during deployment
- ✅ **Fix**: Issue SSL cert as part of deploy_app (staging first)

---

## 🔧 **Required Changes to manager.py**

### **New deploy_app Method Flow:**

```python
def deploy_app(self, key: str, branch: str = "main", setup: bool = False) -> None:
    """
    Complete deployment in ONE command.
    
    Steps:
    1. Create remote directory
    2. Create PostgreSQL USER only (if --setup, with CREATEDB privilege)
    3. Clone repo via SSH (or git pull if exists)
    4. Bundle install --without development test (NO debug gem)
    5. Deploy systemd service file template
    6. Run deploy-secure-sync.py to inject secrets
    7. Create database with rake db:create (if --setup)
    8. Run rake db:migrate
    9. Run rake assets:precompile
    10. Deploy nginx config
    11. Issue SSL certificate (if --setup)
    12. Restart nginx
    13. systemctl daemon-reload
    14. systemctl enable puma-{app}
    15. systemctl start puma-{app}
    16. Verify service is running
    """
```

---

## 📝 **Step-by-Step Implementation**

### **Step 1: Fix Git Clone**
```python
# Use SSH URL, not HTTPS
ssh_repo = app.github_repo.replace('https://github.com/', 'git@github.com:')
conn.sudo(f"git clone -b {branch} {ssh_repo} {repo_path}")
```

### **Step 2: Fix Bundle Install**
```python
# NO development or test gems
conn.sudo(f"cd {repo_path} && bundle install --without development test")
```

### **Step 3: Create USER Only (No Database)**
```python
if setup:
    # Only create user, NOT database
    create_user_sql = """
        CREATE USER {username} WITH PASSWORD '{password}' CREATEDB;
    """
    conn.sudo(f'sudo -u postgres psql -c "{create_user_sql}"')
```

### **Step 4: Deploy Systemd Service Template**
```python
# Deploy basic service file WITHOUT secrets
self._deploy_systemd_service(conn, app)
conn.sudo("systemctl daemon-reload")
```

### **Step 5: Inject Secrets via deploy-secure-sync.py**
```python
# Run on remote server
conn.sudo("cd /opt/hosting-api && .venv/bin/python deploy-secure-sync.py --app {key}")
```

### **Step 6: Create Database**
```python
if setup:
    # Source environment from systemd file
    env_source = "source <(grep ^Environment= /etc/systemd/system/puma-{app}.service | sed 's/^Environment=//' | sed 's/^/export /')"
    conn.sudo(f"cd {repo_path} && bash -c '{env_source && bundle exec rake db:create RAILS_ENV=production'")
```

### **Step 7: Run Migrations**
```python
# Use environment from systemd
conn.sudo(f"cd {repo_path} && bash -c '{env_source && bundle exec rake db:migrate RAILS_ENV=production'")
```

### **Step 8: Compile Assets**
```python
# Use environment from systemd
conn.sudo(f"cd {repo_path} && bash -c '{env_source && bundle exec rake assets:precompile RAILS_ENV=production'")
```

### **Step 9: Deploy Nginx Config**
```python
self._deploy_nginx_config(conn, app)
```

### **Step 10: Issue SSL Certificate**
```python
if setup:
    email = self.get_app_letsencrypt_email(key)
    conn.sudo(f"certbot --nginx -d {app.domain} --email {email} --agree-tos -n --staging")
```

### **Step 11: Restart Nginx**
```python
conn.sudo("nginx -t")  # Test config
conn.sudo("systemctl restart nginx")
```

### **Step 12: Start Puma Service**
```python
conn.sudo("systemctl daemon-reload")
conn.sudo(f"systemctl enable puma-{key}")
conn.sudo(f"systemctl start puma-{key}")
time.sleep(3)
conn.sudo(f"systemctl status puma-{key} --no-pager")
```

---

## ✅ **Success Criteria**

### **Single Command Deployment:**
```bash
# New deployment (first time)
python manager.py deploy --app cigar --setup

# Re-deployment (updates)
python manager.py deploy --app cigar
```

### **Expected Output:**
```
🚀 Deploying Cigar Management System from branch main (setup=True)
📁 Step 1: Creating remote directory /var/www/cigar
👤 Step 2: Creating PostgreSQL user cigar_management_system_production
✅ User created (CREATEDB privilege granted)
📦 Step 3: Cloning repository via SSH
✅ Repository cloned
💎 Step 4: Installing Ruby dependencies (production mode)
✅ Bundle install complete (96 gems, NO debug gem)
⚙️ Step 5: Deploying systemd service file
✅ Systemd service file deployed
🔐 Step 6: Deploying secrets via deploy-secure-sync.py
✅ Secrets deployed to systemd
🗄️ Step 7: Creating database with rake db:create
✅ Database created
🔄 Step 8: Running database migrations
✅ Migrations complete
🎨 Step 9: Precompiling assets
✅ Assets compiled
🌐 Step 10: Deploying Nginx configuration
✅ Nginx config deployed
🔒 Step 11: Issuing SSL certificate
✅ SSL certificate issued (staging)
♻️ Step 12: Restarting nginx
✅ Nginx restarted
🚦 Step 13: Enabling and starting puma service
✅ Puma service started
🎉 Deployment of Cigar Management System complete!
📊 Verify at: https://cigars.remoteds.us
```

---

## 🚫 **What NOT to Do**

1. ❌ Do NOT use HTTPS git clone URLs
2. ❌ Do NOT install development/test gems in production
3. ❌ Do NOT create database when creating user
4. ❌ Do NOT install fabric during deployment (already in requirements.txt)
5. ❌ Do NOT manually run rsync instead of git clone
6. ❌ Do NOT manually run bundle/rake commands
7. ❌ Do NOT forget to deploy systemd/nginx configs
8. ❌ Do NOT skip deploy-secure-sync.py
9. ❌ Do NOT skip SSL certificate issuance

---

## 📋 **Implementation Checklist**

- [ ] Decommission current cigar deployment
- [ ] Rewrite deploy_app method in manager.py
- [ ] Test deployment with --setup flag
- [ ] Verify single-command works
- [ ] Update CIGAR_DEPLOYMENT_GUIDE.md
- [ ] Update ARCHITECTURE_PLAN.md
- [ ] Deploy HMS changes to server
- [ ] Test cigar deployment end-to-end

---

## 🎯 **Next Actions**

1. Decommission cigar app cleanly
2. Rewrite manager.py deploy_app method
3. Test on server
4. Update documentation
5. Deploy HMS
6. Deploy cigar with single command

---

This plan ensures the deployment process is:
- ✅ Automated
- ✅ Repeatable
- ✅ Database-first
- ✅ Secure
- ✅ Production-ready
