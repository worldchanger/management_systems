# Quick Start Guide - Hosting Management System

## 🎯 **Current Status**
- ✅ Architecture finalized (Python FastAPI manages Rails apps - no circular dependency)
- ✅ Documentation complete (`agents.md`, `ARCHITECTURE_PLAN.md`, `ARCHITECTURE_SUMMARY.md`)
- ✅ Existing code: CLI tool (`manager.py`), FastAPI app (`app_fastapi.py`), tests
- 🔨 Ready for Phase 1 implementation

## 🚀 **Immediate Next Steps (This Week)**

### Step 1: Update .secrets.json
**Location**: `/Users/bpauley/Projects/mangement-systems/hosting-management-system/.secrets.json`

Add this section (generate secure values):
```json
{
  "hosting_management": {
    "admin_username": "admin",
    "admin_password": "GENERATE_SECURE_PASSWORD",
    "jwt_secret": "GENERATE_JWT_SECRET",
    "api_token": "GENERATE_API_TOKEN"
  },
  "ssl_config": {
    "hosting": {
      "domain": "hosting.remoteds.us",
      "cert_path": "/etc/nginx/ssl/hosting.remoteds.us/hosting.remoteds.us.crt",
      "key_path": "/etc/nginx/ssl/hosting.remoteds.us/hosting.remoteds.us.key"
    }
  }
}
```

**Generate values:**
```bash
# JWT secret (copy output to .secrets.json)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# API token
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Admin password (use a password manager or generate)
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### Step 2: Create Remote CLI Tools
```bash
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system
mkdir -p remote_cli_tools

# Create check_status.sh
cat > remote_cli_tools/check_status.sh << 'EOF'
#!/bin/bash
# Check status of all services
echo "=== Rails Apps ==="
for service in cigar tobacco; do
    status=$(systemctl is-active ${service}.service)
    echo "${service}: ${status}"
done

echo -e "\n=== Nginx ==="
systemctl is-active nginx

echo -e "\n=== Disk Usage ==="
df -h / | tail -1
EOF

chmod +x remote_cli_tools/check_status.sh

# Create parse_logs.sh
cat > remote_cli_tools/parse_logs.sh << 'EOF'
#!/bin/bash
# Parse logs for errors
APP=${1:-cigar}
PATTERN=${2:-ERROR}
LINES=${3:-50}

echo "=== Searching ${APP} logs for: ${PATTERN} ==="
journalctl -u ${APP}.service -n ${LINES} | grep -i "${PATTERN}" || echo "No matches found"
EOF

chmod +x remote_cli_tools/parse_logs.sh

# Create restart_service.sh
cat > remote_cli_tools/restart_service.sh << 'EOF'
#!/bin/bash
# Quick restart helper
SERVICE=$1

if [ -z "$SERVICE" ]; then
    echo "Usage: $0 <service_name>"
    exit 1
fi

echo "Restarting ${SERVICE}..."
systemctl restart ${SERVICE}.service
systemctl status ${SERVICE}.service --no-pager | head -5
EOF

chmod +x remote_cli_tools/restart_service.sh
```

### Step 3: Run Existing Tests
```bash
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system

# See what tests exist and their status
pytest -v

# Check coverage
pytest --cov=. --cov-report=term-missing
```

### Step 4: Create DEPLOYMENT_LOG.md
```bash
# Document the current deployment state
cat > DEPLOYMENT_LOG.md << 'EOF'
# Deployment Log - Hosting Management System

## Purpose
This log documents every step required to deploy the hosting management system and all Rails applications from a bare Ubuntu server to production-ready state.

## Prerequisites
- Ubuntu 25.04 LTS server
- Root SSH access
- Local machine with Python 3.12+
- `.secrets.json` file configured
- SSH deployment keys generated

## Deployment Steps

### Phase 1: Server Provisioning
(To be documented during next deployment)

### Phase 2: Hosting API Bootstrap
(To be documented)

### Phase 3: Rails Apps Deployment
(To be documented)

### Verification Steps
(To be documented)

