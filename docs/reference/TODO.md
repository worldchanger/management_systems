# TODO / Kanban Task Tracking

**Last Updated**: October 30, 2025 4:21 PM  
**Status**: Active task tracking for all remaining work

---

## 🔴 HIGH PRIORITY - Ready for Production Deployment

### 1. Deploy Script Enhancement - API Tokens ✅ 
- **Status**: COMPLETED
- **Priority**: HIGH  
- **Description**: Updated deploy-secure-sync.py to deploy API tokens to Rails apps
- **Completed**: Oct 30, 2025
- **Subtasks**:
  - [x] Read API tokens from .secrets.json
  - [x] Deploy to cigar app systemd service file as ENV variable
  - [x] Deploy to tobacco app systemd service file as ENV variable
  - [x] Added systemd daemon reload
  - [x] Added restart instructions

### 2. Update Deployment Documentation ✅
- **Status**: COMPLETED
- **Priority**: HIGH
- **Description**: Updated HOSTING_DEPLOYMENT_GUIDE.md with comprehensive Rails deployment
- **Completed**: Oct 30, 2025
- **Subtasks**:
  - [x] Document API token deployment step
  - [x] Document deployment order: secrets first, then app code
  - [x] Document verification process for API endpoints
  - [x] Add troubleshooting section for API issues
  - [x] Added comprehensive deployment checklist
  - [x] Added common issues and fixes

### 3. Humidor Show Page Enhancements ✅
- **Status**: COMPLETED
- **Priority**: HIGH
- **Description**: Added cigar image thumbnails and enhanced navigation
- **Completed**: Oct 30, 2025
- **Subtasks**:
  - [x] Add thumbnail column to cigars table in humidor show view
  - [x] Make thumbnails link to cigar show page
  - [x] Make brand names clickable links to brand page
  - [x] Show placeholder for missing images

### 4. Brand Show Page Enhancements ✅
- **Status**: COMPLETED
- **Priority**: HIGH
- **Description**: Multiple improvements implemented
- **Completed**: Oct 30, 2025
- **Subtasks**:
  - [x] Add cigar thumbnails to left of cigar name
  - [x] Fix "Total Inventory" to show actual count sum
  - [x] Replace location display with humidor + link
  - [x] Make humidor names clickable
  - [x] Show quantities per humidor

### 5. Production Deployment - Cigar App ✅
- **Status**: COMPLETED
- **Priority**: HIGH
- **Description**: Deploy cigar app with API token support
- **Completed**: Oct 30, 2025
- **Subtasks**:
  - [x] Run deploy-secure-sync.py to set API token
  - [x] Deploy cigar app code
  - [x] Verify API endpoint works with token
  - [x] All secrets deployed via deploy-secure-sync.py
  - [x] Service restarted successfully
  - [x] API returning valid JSON data

### 6. Production Deployment - Tobacco App ✅
- **Status**: COMPLETED
- **Priority**: HIGH
- **Description**: Deploy tobacco app with API token support
- **Completed**: Oct 30, 2025
- **Subtasks**:
  - [x] Run deploy-secure-sync.py to set API token
  - [x] Deploy tobacco app code  
  - [x] All secrets deployed via deploy-secure-sync.py
  - [x] Fixed database.yml (added host: 127.0.0.1)
  - [x] Database migrations run successfully (8 tables created)
  - [x] Admin user created successfully
  - [x] Service restarted successfully
  - [x] API endpoint verified - returns JSON data ✅
  - [x] Web app login working

---

## 🟡 MEDIUM PRIORITY - Backlog

### 8. Location Maps Integration
- **Status**: TODO
- **Priority**: MEDIUM
- **Description**: Add embedded maps to location show pages using free service
- **Options**: OpenStreetMap, Google Maps embed, Mapbox
- **Both Apps**: Cigar and Tobacco

### 9. Tobacco Add/Remove Quantity Functionality
- **Status**: TODO
- **Priority**: MEDIUM
- **Description**: Implement add/remove quantity actions for storage_tobaccos
- **Similar to**: Humidor cigars add/remove functionality in cigar app

---

## ✅ COMPLETED

### ✓ Agents.md Rule #1 Addition
- Added mandatory task tracking as first rule
- Completed: Oct 30, 2025

### ✓ Tobacco App - Missing Show Views
- Created locations/show, storages/show, tobacco_products/show, brands/show, users/show
- Completed: Oct 30, 2025

### ✓ Tobacco Dashboard Implementation  
- Summary cards, top brands, recently used, storage overview
- Completed: Oct 30, 2025

### ✓ Fixed Tobacco Routes
- Fixed storage_tobaccos routing errors
- Completed: Oct 30, 2025

### ✓ API Token System Implementation
- Token-based authentication for both cigar and tobacco APIs
- Tokens from .secrets.json via ENV variables
- Tested locally and working
- Completed: Oct 30, 2025

### ✓ Users Show View - Both Apps
- Created users/show.html.erb for cigar and tobacco apps
- Completed: Oct 30, 2025

### ✓ Config.json API URL Updates
- Updated with proper tokenized API URLs
- Completed: Oct 30, 2025

---

## ✅ RECENTLY COMPLETED

### ✓ Deploy-Secure-Sync.py Refactor
- **Completed**: Oct 30, 2025
- **Description**: Complete refactor of deployment secrets system
- **Changes**:
  - Made deploy-secure-sync.py the SOLE method for deploying secrets
  - Added full Rails secret deployment (SECRET_KEY_BASE, DATABASE_PASSWORD, API_TOKEN)
  - Added command-line options: --app, --hms, --rails-only, --no-restart
  - Automated service restart after deployment
  - Comprehensive error checking and status messages
- **Impact**: Eliminates secret deployment conflicts between manager.py and deploy-secure-sync.py

---

## 📊 Summary Statistics

- **Total Tasks**: 14
- **Completed**: 13
- **In Progress**: 0
- **TODO (Backlog)**: 2
- **High Priority**: 6 (all completed)
- **Medium Priority**: 2 (backlog)
