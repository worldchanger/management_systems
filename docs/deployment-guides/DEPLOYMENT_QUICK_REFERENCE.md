# Deployment Quick Reference Guide

**Last Updated**: November 1, 2025 2:30 PM EST  
**Version**: 1.0

---

## 🚀 Quick Redeployment Commands

### **Using manager.py (Recommended)**

For routine redeployments (code updates only, no database wipe):

```bash
# Cigar App
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --local"

# Tobacco App
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app tobacco --local"

# Whiskey App
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app whiskey --local"
```

**Important**: The `--local` flag ensures:
- ✅ Pulls latest code from GitHub
- ✅ Runs `bundle install`
- ✅ Runs `rails assets:precompile`
- ✅ Runs `rails db:migrate` (safe - only adds new migrations)
- ✅ Restarts the application service
- ❌ Does NOT wipe or recreate the database
- ❌ Does NOT run `db:setup` or `db:seed`

---

## 🔄 Deployment Workflow

### **1. Local Testing (Development/Test - Darwin)**

```bash
# Stop all local apps
cd /Users/bpauley/Projects/mangement-systems
./local-rails-apps.sh stop all

# Start all local apps
./local-rails-apps.sh start all

# Run unit tests
cd whiskey-management-system && bundle exec rspec
cd ../cigar-management-system && bundle exec rspec
cd ../tobacco-management-system && bundle exec rspec

# Run local curl tests
cd .. && ./test-apps-local.sh
```

### **2. Verify Code Committed**

```bash
# Check each repo
cd cigar-management-system && git status
cd ../tobacco-management-system && git status
cd ../whiskey-management-system && git status

# If changes exist, commit and push
git add -A
git commit -m "Description of changes"
git push origin main
```

### **3. Verify Remote Status**

```bash
# Check if remote is up to date
ssh root@asterra.remoteds.us "cd /var/www/cigar && git status"
ssh root@asterra.remoteds.us "cd /var/www/tobacco && git status"
ssh root@asterra.remoteds.us "cd /var/www/whiskey && git status"
```

### **4. Deploy if Needed**

Only deploy if remote `git status` shows it's behind:

```bash
# Deploy using manager.py (recommended)
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --local"
```

### **5. Remote Testing (Production - Linux)**

```bash
# Run remote curl tests
./test-apps-remote.sh
```

---

## 🔁 Iterative Fix Process

If tests fail at any point:

1. **Stop** - Note the error
2. **Fix** - Make changes in local Darwin environment
3. **Test Locally** - Run unit tests + curl tests until all pass
4. **Commit** - Push to GitHub
5. **Deploy** - Use manager.py to redeploy
6. **Test Remote** - Run remote curl tests
7. **Repeat** - If remote tests fail, go back to step 1

**Never** make changes directly on production server.

---

## ⚠️ Safety Rules

1. **Never use force deploy** unless explicitly rebuilding from scratch
2. **Always test locally first** before deploying
3. **Check git status** on remote before deploying
4. **Only deploy if code has changed**
5. **Run remote tests** after every deployment
6. **Never hardcode credentials** - use environment variables
7. **Update design docs** when functionality changes
8. **Update test files** when functionality changes

---

## 📝 Environment Variables

### **Development (Local)**
- Stored in each app's `.env` file
- Login credentials: `DEV_CIGAR_EMAIL`, `DEV_CIGAR_PASSWORD` (from hosting_production.global_admin_users)

### **Production (Remote)**
- Managed by systemd service files in `/etc/systemd/system/`
- Login credentials: `PROD_CIGAR_EMAIL`, `PROD_CIGAR_PASSWORD`

---

## 📚 Related Documentation

- [Cigar Deployment Guide](./CIGAR_DEPLOYMENT_GUIDE.md)
- [Tobacco Deployment Guide](./TOBACCO_DEPLOYMENT_GUIDE.md)
- [Testing Strategies](../testing-strategies/)
- [Architecture Overview](../architecture-security/ARCHITECTURE_SUMMARY.md)