---
Last Updated: [DATE]
Last Deployed By: [NAME]
Server IP: [IP]
EOF
```

## 📁 **Project Structure Overview**

```
/Users/bpauley/Projects/mangement-systems/
├── ARCHITECTURE_SUMMARY.md       # ← High-level overview
├── IMPLEMENTATION_SUMMARY.md     # ← What's done, what's next
├── QUICK_START.md               # ← This file
├── agents.md                    # ← Master architecture
├── TODO.md                      # ← Task tracking
├── config.json                  # ← Server configuration
├── .secrets.json               # ← Credentials (gitignored)
│
├── cigar-management-system/     # Git repo - Rails app
├── tobacco-management-system/   # Git repo - Rails app
│
└── hosting-management-system/   # Git repo - Management system
    ├── manager.py               # LOCAL: CLI tool
    ├── app_fastapi.py          # REMOTE: API (to refactor to web/)
    ├── web/                     # REMOTE: Web interface
    │   ├── templates/
    │   └── README.md
    ├── templates/               # Server config templates
    ├── remote_cli_tools/        # ← Create this with scripts
    ├── tests/                   # ← Update existing tests
    ├── DEPLOYMENT_LOG.md        # ← Create this
    ├── ARCHITECTURE_PLAN.md     # ← Detailed plan
    └── .secrets.json           # ← Update with hosting credentials
```

## 🎯 **Key Architectural Points**

1. **NO circular dependency**: Python FastAPI manages Rails apps
2. **Two interfaces**: 
   - Local CLI (`manager.py`) on your laptop
   - Remote Web UI (hosting.remoteds.us) for monitoring/control
3. **NO root-level git**: Only individual app repos
4. **Testing discipline**: No production deploys without passing tests
5. **Infrastructure as Code**: Everything scripted and repeatable

## 🔄 **Workflow Examples**

### Deploy a Rails App
```bash
# From laptop
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system

# Method 1: Via local CLI
python manager.py deploy --app cigar

# Method 2: Via web UI (after hosting API is deployed)
# Visit https://hosting.remoteds.us/deploy
```

### View Logs
```bash
# From laptop via CLI (to be implemented)
python manager.py logs --app cigar --lines 100

# Via web UI (to be implemented)
# Visit https://hosting.remoteds.us/logs
```

### Restart an App
```bash
# From laptop via CLI
python manager.py restart --app cigar

# Via web UI (to be implemented)
# Visit https://hosting.remoteds.us/dashboard → Click "Restart"
```

## 📚 **Documentation Map**

- **QUICK_START.md** (this file) - Immediate action items
- **ARCHITECTURE_SUMMARY.md** - Architecture overview and corrections
- **ARCHITECTURE_PLAN.md** - Detailed implementation phases
- **IMPLEMENTATION_SUMMARY.md** - Status, what exists, what needs building
- **SECURITY.md** - Secrets management and security practices
- **agents.md** - Master architecture document (updated)
- **TODO.md** - Task tracking board

## ✅ **Today's Checklist**

- [ ] Update `.secrets.json` with hosting_management section
- [ ] Create `remote_cli_tools/` directory with scripts
- [ ] Run `pytest -v` to see current test status
- [ ] Create `DEPLOYMENT_LOG.md` file
- [ ] Review `ARCHITECTURE_PLAN.md` for detailed phases
- [ ] Commit changes to hosting-management-system repo

## 🚨 **Important Reminders**

- **NEVER commit `.secrets.json`** - It's in `.gitignore`
- **Test locally first** - No production without passing tests
- **Document everything** - Update `DEPLOYMENT_LOG.md` as you go
- **No manual steps** - All provisioning must be scripted

## 🆘 **Getting Help**

- Review `ARCHITECTURE_PLAN.md` for detailed implementation guidance
- Check `agents.md` for architectural decisions and rationale
- See `IMPLEMENTATION_SUMMARY.md` for phase breakdown
- Tests are in `tests/` directory - run with `pytest -v`

---

**Next Action**: Update `.secrets.json` with hosting management credentials
**Time Estimate**: 10-15 minutes to complete today's checklist
**Status**: Ready to begin Phase 1 implementation
