# Agents.md: Master Development Rules & System Architecture

**Status**: ✅ **GOLDEN RULES DOCUMENT** - Must be read before any development work  
**Last Updated**: October 29, 2025  
**Version**: 3.0

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
├── config.json                       # Public configuration
├── .secrets.json                     # Private credentials (gitignored)
├── docs/                             # Consolidated documentation
│   ├── CIGAR_DEPLOYMENT_GUIDE.md     # Cigar app procedures
│   ├── TOBACCO_DEPLOYMENT_GUIDE.md   # Tobacco app procedures
│   ├── HOSTING_DEPLOYMENT_GUIDE.md   # Hosting system procedures
│   ├── CHANGELOG.md                  # Change tracking
│   ├── TODO.md                       # Task tracking
│   └── [Additional documentation]    # Reference materials
├── cigar-management-system/          # Individual app repository
├── tobacco-management-system/        # Individual app repository
├── hosting-management-system/        # Individual app repository
└── qa-test-repo/                     # Testing repository
```

---

## 🎯 Core Development Rules

### **1. Question Ambiguity**
- Treat every unclear requirement as a topic for clarification
- Surface questions early to confirm assumptions before coding
- Never make assumptions about user requirements

### **2. Documentation First**
- Every folder across all repositories must contain a README.md
- Include purpose, architecture relationships, entry points, and usage patterns
- Include at least one relevant Mermaid diagram (flowchart, sequence, or class)

### **3. Code Commentary Discipline**
- Provide concise, high-value inline comments for complex logic only
- Default to self-documenting code
- Ensure docstrings/YARD/Sphinx annotations stay current

### **4. Change Tracking**
- Update `docs/CHANGELOG.md` alongside any notable modification
- Log date, author (AI agent), and summary
- Use domain-based sections (UI, API, storage, images, tasks, QA, docs, ops)

### **5. Task Hygiene**
- Use the TODO system in the hosting management interface
- Move cards between states: Backlog → To Do → In Progress → Completed
- Capture priorities (High/Med/Low) per card
- Split broad items into smaller subtasks immediately

### **6. Testing Before Completion**
- ALL code must have comprehensive unit tests written and passing locally
- Rails apps: RSpec tests for models, controllers, and views
- Python: pytest tests
- No task is "complete" until tests are written, passing, and verified locally

### **7. Code Review**
- Run `rubocop` for Rails apps or `pylint` for Python apps
- Run all tests again after review
- Ensure code meets quality standards before marking complete

### **8. Code Push**
- Ensure code has been pushed to the remote repository
- Use proper commit messages
- Keep repository up to date with remote

### **9. Command Cancellation Handling**
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

## 📚 Required Documentation Reading

### **Before Any Development Work**
1. **[README.md](README.md)** - System overview and navigation
2. **This agents.md** - Master development rules (you are here)
3. **Application-specific deployment guide**:
   - [CIGAR_DEPLOYMENT_GUIDE.md](docs/CIGAR_DEPLOYMENT_GUIDE.md) for cigar app work
   - [TOBACCO_DEPLOYMENT_GUIDE.md](docs/TOBACCO_DEPLOYMENT_GUIDE.md) for tobacco app work
   - [HOSTING_DEPLOYMENT_GUIDE.md](docs/HOSTING_DEPLOYMENT_GUIDE.md) for hosting system work

### **Documentation Hierarchy**
```
agents.md (GOLDEN RULES)
├── README.md (System Overview)
├── docs/DEPLOYMENT_GUIDES.md (Application-specific)
├── docs/CHANGELOG.md (Change tracking)
└── Individual repository README.md files
```

### **For Security Procedures**
- **[SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md)** - Complete security protocols
- **[SSL_SETUP.md](docs/SSL_SETUP.md)** - SSL certificate management

### **For Architecture Details**
- **[ARCHITECTURE_PLAN.md](docs/ARCHITECTURE_PLAN.md)** - Detailed technical specifications
- **[COMPLETE_DEPLOYMENT_GUIDE.md](docs/COMPLETE_DEPLOYMENT_GUIDE.md)** - Comprehensive deployment procedures

---

## 🔒 Security Protocols

### **CRITICAL SECURITY RULES**
1. **❌ NEVER copy .secrets.json to any remote server**
2. **❌ NEVER commit secrets to version control**
3. **❌ NEVER use hardcoded credentials in code**
4. **✅ ALWAYS use environment variables for production**
5. **✅ ALWAYS verify file permissions (600)**
6. **✅ ALWAYS use www-data:www-data ownership**

### **Secrets Management**
- **Location**: `/Users/bpauley/Projects/mangement-systems/.secrets.json`
- **Purpose**: Central credential storage (NEVER committed)
- **Usage**: Reference for environment variable generation
- **Security**: Global workspace root, not in any app repo

### **Environment Variables**
- Production uses `.env` files with 600 permissions
- All sensitive data loaded from environment, not code
- **Detailed procedures**: [SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md)

### **SSL/HTTPS Management**
- **Required**: Let's Encrypt certificates via certbot
- **Automated**: Certificate issuance/renewal in deployment scripts
- **No self-signed certs**: Use only trusted certificates
- **Detailed setup**: [SSL_SETUP.md](docs/SSL_SETUP.md)

### **SSH and Access Control**
- SSH key authentication only (no passwords)
- Keys stored in `.secrets.json` (gitignored)
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
* **Security** : Use SSH keys for remote access (no passwords). Store secrets in .secrets.json (not committed to Git). Use HTTPS via Let's Encrypt or approved self-signed certificates (free options only), and ensure provisioning automates certificate issuance/renewal as part of deployments.
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

This is a web-based inventory tracker for cigars across multiple humidors. Features: CRUD for cigars/humidors/inventories, photo scanning with local OCR for add/remove, aggregation dashboards, capacity tracking, JSON API.

### Detailed Domain Model

#### Core Relationships
- **Location** has_many :humidors
- **Humidor** has_many :cigars, has_many :brands, through: :cigars
- **Cigar** belongs_to :brand, belongs_to :humidor
- **Brand** has_many :cigars

#### Model Specifications

**Location Model:**
- Attributes: name (string), address (string), city (string), state (string), zip (string), country (string)
- Associations: has_many :humidors, dependent: :destroy
- Validations: presence of name, uniqueness of name within scope

**Humidor Model:**
- Attributes: name (string), location_id (foreign key), max_qty (integer), image (attachment)
- Associations: belongs_to :location, has_many :humidor_cigars, has_many :cigars, through: :humidor_cigars
- Validations: presence of name, location_id; numericality of max_qty > 0
- Methods: available_capacity, used_capacity, capacity_percentage

**Brand Model:**
- Attributes: name (string), website_url (string)
- Associations: has_many :cigars, dependent: :restrict_with_error
- Validations: presence of name, uniqueness of name; valid URL format for website_url

**Cigar Model:**
- Attributes: cigar_name (string), brand_id (foreign key), rating (integer, 1-5), cigar_image (attachment for OCR)
- Associations: belongs_to :brand, has_many :humidor_cigars, has_many :humidors, through: :humidor_cigars
- Validations: presence of cigar_name, brand_id; inclusion of rating in 1..5

**HumidorCigar Join Model (for quantity tracking):**
- Attributes: humidor_id (foreign key), cigar_id (foreign key), quantity (integer, default 0)
- Associations: belongs_to :humidor, belongs_to :cigar
- Validations: presence of humidor_id, cigar_id; numericality of quantity >= 0
- Callbacks: after_update :destroy_if_zero_quantity
- Methods: transfer_quantity(to_humidor, amount), add_quantity(amount), remove_quantity(amount)

#### Key Business Logic

**Quantity Management:**
- Use `has_many :through` with `HumidorCigar` join table to track quantities
- Avoid duplicate cigar records - track quantity on relationship
- When quantity reaches 0, automatically delete the `HumidorCigar` record
- Support bulk adding (box purchase) and individual tracking

**OCR Integration:**
- `cigar_image` stored for OCR processing
- Tesseract OCR to extract cigar_name and brand from cigar bands
- Fuzzy string matching to identify existing cigars/brands
- Manual fallback for unrecognized cigars

**Capacity Management:**
- `max_qty` on humidor prevents overfilling
- Real-time capacity tracking across all humidors
- Visual indicators for capacity status

### Public JSON API Endpoint for Cigar Rails App.

**Dynamic Link Requirements:**
- Read-only public exposure of inventory data exposed with some sort of random token that doesn't change. This is to keep the url from being guessed, but allowing for easy access to the data for homeassistant to pull the inventory data.
- Format matches existing Google Sheets output. It needs to have the humidor name, cigar name, brand name, rating, and quantity. Need all of the humidors and their cigars returned in the json output.:
```json
{
  "cigars": {
    "LargeHumidor": [
      {
        "cigar_name": "Undercrown",
        "brand": "Drew Estate", 
        "rating": 5,
        "qty": 6
      }
    ],
    "SmallHumidor": [
      {
        "cigar_name": "Coro #5",
        "brand": "Test",
        "rating": 4,
        "qty": 6
      }
    ]
  }
}
```

**Endpoint:** `GET /api/inventory/:token`
**Security:** UUID token with expiration, rotation capability

### Repository Setup

* Private GitHub repo: cigar-management-system.
* Structure:

```
├── app
│   ├── controllers
│   ├── models
│   ├── views
│   ├── assets
│   └── ...
├── config
│   ├── routes.rb
│   ├── unicorn.rb
│   └── ...
├── db
│   ├── migrate
│   └── seeds.rb
├── lib
│   └── tasks (e.g., import_from_sheets.rake)
├── spec
├── Gemfile
├── README.md
└── .env.example
```

### Models (ActiveRecord)

* **Humidor** : Represents a storage unit.
* Attributes: name (string, unique), capacity (integer, default 0), timestamps.
* Associations: has_many :inventories, has_many :cigars, through: :inventories.
* Validations: validates :name, presence: true, uniqueness: true; validates :capacity, numericality: { greater_than_or_equal_to: 0 }.
* Methods:
  * available_slots: capacity - inventories.sum(:qty).
  * used_slots: inventories.sum(:qty).
* **Cigar** : Represents a cigar type.
* Attributes: name (string), brand (string), rating (integer, 1-5), timestamps.
* Associations: has_many :inventories, has_many :humidors, through: :inventories.
* Validations: validates :name, :brand, presence: true; validates :rating, inclusion: { in: 1..5 }, allow_nil: true.
* Methods:
  * total_qty: inventories.sum(:qty).
  * locations: inventories.map { |inv| { humidor: inv.humidor.name, qty: inv.qty } }.
  * Class method totals: joins(:inventories).group(:id).sum("inventories.qty").
* **Inventory** : Joins cigars to humidors with quantity.
* Attributes: qty (integer, default 0), timestamps.
* Associations: belongs_to :humidor, belongs_to :cigar.
* Validations: validates :qty, numericality: { greater_than_or_equal_to: 0 }; After save, check humidor.available_slots >= 0 and rollback if over capacity (use callback).
* Methods: None additional.

Generate with: rails generate model ... as per earlier code.

### Controllers and CRUD Operations

All controllers inherit from ApplicationController. Use strong params. Auth: Basic HTTP auth for prod (add http_basic_authenticate_with).

* **HumidorsController** (RESTful):
  * Index: List all humidors with capacity/used/available. View: Table with edit/delete links.
  * Show: Details + list of inventories. View: Details card + table of cigars.
  * New/Create: Form for name/capacity.
  * Edit/Update: Same form.
  * Destroy: Delete if no inventories.
  * CRUD Routes: resources :humidors.
* **CigarsController** (RESTful):
  * Index: List all with total_qty and locations (JSON-like summary).
  * Show: Details + locations array.
  * New/Create: Form for name/brand/rating.
  * Edit/Update.
  * Destroy: If no inventories.
  * Routes: resources :cigars.
* **InventoriesController** (RESTful, nested under humidors or cigars? Use shallow nesting).
  * Index: All entries.
  * Show/New/Create/Edit/Update/Destroy: Standard, but create/update handles qty changes with capacity check.
  * Routes: resources :inventories.
* **ScansController** (For photo scanning):
  * Create (POST): Upload image, run OCR (Tesseract), fuzzy match to known cigars, update inventory based on mode (add/remove) and humidor_id.
    * Params: image (file), mode (add/remove), humidor_id.
    * If unrecognized, return error for manual entry.
  * Routes: post '/scan', to: 'scans#create'.
* **Api::InventoryController** (Namespaced for JSON API):
  * Index: Return JSON as specified (grouped by humidor, with cigar details).
  * Secure with API key param (check in before_action).
  * Routes: namespace :api do get '/inventory', to: 'inventory#index' end.
* **HomeController** (Dashboard):
  * Index: Aggregate view (totals, locations, capacities). Load via JS/AJAX if dynamic.

### Views (ERB)

* Layout: application.html.erb with Bootstrap for styling (add gem 'bootstrap').
* **Humidors** :
* index.html.erb: Table `<table><tr>``<th>`Name `</th><th>`Capacity `</th><th>`Available `</th>`...`</tr>` with @humidors.each.
* show.html.erb: `<h1>`<%= @humidor.name %>`</h1><p>`Available: <%= @humidor.available_slots %>`</p>` + inventories table.
* _form.html.erb: <%= form_with model: humidor do |f| %> <%= f.text_field :name %> <%= f.number_field :capacity %> ....
* **Cigars** :
* Similar: Index with totals/locations in columns (use partial for locations list).
* show.html.erb: Details + `<ul>`<%= @cigar.locations.each { |loc| `<li>`<%= loc[:humidor] %>: <%= loc[:qty] %>`</li>` } %>`</ul>`.
* **Inventories** : Standard scaffold views.
* **Dashboard (home/index.html.erb)** :
* Sections: Totals (ul/li per cigar), Capacities (ul/li per humidor), Scan buttons.
* JS for camera: Use `<video>`, `<canvas>` to capture, FormData POST to /scan.
* Dropdown for humidor select (populate via API or instance vars).
* **Partials** : _cigar.html.erb,_humidor.html.erb for reuse.

### Additional Features

* **OCR Integration** : In ScansController, use Tesseract.convert(image.path), fuzzy match with FuzzyStringMatch.
* **Data Import** : Rake task to import from Google Sheets (use 'google_drive' gem).
* **Capacity Logic** : Callbacks in Inventory to prevent overfill.
* **Testing** : RSpec for models (validations, methods), controllers (CRUD responses, API JSON format).

## 2. Tobacco Management System (Ruby on Rails App)

Analogous to Cigar System, but for tobacco storage (tins, bags, loose tobacco). Similar structure with adapted domain model for tobacco-specific needs.

### Detailed Domain Model

#### Core Relationships
- **TobaccoStorage** has_many :tobaccos
- **Tobacco** belongs_to :tobacco_storage

#### Model Specifications

**TobaccoStorage Model:**
- Attributes: name (string), location (string), image (attachment)
- Associations: has_many :tobaccos, dependent: :destroy
- Validations: presence of name, uniqueness of name

**Tobacco Model:**
- Attributes: tobacco_name (string), type (string), tobacco_storage_id (foreign key), qty_weight (decimal, in ounces), tobacco_image (attachment)
- Associations: belongs_to :tobacco_storage
- Validations: presence of tobacco_name, tobacco_storage_id; numericality of qty_weight > 0

#### Key Business Logic

**Weight-Based Tracking:**
- Track tobacco by weight in ounces (not individual units)
- Support partial usage with weight deduction
- Visual storage capacity indicators

**Tobacco Type Classification:**
- `type` field stores tobacco form (Loose Leaf, Flake, etc.)
- Supports empty type values for unclassified tobacco
- Useful for filtering and categorization in UI

**Image Management:**
- Upload tobacco tin/bag images for reference
- No OCR integration initially (manual data entry)
- Image gallery for storage identification

**JSON API Format:**
- Read-only public exposure of inventory data exposed with some sort of random token that doesn't change. This is to keep the url from being guessed, but allowing for easy access to the data for homeassistant to pull the inventory data.
- Format matches existing Google Sheets output. It needs to have the Tobacco Storage name, Tobacco name, type, and weight. Need all of the Tobacco Storage and their cigars returned in the json output.:
```json
{
  "tobacco": {
    "LargeTobaccoStorage": [
      {
        "tobacco_name": "Black Cherry",
        "type": "Loose Leaf",
        "qty_weight": 3
      }
    ],
    "LargeVerticalTobaccoStorage": [
      {
        "tobacco_name": "Lane Bulk RLP-6",
        "type": "Loose Leaf",  
        "qty_weight": 4
      },
      {
        "tobacco_name": "Maple Rum",
        "type": "Loose Leaf",
        "qty_weight": 12
      },
      {
        "tobacco_name": "Cornell & Diehl Green River Vanilla",
        "type": "Loose Leaf",
        "qty_weight": 1
      },
      {
        "tobacco_name": "Cornell & Diehl Autumn Evening",
        "type": "Loose Leaf",
        "qty_weight": 2
      }
    ],
    "Tins": [
      {
        "tobacco_name": "Squadron Leader",
        "type": "Flake",
        "qty_weight": 1
      }
    ]
  }
}
```

**Endpoint:** `GET /api/inventory/:token`
**Security:** Same token-based access as Cigar system

* Repository: tobacco-management-system
* Tech Stack: Ruby 3.3+, Rails 7.2+, Postgres, Bootstrap UI
* Testing: RSpec for all CRUD operations
* Deployment: Same infrastructure as Cigar system

## 3. Hosting Management System

### Overview

The Hosting Management System consists of TWO components that work together:

**A. Local CLI Tool (Python)**
* **Location**: Developer's laptop
* **Purpose**: Primary deployment and automation engine
* **Technology**: Python 3.12+ with Fabric/Paramiko, Click CLI framework
* **No Web Server**: CLI-only, no Flask or web interface running locally
* **Config Storage**: JSON files (config.json, .secrets.json)

**B. Remote Management Web Interface (FastAPI + Web UI)**
* **Location**: Deployed at hosting.remoteds.us on the remote server (`/opt/hosting-api/`)
* **Purpose**: Monitoring, control, and visibility dashboard
* **Technology**: FastAPI with Jinja2 templates, JWT authentication, REST API
* **Storage**: SQLite/JSON for lightweight state (no need for Postgres overhead)
* **Key Advantage**: Python manages Rails apps (no circular dependency)

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
├── config.json             # Server config (hosts, repos, domains)
├── .secrets.json          # Passwords, SSH keys, hosting credentials (gitignored)
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
├── tests/                 # Pytest test suite (update existing)
├── DEPLOYMENT_LOG.md      # Master deployment procedure log
├── ARCHITECTURE_PLAN.md   # Detailed architecture documentation
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

* **Config Files**:
  * `config.json`: Remote host, SSH paths, GitHub repos, domains, app metadata, backup dirs, `letsencrypt_email`
  * `.secrets.json`: Database passwords, secret key bases, SSL configs (NEVER committed to Git)
  * `deployment_key` / `.pub`: SSH keypair for Git operations on remote host

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
1. **[ARCHITECTURE_PLAN.md](hosting-management-system/ARCHITECTURE_PLAN.md)** - Complete system architecture and technical specifications
2. **[SECURITY_GUIDE.md](hosting-management-system/SECURITY_GUIDE.md)** - Security protocols, secret management, and compliance requirements  
3. **[SSL_SETUP.md](hosting-management-system/SSL_SETUP.md)** - Let's Encrypt SSL certificate management with certbot
4. **[DEPLOYMENT_PRACTICES.md](hosting-management-system/DEPLOYMENT_PRACTICES.md)** - Security protocols and deployment methods
5. **[COMPLETE_DEPLOYMENT_GUIDE.md](hosting-management-system/COMPLETE_DEPLOYMENT_GUIDE.md)** - Comprehensive guide for all three applications

### **📋 Implementation Documentation**
6. **[CHANGELOG_TODO_IMPLEMENTATION.md](hosting-management-system/CHANGELOG_TODO_IMPLEMENTATION.md)** - Detailed TODO implementation technical notes
7. **[PROJECT_COMPLETION_REPORT.md](hosting-management-system/PROJECT_COMPLETION_REPORT.md)** - Executive summary and current system status
8. **[ISSUES_RESOLUTION_SUMMARY.md](hosting-management-system/ISSUES_RESOLUTION_SUMMARY.md)** - Resolution summary for recent fixes

### **📜 Historical Documentation (Reference Only)**
9. **[DEPLOYMENT_LOG.md](hosting-management-system/DEPLOYMENT_LOG.md)** - Historical deployment logs for reference

---

## 🎯 **AI Agent Documentation Requirements**

### **📖 Before Starting Any Work**
1. **READ ARCHITECTURE_PLAN.md** - Understand system architecture and component relationships
2. **READ SECURITY_GUIDE.md** - Follow all security protocols without exception
3. **READ DEPLOYMENT_PRACTICES.md** - Use correct deployment methods for each application
4. **READ COMPLETE_DEPLOYMENT_GUIDE.md** - Use application-specific deployment commands

### **🔍 For SSL/HTTPS Work**
- **READ SSL_SETUP.md** - Use Let's Encrypt/certbot, NOT self-signed certificates
- Follow automated SSL setup procedures
- Verify certificate auto-renewal is configured

### **For Deployment Work**
- **ALWAYS read [HOSTING_DEPLOYMENT_GUIDE.md](docs/HOSTING_DEPLOYMENT_GUIDE.md) before deploying the hosting app** and anything related to the hosting app/API (kanban API, etc.)
- Use the correct deployment method for each application:
  - **Hosting System**: Follow Method 1 in HOSTING_DEPLOYMENT_GUIDE.md
    ```bash
    cd hosting-management-system
    git add -A && git commit -m "Description" && git push origin main
    python manager.py deploy-hosting-api --project-dir /opt/hosting-api
    python deploy-secure-sync.py
    python manager.py hms-api-service status
    ```
  - **Cigar App**: `python deploy-cigar.py` + `python deploy-cigar-secrets.py`  
  - **Tobacco App**: `python deploy-tobacco.py` + `python deploy-tobacco-secrets.py`
- NEVER copy .secrets.json to remote servers
- ALWAYS verify .env file permissions (600, correct ownership)

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
