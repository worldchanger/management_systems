# Agents.md: Master Development Rules & System Architecture

**Status**: ✅ **GOLDEN RULES DOCUMENT** - Must be read before any development work  
**Last Updated**: October 31, 2025  
**Version**: 3.1 - CRITICAL DATABASE-FIRST RULES ADDED

---

## 🚨 CRITICAL RULES - NEVER VIOLATE THESE 🚨

### **RULE #1: DATABASE-FIRST ARCHITECTURE - All Secrets from PostgreSQL**

**THIS IS ABSOLUTELY MANDATORY - READ CAREFULLY:**

#### **On Remote Server (Linux/Ubuntu):**
1. **NO .env files on the server** - EVER. Not `.env.production`, not `.env.local`, not `/opt/hosting-api/.env`. NOTHING.
2. **NO .secrets.json files on the server** - Not for Rails apps, not for HMS. NO FILES.
3. **NO config.json files on the server** - Database is the ONLY config source.
4. **ALL secrets come from the database** - `hosting_production` PostgreSQL database on `asterra.remoteds.us` is the ONLY source of truth.
5. **Secrets go DIRECTLY into systemd service files** - Write them as `Environment=` variables in `/etc/systemd/system/puma-{app}.service` AND `/etc/systemd/system/hms-api.service`

#### **On Local Mac (Darwin):**
1. **✅ .env files ARE allowed** - Only on Mac localhost for local development
2. **✅ .secrets.json allowed** - For local development reference only
3. **⚠️ Before writing .env files**: Check `uname` - if returns `Linux` (remote server), use database; if returns `Darwin` (Mac), can use .env files
4. **✅ All .env files must be in .gitignore**

**THIS APPLIES TO:**
- ✅ Rails apps (cigar, tobacco, whiskey) - Secrets from `apps` table in `hosting_production` database
- ✅ HMS (Hosting Management System) - Secrets from `hms_config` table in `hosting_production` database

**Example of CORRECT systemd service file on remote server:**
```ini
[Service]
Environment=RAILS_ENV=production
Environment=SECRET_KEY_BASE={value_from_hosting_production_database}
Environment=CIGAR_DATABASE_PASSWORD={value_from_hosting_production_database}
Environment=CIGAR_API_TOKEN={value_from_hosting_production_database}
Environment=OPENROUTER_API_KEY={value_from_hosting_production_database}
```

**WRONG - NEVER DO THIS ON REMOTE SERVER:**
```ini
EnvironmentFile=/var/www/cigar/.env.production  ❌ NEVER ON LINUX
EnvironmentFile=/var/www/cigar/shared/.env.production  ❌ NEVER ON LINUX
EnvironmentFile=/opt/hosting-api/.env  ❌ NEVER ON LINUX
```

### **RULE #2: USE DEPLOYMENT GUIDES**

**All deployment procedures are documented in dedicated guides:**
- **[docs/deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md](docs/deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md)** - Cigar app deployment
- **[docs/deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md](docs/deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md)** - Tobacco app deployment  
- **[docs/deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md](docs/deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md)** - HMS deployment
- **[docs/deployment-guides/COMPLETE_DEPLOYMENT_GUIDE.md](docs/deployment-guides/COMPLETE_DEPLOYMENT_GUIDE.md)** - Full system deployment

**DO NOT create ad-hoc deployment procedures. Always follow the documented guides.**

---

### **RULE #3: DEPLOYMENT AND DECOMMISSION COMMANDS**

#### **🚀 Production Deployment Commands (Run from Mac localhost)**

**First-Time Deployment (Setup):**
```bash
# Deploy cigar app (first time)
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --setup --local"

# Deploy tobacco app (first time)
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app tobacco --setup --local"

# Deploy whiskey app (first time)
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app whiskey --setup --local"
```

**Redeployment (Updates):**
```bash
# Redeploy cigar app (runs migrations only)
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --migrate-only"

# Redeploy tobacco app (runs migrations only)
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app tobacco --migrate-only"

# Redeploy whiskey app (runs migrations only)
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app whiskey --migrate-only"
```

**Health Check:**
```bash
# Check app health after deployment
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py health-check --app {app_name}"
```

#### **🚨 DESTRUCTIVE: Decommission Commands**

**⚠️ CRITICAL WARNING: These commands are EXTREMELY DESTRUCTIVE**

These commands will completely destroy the application and remove ALL traces from the server:
- ❌ Stops and removes systemd services
- ❌ Removes all application files from `/var/www/{app}`
- ❌ Drops the PostgreSQL database
- ❌ Removes database users/roles
- ❌ Removes Nginx configuration
- ❌ Removes SSL certificates
- ✅ **PRESERVES database backups in `/opt/backups/postgresql/{app}`**

**RULES:**
1. **NEVER run these commands without explicit user permission**
2. **User must say "decommission {app-name}"** for you to execute
3. **Always confirm with user before running**
4. **Can process multiple apps if user provides multiple names**
5. **Always use `--force` flag** (prevents accidental runs)

```bash
# Decommission cigar app
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python decommission-app.py --app cigar --force"

# Decommission tobacco app
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python decommission-app.py --app tobacco --force"

# Decommission whiskey app
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python decommission-app.py --app whiskey --force"
```

**Example: User requests multiple decommissions**
```bash
# User says: "decommission cigar and tobacco"
for app in cigar tobacco; do
  ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python decommission-app.py --app $app --force"
done
```

#### **📝 Local Development (Mac localhost)**

**Use local-rails-apps.sh script:**
```bash
# Located at: /Users/bpauley/Projects/mangement-systems/local-rails-apps.sh

# Start all apps locally
./local-rails-apps.sh start all

# Start specific app
./local-rails-apps.sh start cigar

# Stop all apps
./local-rails-apps.sh stop all

# Test specific app
./local-rails-apps.sh test cigar

# Restart app
./local-rails-apps.sh restart cigar
```

---

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Core Development Rules](#core-development-rules)
- [Required Documentation Reading](#required-documentation-reading)
- [Development Workflow](#development-workflow)
- [Security Protocols](#security-protocols)
- [Testing Requirements](#testing-requirements)
- [Deployment Rules](#deployment-rules)
- [Code Quality Standards](#code-quality-standards)
- [Quick Reference Links](#quick-reference-links)

---

## 🏗️ System Overview

This workspace contains **three interconnected management systems** designed for inventory tracking and infrastructure management:

### **Core Applications**
1. **Cigar Management System** - Track cigar inventory across humidors with OCR support
2. **Tobacco Management System** - Track tobacco products and storage management  
3. **Hosting Management System** - Deploy, monitor, and manage the Rails applications

### **Technology Stack**
- **Rails Applications**: Ruby 3.3+, Rails 7.2.2, PostgreSQL, Puma
- **Hosting System**: Python FastAPI, SQLite, Nginx
- **Infrastructure**: Ubuntu 25.04 LTS, systemd services, Let's Encrypt SSL

### **Production Domains**
- **Cigar App**: https://cigars.remoteds.us
- **Tobacco App**: https://tobacco.remoteds.us
- **Hosting Management**: https://hosting.remoteds.us

### **Repository Structure**
```
management-systems/                    # Root workspace repository
├── agents.md                         # Master development rules
├── README.md                         # System overview
├── config.json                       # LOCAL MAC ONLY - Dev reference (gitignored)
├── .secrets.json                     # LOCAL MAC ONLY - Dev secrets (gitignored)
├── docs/                             # Consolidated documentation (organized in folders)
│   ├── README.md                     # Documentation master index
│   ├── application-design-documents/ # App design specifications
│   ├── deployment-guides/            # Deployment procedures
│   ├── architecture-security/        # Architecture & security docs
│   └── reference/                    # Change tracking, dev guides
├── cigar-management-system/          # Individual app repository (gitignored)
├── tobacco-management-system/        # Individual app repository (gitignored)
├── whiskey-management-system/        # Individual app repository (gitignored)
├── hosting-management-system/        # Individual app repository (gitignored)
└── qa-test-repo/                     # Testing repository (gitignored)

**⚠️ IMPORTANT**: config.json and .secrets.json exist ONLY on Mac localhost for development.
Production uses hosting_production PostgreSQL database as sole source of truth.
```

---

## 🎯 Core Development Rules

### **1. Task Tracking via Kanban API (MANDATORY)**

**ALL task management is done via the PostgreSQL-backed Kanban API**

#### Start of Work Session
```bash
# Fetch all current tasks from server
cd hosting-management-system
python scripts/kanban/fetch_tasks.py

# Review your tasks (saved to scripts/kanban/my_tasks.json)
cat scripts/kanban/my_tasks.json | jq '.tasks[] | select(.section == "In Progress")'
```

#### When User Assigns New Tasks
```bash
# Check if task exists in your fetched tasks
# If NOT found, create it:
python scripts/kanban/add_task.py \
  --content "Task description" \
  --priority high \
  --section "In Progress" \
  --epic "category" \
  --owner "agent"

# Then refresh your task list
python scripts/kanban/fetch_tasks.py
```

#### When You Complete Tasks
```bash
# Edit scripts/kanban/my_tasks.json
# Change task status from "pending" to "completed"
# Change section to "Completed" if needed

# Then sync changes back to server
python scripts/kanban/sync_tasks.py
```

#### End of Work Session
```bash
# Final sync of all changes
python scripts/kanban/sync_tasks.py

# Verify sync succeeded
python scripts/kanban/fetch_tasks.py
```

**Rules**:
- **NEVER use docs/TODO.md** - it's deprecated
- **ALWAYS** fetch tasks at session start
- **ALWAYS** sync tasks at session end
- Server is the source of truth
- All changes go through the API
- See: `hosting-management-system/scripts/kanban/README.md`

### **2. Question Ambiguity**
- Treat every unclear requirement as a topic for clarification
- Surface questions early to confirm assumptions before coding
- Never make assumptions about user requirements

### **3. Documentation First**
- Every folder across all repositories must contain a README.md
- Include purpose, architecture relationships, entry points, and usage patterns
- Include at least one relevant Mermaid diagram (flowchart, sequence, or class)

### **4. Code Commentary Discipline**
- Provide concise, high-value inline comments for complex logic only
- Default to self-documenting code
- Ensure docstrings/YARD/Sphinx annotations stay current

### **5. Change Tracking**
- Update `docs/CHANGELOG.md` alongside any notable modification
- Log date, author (AI agent), and summary
- Use domain-based sections (UI, API, storage, images, tasks, QA, docs, ops)

### **6. Task Hygiene**
- Use the Kanban API system via scripts (see Rule #1)
- Move tasks between sections: Backlog → In Progress → Completed
- Capture priorities (low/medium/high) per task
- Split broad items into smaller subtasks immediately
- Assign epics/categories for organization
- Always assign owner="agent" for your tasks

### **7. Testing Before Completion**
- ALL code must have comprehensive unit tests written and passing locally
- Rails apps: RSpec tests for models, controllers, and views
- Python: pytest tests
- No task is "complete" until tests are written, passing, and verified locally

### **8. Code Review**
- Run `rubocop` for Rails apps or `pylint` for Python apps
- Run all tests again after review
- Ensure code meets quality standards before marking complete

### **9. Code Push**
- Ensure code has been pushed to the remote repository
- Use proper commit messages
- Keep repository up to date with remote

### **10. Command Cancellation Handling**
- **First Cancellation**: Immediately retry the same command once
- **Second Cancellation**: Retry again - may be in a hung state
- **Third Cancellation**: Check if user manually executed successfully
- **Never assume**: Always verify actual state rather than assuming failure

### TODO Management System Rules

**Data Storage:**
- **Database**: PostgreSQL database `hosting_production`
- **Table**: `kanban_tasks` with relational schema
- **Location**: Same PostgreSQL server as Rails applications
- **Backup**: Included in standard PostgreSQL backup procedures
- **Migration**: Migrated from TODO.md file-based system to database (October 2025)

**API-First Interaction (REQUIRED):**
- **All kanban operations MUST use the REST API**: `/api/v1/kanban/*`
- **Authentication**: Bearer token required (JWT from login)
- **Base URL**: `https://hosting.remoteds.us/api/v1/kanban`
- **Available Endpoints**:
  - `GET /tasks` - List all tasks (supports filtering by section, priority, epic, status)
  - `GET /tasks/{task_id}` - Get specific task by ID
  - `POST /tasks` - Create new task
  - `PUT /tasks/{task_id}` - Update task fields
  - `POST /tasks/{task_id}/move` - Move to different section
  - `POST /tasks/{task_id}/priority` - Update priority
  - `POST /tasks/{task_id}/complete` - Mark completed
  - `DELETE /tasks/{task_id}` - Delete task
  - `GET /sections` - List available sections
  - `GET /stats` - Get kanban statistics by section
  - `GET /health` - Health check and database connectivity

**Kanban Board Management:**
- **Database-backed**: All tasks stored in PostgreSQL with ACID compliance
- **No Duplicates**: Tasks automatically managed by database constraints and relationships
- **Data Structure**: Each task includes:
  - `id` (integer, auto-increment primary key)
  - `content` (text, required)
  - `status` (pending/completed)
  - `priority` (high/medium/low)
  - `owner` (user/agent)
  - `section` (Backlog/To Do/In Progress/Completed)
  - `epic` (parent system/subsystem classification)
  - `area` (ui/api/docs/ops categorization)
  - `occurrence_count` (for recurring issues)
  - `created_at`, `updated_at`, `completed_at` (timestamps)
  - `position` (for drag-and-drop ordering within sections)
- **Audit Trail**: All changes logged in `kanban_task_history` table
- **Timestamps**: Automatically managed by PostgreSQL with timezone awareness

**API Usage Examples:**
```bash
# Get JWT token
curl -X POST https://hosting.remoteds.us/login \
  -d "username=admin" -d "password=YOUR_PASSWORD" -d "next=/"

# Use token for API calls
TOKEN="your_jwt_token_here"

# List all tasks
curl -H "Authorization: Bearer $TOKEN" \
  https://hosting.remoteds.us/api/v1/kanban/tasks

# Create task
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Fix bug","priority":"high","section":"To Do"}' \
  https://hosting.remoteds.us/api/v1/kanban/tasks

# Move task to In Progress
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"section":"In Progress"}' \
  https://hosting.remoteds.us/api/v1/kanban/tasks/42/move
```

**Startup Workflow (Every Conversation):**
1. Read agents.md file IN FULL and read all linked documents it references under the root docs/ folder (deployment guides, security, architecture, etc.)
2. Authenticate to kanban API (use stored credentials)
3. Fetch current tasks via `GET /api/v1/kanban/tasks`
4. Parse logs for errors/failures/404/500/auth errors
5. Create TODO items for new errors via API (check for duplicates first)
6. Increment `occurrence_count` for recurring errors
7. Work on In Progress items by priority (high → medium → low) using API
8. If user gives direct request, add to In Progress as high priority via API, work on that first.
9. If user gives a direct request but says to not work on it, add to Backlog as whatever priority they say via API.

**Error Processing:**
- Functional failures → High priority, ## To Do section
- General errors → Medium priority, ## Backlog section
- Recurring completed issues → Treat as new issue
- Track last seen timestamp in `tmp/` folder
- **Deprecation Warnings**: When running commands and seeing deprecation warnings about deprecated code/methods, create a TODO/Kanban item to track it (Medium priority, Backlog section) with the warning message and file/line number

**Completion Criteria:**
- Only mark completed when 100% working and tested
- Ask user verification for items requiring manual testing
- User can complete items directly in web interface

**Filtering System:**
- Default: Show completed items from last 7 days
- Filter options: all, last 7 days, last week, last month, last 3 months, last year
- Filter by: assigned_to, priority

**Future Web Interface:**
- Drag-and-drop between columns
- Priority lanes within each column
- Epic/subtask relationships
- Real-time updates with timestamps
6. **Validation Mindset**: Prefer automated tests and linting. Before declaring work done, outline validation steps, even if not executed due to constraints. Always create unit tests for any new code for the Rails apps, pytest for the hosting tool. Run all tests and ensure all tests pass before declaring work done and before deploying. For rails apps, also start the rails server and ensure it is running, validate all routes and methods function and the expected results are returned before declaring work done and before deploying.
7. **Cross-System Awareness**: When editing one subsystem, consider impacts on others (e.g., shared APIs, deployment scripts) and document dependencies.
8. **Security & Secrets**: Never store or expose secrets in tracked files. Confirm `.env` usage and sanitize logs and docs accordingly.
9. **QA Discipline**: Every automation action must have accompanying unit tests (Pytest for hosting tool, RSpec for Rails apps). Use QA fixtures prefixed with `qa-` (files, records, credentials) and provide cleanup scripts/tasks that remove those QA assets after test runs. The `qa-test-repo` Rails app acts as the canonical smoke-test target for deployment flows—keep it lean, well-documented, and synchronized with the kanban board.
10. **Local Dev Parity**: Maintain a full Ruby 3.3+/Rails 7.2+ toolchain locally so QA repos (qa-test-repo, cigar, tobacco) can be scaffolded, tested, and linted before remote deployment.
11. **Rebuild Readiness**: Hosting Management System workflows must support provisioning from a pristine Ubuntu host, repeated rebuilds (destroy/recreate), and restoration from remote backups when available. Always assume the remote server may be a fresh vanilla install.
12. **Dependency Hygiene**: Keep `hosting-management-system/requirements.txt` up to date. When adding/removing Python imports or new modules, update and commit `requirements.txt` in the same change. Prefer minimal dependencies.

### Changelog Conventions

- Keep the root `docs/CHANGELOG.md` updated with every notable modification across subsystems.
- Use dated releases with domain sections as applicable: UI, API, Storage, Images, Tasks, Admin, QA/Testing, Documentation, Operations, Schema, API Changes, Migration Notes, Testing Checklist, Known Limitations, Next Steps.
- Use inline code for endpoints, fields, files, and paths; call out auth/roles and compatibility notes when relevant.
- Cross-link related sections in `agents.md` and impacted subproject `README.md` files; log follow-ups in `docs/TODO.md`.

---

## 🚀 Deployment & Secrets Management

### **CRITICAL: deploy-secure-sync.py is the SOLE Secrets Deployment Method**

**Location**: `hosting-management-system/deploy-secure-sync.py - Secret Deployment Script`

**Purpose**: This script is the PRIMARY and ONLY method for deploying secrets to production. NO other script should deploy secrets.

**What It Does**:
1. **Reads secrets from `hosting_production` PostgreSQL database** on `asterra.remoteds.us`
   - Rails apps: Reads from `apps` table
   - HMS: Reads from `hms_config` table
2. **Writes secrets DIRECTLY to systemd service files** on remote server
   - Rails apps: `/etc/systemd/system/puma-{app}.service`
   - HMS: `/etc/systemd/system/hms-api.service`
3. **NO .env files created** - Secrets go directly into systemd Environment variables

**Secrets Deployed**:
- **Rails Apps**: SECRET_KEY_BASE, database_password, api_token, openrouter_api_key
- **HMS**: Admin credentials, JWT secrets, database credentials

**Security Flow**:
- Connects to `hosting_production` database via PostgreSQL connection
- Reads secrets from appropriate table (`apps` or `hms_config`)
- Connects to remote server via Fabric/SSH
- Updates systemd service files with `Environment=` lines
- **NEVER creates .env files on Linux servers**
- Reloads systemd and optionally restarts services

**Usage**:
```bash
# Deploy HMS secrets (from hms_config table)
python deploy-secure-sync.py --app hms

# Deploy Rails app secrets (from apps table)
python deploy-secure-sync.py --app cigar
python deploy-secure-sync.py --app tobacco
python deploy-secure-sync.py --app whiskey

# Skip service restart (manual restart later)
python deploy-secure-sync.py --app cigar --no-restart
```

**Deployment Workflow**:
1. Script connects to `hosting_production` database and reads secrets
2. Connects to remote server via Fabric/SSH
3. Updates systemd service files with Environment variables
4. Reloads systemd daemon
5. Restarts affected services (unless `--no-restart`)
6. **NO temporary files created, NO .env files written**
7. Verifies services are active

**Integration with manager.py**:
- ✅ `manager.py` automatically calls `deploy-secure-sync.py` during deployment
- ✅ `manager.py` creates skeleton systemd service files WITHOUT secrets
- ✅ `deploy-secure-sync.py` then injects secrets into service files
- ✅ `manager.py` never touches secrets directly
- ✅ This ensures secrets are never overwritten during code deployments

**Critical Fix (Oct 30, 2025)**:
- Created `puma.service.skeleton.tpl` template WITHOUT secrets
- Modified `_write_systemd_service()` to use skeleton template
- Added automatic `deploy-secure-sync.py` call after service file creation
- This prevents manager.py from overwriting secrets deployed by deploy-secure-sync.py

**Security Features**:
- ✅ No secrets passed on command line
- ✅ No plain-text files in Rails app directories  
- ✅ Secrets stored in systemd Environment variables only
- ✅ Secure file permissions (root-owned service files)
- ✅ All secrets read from `hosting_production` PostgreSQL database

**Verification Commands**:
```bash
# Check systemd service file has secrets
ssh root@server "grep Environment /etc/systemd/system/puma-cigar.service"

# Verify service is running
ssh root@server "systemctl status puma-cigar"

# Test API with token
curl "https://cigars.remoteds.us/api/inventory/{TOKEN}"
```

**NEVER**:
- ❌ Deploy secrets via environment variables on command line
- ❌ Create `.env` files in Rails app directories on Linux servers
- ❌ Pass secrets as CLI arguments to Rails commands
- ❌ Use any deployment method other than `deploy-secure-sync.py`
- ❌ Read secrets from .secrets.json on remote servers

---

## 📚 Required Documentation Reading

### **Before Any Development Work**
1. **[README.md](README.md)** - System overview and navigation
2. **This agents.md** - Master development rules (you are here)
3. **[docs/README.md](docs/README.md)** - Complete documentation index
4. **Application-specific deployment guide**:
   - [CIGAR_DEPLOYMENT_GUIDE.md](docs/deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md) for cigar app work
   - [TOBACCO_DEPLOYMENT_GUIDE.md](docs/deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md) for tobacco app work
   - [HOSTING_DEPLOYMENT_GUIDE.md](docs/deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md) for hosting system work

### **Documentation Hierarchy**
```
agents.md (GOLDEN RULES)
├── README.md (System Overview)
├── docs/README.md (Documentation Master Index)
├── docs/deployment-guides/ (Deployment procedures)
├── docs/application-design-documents/ (App designs)
├── docs/architecture-security/ (Architecture & security)
├── docs/reference/ (Change tracking, dev guides)
└── Individual repository README.md files
```

### **For Security Procedures**
- **[SECURITY_GUIDE.md](docs/architecture-security/SECURITY_GUIDE.md)** - Complete security protocols
- **[SSL_SETUP.md](docs/architecture-security/SSL_SETUP.md)** - SSL certificate management
- **[DEPLOYMENT_PRACTICES.md](docs/architecture-security/DEPLOYMENT_PRACTICES.md)** - Secure deployment methods

### **For Architecture Details**
- **[ARCHITECTURE_PLAN.md](docs/architecture-security/ARCHITECTURE_PLAN.md)** - Detailed technical specifications
- **[COMPLETE_DEPLOYMENT_GUIDE.md](docs/deployment-guides/COMPLETE_DEPLOYMENT_GUIDE.md)** - Comprehensive deployment procedures

---

## 🔒 Security Protocols

### **CRITICAL SECURITY RULES**
1. **❌ NEVER copy .secrets.json to any remote server**
2. **❌ NEVER commit secrets to version control**
3. **❌ NEVER use hardcoded credentials in code**
4. **✅ ALWAYS use environment variables for production in systemd service files**
5. **✅ ALWAYS verify file permissions (600)**
6. **✅ ALWAYS use www-data:www-data ownership**

### **Secrets Management**
- **Location**: hosting_production database on asterra.remoteds.us in postgresql
- **Purpose**: Central credential storage
- **Usage**: Reference for environment variable generation
- **Security**: Global workspace root, not in any app repo

### **Environment Variables**
- **Remote Server (Linux)**: NO .env files - secrets in systemd service files only
- **Local Mac (Darwin)**: .env files allowed with 600 permissions for development
- All sensitive data loaded from environment, not code
- **Detailed procedures**: [SECURITY_GUIDE.md](docs/architecture-security/SECURITY_GUIDE.md)

### **SSL/HTTPS Management**
- **Required**: Let's Encrypt certificates via certbot
- **Automated**: Certificate issuance/renewal in deployment scripts
- **No self-signed certs**: Use only trusted certificates
- **Detailed setup**: [SSL_SETUP.md](docs/architecture-security/SSL_SETUP.md)

### **SSH and Access Control**
- SSH key authentication only (no passwords)
- SSH keys stored in `hosting_production` database or local .secrets.json (Mac only)
- **Deployment**: SSH keys deployed to remote servers during provisioning
- **Ownership**: All web content runs as www-data:www-data

---

### Key Principles for AI Implementation

* **Modularity** : Each system is in its own private GitHub repository (e.g., cigar-management-system, tobacco-management-system, hosting-management-system). **WORKSPACE STRUCTURE**: The root workspace directory is a consolidated git repository (management-systems) that contains documentation, configuration, and references to individual application repositories.
* **Tech Stack** :
  * Rails Apps: Ruby 3.3+, Rails 7.2.2, Postgres DB, Puma (app server), Nginx (reverse proxy).
  * Local Management Tool: Python 3.12+, CLI-based (manager.py), Fabric/Paramiko for SSH automation, JSON for config/datastore.
  * Remote Management Interface: Rails/Sinatra web app at hosting.remoteds.us with secure authentication, API endpoints, log viewing, app control.
* **Development Workflow (CRITICAL)** :
  * ALL Rails development happens locally on the developer's laptop.
  * Local environment MUST match production: same Ruby version, same Rails version (7.2.2), same gem versions.
  * Full RSpec unit tests MUST pass before ANY code is pushed to production.
  * Website MUST load and function correctly locally before production deployment.
  * NO production deployments without: (1) passing tests, (2) local verification.
  * Git push to repository, THEN deploy to production via management tool.
* **Security** : Use SSH keys for remote access (no passwords). Store secrets in `hosting_production` PostgreSQL database (remote server) or .secrets.json (local Mac only, not committed to Git). Use HTTPS via Let's Encrypt, and ensure provisioning automates certificate issuance/renewal as part of deployments.
* **Testing** : Include RSpec (for Rails) and Pytest (for Python) specs for all CRUD operations, API endpoints, and automation tasks.
* **Version Control** : Main branch for production-ready code. Use semantic versioning (e.g., v1.0.0 tags). **Workspace Repository**: The root management-systems repository tracks consolidated documentation and configuration, while individual application repositories track their respective codebases.
* **Documentation in Code** : Use inline comments, README.md per repo, and YARD/RDoc for Ruby, Sphinx/Pydoc for Python.
* **AI Workflow** : Agents should generate code iteratively: Start with scaffolds, add features, test, refine. Use tools like code_execution for validation.
* **Dependencies** : Minimize external gems/packages. For Rails: Add tesseract-ffi, rmagick, fuzzy-string-match for OCR. For Python: fabric, paramiko, click, python-dotenv, keyring, rsync (via subprocess).
* **Infrastructure as Code** : ALL provisioning and deployment steps MUST be scripted and repeatable. Manual steps are NOT allowed. Every deployment must follow the exact same automated process.

## Overall System Architecture

### Management System Design

The hosting management system operates on TWO interfaces:

**1. Local Management Interface (Developer Laptop)**
* **Tool**: Python CLI (`manager.py`) with Click framework
* **Purpose**: Primary deployment and management tool
* **Operations**: Provision servers, deploy apps, manage configs, trigger backups/restores
* **No Web Server**: CLI-only, no Flask/web server running locally
* **Authentication**: Uses SSH keys and .secrets.json for remote operations

**2. Remote Management Interface (hosting.remoteds.us)**
* **Tool**: FastAPI web application deployed on the remote host
* **Purpose**: Monitoring, control, and visibility interface
* **Features**:
  * **Authentication**: Secure login/password (stored in .secrets.json), JWT tokens for API
  * **Dashboard**: Real-time status of all Rails apps, quick start/stop/restart actions
  * **Log Viewing**: View app logs (journalctl), Nginx access/error logs, search and filter
  * **Config Management**: View/edit Nginx configs, test before applying, backup/restore
  * **Script Execution**: Run troubleshooting scripts from web UI, view output in real-time
  * **Deployment**: Trigger redeployments of Rails apps, self-update capability
  * **API Endpoints**: Full REST API for programmatic access from local CLI
* **Safety**: Redeployments NEVER erase production data unless explicitly instructed
* **Deployment**: Bootstrap deployment via manager.py, then can self-update via web UI

**3. Remote CLI Tools**
* **Location**: Installed on remote host during provisioning
* **Purpose**: Direct server troubleshooting and management
* **Tools**:
  * Log parsing scripts (find errors, analyze patterns)
  * Service management shortcuts
  * Database query utilities
  * Quick restart/reload helpers

### Infrastructure Architecture

* **Remote Host** : Vanilla Ubuntu 25.04 LTS (x64) on Digital Ocean. The Hosting Management System must be capable of provisioning this host end-to-end every time it is rebuilt from scratch. Hosts Rails apps at /var/www/cigar and /var/www/tobacco. FastAPI management interface at /opt/hosting-api/. Nginx handles subdomains via virtual hosts. Puma runs Rails apps on Unix sockets. All web content runs as www-data user with proper ownership.
* **Domain Mapping** :
  * cigars.remoteds.us → Cigar Management Rails app (Puma)
  * tobacco.remoteds.us → Tobacco Management Rails app (Puma)
  * hosting.remoteds.us → FastAPI Management Interface (uvicorn)
* **Data Preservation** : All deployment operations preserve production databases and user-uploaded files unless explicitly told to reset/restore.
* **Backups** : DB dumps + file rsync to remote dir, then sync to local. Restores rebuild from backups.
* **Home Assistant Integration** : Rails apps expose /api/inventory JSON endpoint (format: {"cigars":{"LargeHumidor":[{"cigar_name":"Undercrown","brand":"Drew Estate","rating":5,"qty":6}],...}} for Cigar; similar for Tobacco).

## 1. Cigar Management System (Ruby on Rails App)

**Overview:** Web-based inventory tracker for cigars across multiple humidors with OCR support, capacity tracking, and JSON API for Home Assistant integration.

**Complete Documentation:** See **[docs/application-design-documents/cigar-management-system.md](docs/application-design-documents/cigar-management-system.md)** for full application design including:
- Database schema and domain model
- Business logic and OCR integration
- API endpoints and JSON format
- Controllers, views, and testing
- Deployment configuration

**Key Features:**
- CRUD operations for cigars, humidors, brands, and locations
- Photo scanning with Tesseract OCR for cigar band recognition
- Capacity tracking across multiple humidors
- Public JSON API: `GET /api/inventory/:token`
- Bootstrap UI with responsive design

**Technology:** Rails 7.2.2, PostgreSQL, Puma, Nginx, Tesseract OCR  
**Deployment:** Via `manager.py deploy --app cigar`  
**Production:** https://cigars.remoteds.us (Port 3001)

---

## 2. Tobacco Management System (Ruby on Rails App)

**Overview:** Web-based inventory tracker for tobacco products and storage management with weight-based tracking and JSON API for Home Assistant integration.

**Complete Documentation:** See **[docs/application-design-documents/tobacco-management-system.md](docs/application-design-documents/tobacco-management-system.md)** for full application design including:
- Database schema and domain model
- Weight-based tracking system
- Tobacco type classification
- API endpoints and JSON format
- Deployment configuration

**Key Features:**
- CRUD operations for tobacco products and storage units
- Weight-based tracking in ounces (decimal precision)
- Tobacco type classification (Loose Leaf, Flake, Plug, etc.)
- Public JSON API: `GET /api/inventory/:token`
- Bootstrap UI with green color scheme

**Key Differences from Cigar App:**
- Weight-based tracking (ounces) instead of quantity
- Simpler two-level hierarchy (Storage → Tobacco)
- No OCR integration (manual entry only)
- Type classification instead of ratings

**Technology:** Rails 7.2.2, PostgreSQL, Puma, Nginx  
**Deployment:** Via `manager.py deploy --app tobacco`  
**Production:** https://tobacco.remoteds.us (Port 3002)

---

## 3. Whiskey Management System (Ruby on Rails App)

**Overview:** Web-based collection tracker for whiskey bottles with detailed specifications, brand management, and comprehensive type taxonomy.

**Complete Documentation:** See **[docs/application-design-documents/whiskey-management-system.md](docs/application-design-documents/whiskey-management-system.md)** for full application design including:
- Database schema and domain model
- Whiskey type taxonomy and classification
- Brand and location management
- Technology stack and dependencies
- Deployment configuration

**Key Features:**
- CRUD operations for whiskeys, brands, types, and locations
- Detailed bottle specifications (ABV, proof, age, mash bill)
- Comprehensive whiskey type taxonomy
- Image storage for bottle reference
- Bootstrap UI with amber/gold color scheme

**Technology:** Rails 7.2.2, PostgreSQL (production), SQLite3 (dev/test), Puma, Nginx  
**Deployment:** Via `manager.py deploy --app whiskey`  
**Production:** https://whiskey.remoteds.us (Port 3003)

---

## 4. Hosting Management System (Python FastAPI + CLI)

**Overview:** Two-part system for deploying, monitoring, and managing all Rails applications. Consists of a local CLI tool (manager.py) and remote web interface (FastAPI).

**Complete Documentation:** See deployment and architecture documentation:
- **[docs/deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md](docs/deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md)** - Deployment procedures
- **[docs/architecture-security/ARCHITECTURE_PLAN.md](docs/architecture-security/ARCHITECTURE_PLAN.md)** - System architecture
- **[docs/architecture-security/SECURITY_GUIDE.md](docs/architecture-security/SECURITY_GUIDE.md)** - Security protocols

**Key Components:**

**A. Local CLI Tool (manager.py)**
* **Location**: Developer's laptop
* **Purpose**: Primary deployment and automation engine
* **Technology**: Python 3.12+ with Fabric/Paramiko, Click CLI framework
* **Config Storage**: Database-first architecture (hosting_production PostgreSQL)
* **Commands**: Deploy apps, manage services, view logs, handle secrets

**B. Remote Web Interface (FastAPI)**
* **Location**: hosting.remoteds.us on remote server (`/opt/hosting-api/`)
* **Purpose**: Monitoring, control, and dashboard
* **Technology**: FastAPI with Jinja2 templates, JWT authentication, REST API
* **Storage**: SQLite for task management, PostgreSQL for configuration
* **Features**: Service control, log viewing, Kanban task management

### Infrastructure as Code Requirements

**CRITICAL**: ALL server provisioning and deployment MUST be:
* Fully automated via scripts (manager.py)
* Repeatable (destroy and rebuild must produce identical results)
* Documented in deployment logs (see Deployment Log section below)
* Idempotent (safe to run multiple times)
* Version controlled (in hosting-management-system repository)

This tool must be soup-to-nuts configuration management: starting from a pristine Ubuntu 25.04 server, install all core dependencies (Ruby 3.3+, Rails 7.2.2, Bundler, Node.js, npm, Postgres, Nginx, systemd services), deploy ALL Rails apps (including the management interface itself), and orchestrate cleanup or restoration from backups. Expect frequent host destruction/recreation as part of QA; automation must therefore be idempotent and fully remote-driven.

### Repository Setup

* Private GitHub repo: hosting-management-system.
* **Local CLI Tool Structure**:

```
hosting-management-system/
├── manager.py              # LOCAL: CLI client (runs on laptop)
├── web/                    # REMOTE: Web interface (deployed to /opt/hosting-api/)
│   ├── app.py             # FastAPI application
│   ├── routes/            # Web routes + API endpoints
│   ├── services/          # Business logic (deploy, logs, configs)
│   ├── templates/         # Jinja2 HTML templates
│   └── static/            # CSS, JS, images
├── config.json             # Local development config reference (gitignored)
├── .secrets.json          # LOCAL MAC ONLY - Dev reference (gitignored, NOT deployed)
├── deployment_key         # Private SSH key for Git (gitignored)
├── deployment_key.pub     # Public SSH key for Git (gitignored)
├── templates/             # Nginx, Puma, systemd templates
│   ├── nginx-ssl.conf.tpl
│   ├── puma.rb.tpl
│   ├── puma.service.tpl
│   └── hosting-api.service.tpl
├── remote_cli_tools/      # Scripts to install on remote host
│   ├── parse_logs.sh
│   ├── check_status.sh
│   └── restart_service.sh
├── tests/                 # Pytest test suite
├── docs/                  # Documentation folder with guides
├── README.md
└── requirements.txt
```

* **Remote Web Interface**: FastAPI application in `web/` directory
  * Deployed to /opt/hosting-api/ on remote server
  * Accessible at hosting.remoteds.us
  * Password-protected with JWT authentication
  * Full web UI + REST API for all management operations
  * Bootstrap deployment via manager.py, then self-updating

### Core Components (Local CLI Tool)

* **Config Files (Mac localhost only)**:
  * `config.json`: Local development reference for hosts, repos, domains (gitignored)
  * `.secrets.json`: LOCAL MAC ONLY - Development reference for secrets (gitignored, NEVER deployed to server)
  * `deployment_key` / `.pub`: SSH keypair for Git operations on remote host (gitignored)
  
* **Production Config Source**:
  * **hosting_production PostgreSQL database** - ONLY source of truth for production
  * All scripts read from database when deploying to remote server
  * Local config files used only for Mac localhost development

* **Fabric Tasks** (in manager.py):
  * `provision_server`: Install ALL system dependencies, setup www-data user, deploy SSH keys, install remote CLI tools
  * `deploy_hosting_api`: Bootstrap deployment of hosting management web interface (first-time only)
  * `deploy_app(app_name)`: Clone/pull Git, bundle install, npm install, db:migrate, assets:precompile, configure Nginx/Puma, restart services
  * `start_app/stop_app/restart_app(app_name)`: Manage Puma systemd services
  * `backup(app_name)`: pg_dump + rsync files to remote backup dir, then local sync
  * `restore(app_name, backup_path)`: Upload backup, restore DB/files, redeploy WITHOUT data loss
  * `full_deploy`: Provision server + deploy ALL apps (Rails apps + hosting API)
  * `update_hosting_api`: Update hosting API via its own API endpoint (calls POST /api/hosting/deploy)
  * `view_logs(app_name)`: Stream journalctl logs from remote
  * `check_status`: Query all app statuses via systemctl or API

* **CLI Interface**: Click framework (e.g., `python manager.py provision`, `python manager.py deploy --app cigar`)

* **Data Preservation**: All deployment operations preserve production databases and uploaded files unless explicitly using `--reset-data` flag

* **Testing**: Pytest for all Fabric tasks using mocked connections

### SSH Key Deployment & User Permissions

* **SSH Keys**: The system includes `deployment_key` (private) and `deployment_key.pub` (public) files that must be deployed to the remote server.
* **Key Installation**: During provisioning, these keys are installed in `/root/.ssh/` with proper permissions (600 for private key, 644 for public key).
* **Git Operations**: The deployed SSH keys enable the remote server to perform `git pull` operations from private GitHub repositories without password prompts.
* **User Ownership**: All web content in `/var/www/` must be owned by `www-data:www-data` user and group.
* **Directory Permissions**: Ensure proper permissions for deployment directories (755 for directories, 644 for files) to allow www-data to read/write execute as needed.

### Deployment Log and Documentation

**CRITICAL**: A master `DEPLOYMENT_LOG.md` file MUST exist in the root of the hosting-management-system repository.

**Purpose**: This log documents EVERY step taken to deploy a server from bare metal to production-ready state.

**Requirements**:
* Record every command executed during server provisioning
* Document every configuration file created/modified
* Note all package installations with versions
* Track SSH key deployment steps
* Record SSL certificate generation steps
* Log service startup and verification steps
* Include timestamps and outcome verification
* Must be detailed enough to manually reproduce the entire deployment

**Usage**:
* Update the log during EVERY deployment
* Use the log to verify repeatability
* Reference the log when troubleshooting
* Compare log entries when testing destroy/rebuild cycles

**Format**: Markdown with chronological sections, code blocks for commands, verification checkpoints

### Runtime & Service Management

- **Local Tool**: Python CLI (`manager.py`) runs on developer's laptop, no web server
- **Remote Services**: All Rails apps run as Puma systemd services under www-data user
  * `cigar.service` → Cigar Management Rails app
  * `tobacco.service` → Tobacco Management Rails app
  * `hosting.service` → Remote Management Web Interface (TBD)
- **Service Management**: Fabric tasks manage remote services via SSH
- **Logging**: 
  * Remote: systemd/journalctl logs, application logs in `/var/www/*/shared/log/`
  * Local: Console output, optional file logging for automation runs
- **Remote CLI Tools**: Bash scripts installed in `/usr/local/bin/` during provisioning for quick troubleshooting

### Near-term Requirements

**Phase 1: Core Infrastructure (CURRENT PRIORITY)**
- Create `DEPLOYMENT_LOG.md` in hosting-management-system repository
- Ensure `deployment_key` and `deployment_key.pub` exist and are properly configured
- Create `remote_cli_tools/` directory with log parsing and service management scripts
- Update `manager.py` to install remote CLI tools during provisioning
- Add `view_logs` and `check_status` commands to manager.py CLI
- Full provision + deploy cycle test (destroy/rebuild verification)

**Phase 2: Local Development Environment**
- Install/verify Ruby 3.3+ and Rails 7.2.2 locally to match production
- Document local Rails setup in hosting-management-system README
- Create test checklist: unit tests → local verification → production deploy
- Add pre-push hooks to enforce testing requirements

**Phase 3: Remote Management Web Interface (TBD)**
- Design Rails 7.2.2 application for hosting.remoteds.us
- Authentication system (secure login/password)
- Dashboard views: app status, logs, configurations
- API endpoints for programmatic access
- App control actions: start/stop/restart, trigger deployments
- Backup management interface

**Phase 4: QA and Testing**
- Pytest coverage for ALL Fabric tasks in manager.py
- Mock connection tests for deployment operations
- qa-test-repo: vanilla Rails app for deployment smoke tests
- Automated test suite for full deployment cycle
- Data preservation verification tests

## Deployment and Operations Guide for AI Agents

* **Initial Setup** : Clone repos locally. Run Hosting tool to provision remote, deploy apps.
* **Updates** : Push to Git, use deploy_app to pull/bundle/migrate.
* **Backups/Restores** : Daily cron for backup; test restores on staging.
* **Monitoring** : Add basic logging; suggest New Relic integration later.
* **Edge Cases** : Handle failed deploys (rollback), low disk space, DB conflicts.

This document is self-contained for AI implementation. Generate code per section, validate with tools, iterate.

## 📚 **Authoritative Documentation - Required Reading**

**🔴 CRITICAL RULE**: All AI agents MUST read and understand these documentation guides before making any changes to the system. These documents contain the authoritative procedures and security protocols.

### **📖 Core Documentation (Must Read)**
1. **[ARCHITECTURE_PLAN.md](docs/architecture-security/ARCHITECTURE_PLAN.md)** - Complete system architecture and technical specifications
2. **[SECURITY_GUIDE.md](docs/architecture-security/SECURITY_GUIDE.md)** - Security protocols, secret management, and compliance requirements  
3. **[SSL_SETUP.md](docs/architecture-security/SSL_SETUP.md)** - Let's Encrypt SSL certificate management with certbot
4. **[DEPLOYMENT_PRACTICES.md](docs/architecture-security/DEPLOYMENT_PRACTICES.md)** - Security protocols and deployment methods
5. **[COMPLETE_DEPLOYMENT_GUIDE.md](docs/deployment-guides/COMPLETE_DEPLOYMENT_GUIDE.md)** - Comprehensive guide for all applications

### **📋 Reference Documentation**
6. **[CHANGELOG.md](docs/reference/CHANGELOG.md)** - System change tracking
7. **[IMPLEMENTATION_PLAN.md](docs/reference/IMPLEMENTATION_PLAN.md)** - Implementation details
8. **[IMPLEMENTATION_SUMMARY.md](docs/reference/IMPLEMENTATION_SUMMARY.md)** - Implementation summary

---

## 🎯 **AI Agent Documentation Requirements**

### **📖 Before Starting Any Work**
1. **READ [ARCHITECTURE_PLAN.md](docs/architecture-security/ARCHITECTURE_PLAN.md)** - Understand system architecture and component relationships
2. **READ [SECURITY_GUIDE.md](docs/architecture-security/SECURITY_GUIDE.md)** - Follow all security protocols without exception
3. **READ [DEPLOYMENT_PRACTICES.md](docs/architecture-security/DEPLOYMENT_PRACTICES.md)** - Use correct deployment methods for each application
4. **READ [COMPLETE_DEPLOYMENT_GUIDE.md](docs/deployment-guides/COMPLETE_DEPLOYMENT_GUIDE.md)** - Use application-specific deployment commands

### **🔍 For SSL/HTTPS Work**
- **READ SSL_SETUP.md** - Use Let's Encrypt/certbot, NOT self-signed certificates
- Follow automated SSL setup procedures
- Verify certificate auto-renewal is configured

### **For Deployment Work**
- **ALWAYS read deployment guides** before deploying any application:
  - [HOSTING_DEPLOYMENT_GUIDE.md](docs/deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md) for hosting app
  - [CIGAR_DEPLOYMENT_GUIDE.md](docs/deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md) for cigar app
  - [TOBACCO_DEPLOYMENT_GUIDE.md](docs/deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md) for tobacco app
  - [COMPLETE_DEPLOYMENT_GUIDE.md](docs/deployment-guides/COMPLETE_DEPLOYMENT_GUIDE.md) for all apps
- Use the correct deployment method from the guides - **DO NOT create ad-hoc procedures**
- **NEVER copy .secrets.json to remote servers** - Database is source of truth
- **Remote Server (Linux)**: NO .env files - secrets in systemd only
- **Local Mac (Darwin)**: .env files allowed with 600 permissions

### **Deployment Troubleshooting Rules**
- **If deployment breaks**: Do NOT reinvent the wheel
- **Diagnose first**: Figure out what broke (package version, missing dependency, config error, etc.)
- **Fix the root cause**: Update/fix the code that broke
- **If new code throws errors**: Debug why it's failing and fix it
- **Push to repo**: Commit and push the fix
- **Try deploy again**: Use the same deployment method from the guide
- **If deployment method is fundamentally broken**: Update the method AND update the guide to match
- **Document changes**: Update HOSTING_DEPLOYMENT_GUIDE.md if procedures change

### **🔒 Security Compliance Checklist**
- [ ] Read SECURITY_GUIDE.md and understand all protocols
- [ ] Never commit secrets to git repositories
- [ ] Use environment variables for all sensitive data
- [ ] Verify file permissions on .env files (600, www-data:www-data)
- [ ] Always read HOSTING_DEPLOYMENT_GUIDE.md before deploying the hosting app

---

## 📞 **Documentation Maintenance**

### **Keeping Documents Current**
- Update CHANGELOG_TODO_IMPLEMENTATION.md when making implementation changes
- Update DEPLOYMENT_PRACTICES.md when deployment procedures change
- Update PROJECT_COMPLETION_REPORT.md when major milestones are reached
- Update SSL_SETUP.md when SSL procedures change

### **Cross-Reference Requirements**
- agents.md must link to all authoritative documents
- CHANGELOG.md files must reference agents.md and relevant documentation
- README.md files must link to relevant sections in agents.md

### **Document Authority**
- **ARCHITECTURE_PLAN.md** = Authoritative system architecture
- **SECURITY_GUIDE.md** = Authoritative security protocols  
- **DEPLOYMENT_PRACTICES.md** = Authoritative deployment methods
- **COMPLETE_DEPLOYMENT_GUIDE.md** = Authoritative application-specific procedures
- **SSL_SETUP.md** = Authoritative SSL certificate management

**IF THERE ARE CONFLICTS between documents, the ARCHITECTURE_PLAN.md and SECURITY_GUIDE.md take precedence.**

---

## 🔗 Quick Reference Links

### **📋 Essential Documents**
- **[System Overview](README.md)** - High-level system introduction
- **[Cigar App Deployment](docs/CIGAR_DEPLOYMENT_GUIDE.md)** - Cigar application procedures
- **[Tobacco App Deployment](docs/TOBACCO_DEPLOYMENT_GUIDE.md)** - Tobacco application procedures  
- **[Hosting System Deployment](docs/HOSTING_DEPLOYMENT_GUIDE.md)** - Hosting management procedures
- **[Change Log](docs/CHANGELOG.md)** - System change tracking
- **[TODO System](docs/TODO.md)** - Task tracking interface

### **🔧 Development Resources**
- **[Security Guide](docs/SECURITY_GUIDE.md)** - Complete security protocols
- **[SSL Setup](docs/SSL_SETUP.md)** - Certificate management
- **[Architecture Plan](docs/ARCHITECTURE_PLAN.md)** - Technical specifications
- **[Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md)** - Pre-deployment verification

### **🚀 Quick Start**
1. **Read this agents.md** - Master rules and protocols
2. **Choose your application** - Follow deployment guide
3. **Set up local environment** - Match production requirements
4. **Run tests** - Ensure all tests pass
5. **Deploy via hosting system** - Use management tools

---

**This workspace follows the development rules outlined in this agents.md document. All team members must read and understand these protocols before making any changes.**
