# TODO / Kanban Task Tracking

**Last Updated**: October 30, 2025 4:21 PM  
**Status**: Active task tracking for all remaining work

---

## 🔴 HIGH PRIORITY - In Progress

### 1. Cigar App Image Display Fix
- **Status**: TODO
- **Priority**: HIGH
- **Description**: Cigar band images not displaying on show page - links broken
- **Notes**: Need to investigate if images are saving correctly, check Active Storage configuration

### 2. Humidor Show Page Enhancements
- **Status**: TODO
- **Priority**: HIGH
- **Description**: Add cigar image thumbnails to left of brand name, make images clickable to cigar show page
- **Subtasks**:
  - [ ] Add thumbnail column to cigars table in humidor show view
  - [ ] Make thumbnails link to cigar show page
  - [ ] Make brand names clickable links to brand page

### 3. Brand Show Page Enhancements
- **Status**: TODO
- **Priority**: HIGH
- **Description**: Multiple improvements needed
- **Subtasks**:
  - [ ] Add cigar thumbnails to left of cigar name
  - [ ] Fix "Total Inventory" to show actual count sum
  - [ ] Replace location display with humidor + link
  - [ ] Make humidor names clickable

### 4. Deploy Script Enhancement - API Tokens
- **Status**: TODO
- **Priority**: HIGH  
- **Description**: Update deploy-secure-sync.py to deploy API tokens to Rails apps
- **Subtasks**:
  - [ ] Read API tokens from .secrets.json
  - [ ] Deploy to cigar app systemd service file as ENV variable
  - [ ] Deploy to tobacco app systemd service file as ENV variable
  - [ ] Test token deployment

### 5. Update Deployment Documentation
- **Status**: TODO
- **Priority**: HIGH
- **Description**: Update HOSTING_DEPLOYMENT_GUIDE.md with API token deployment process
- **Subtasks**:
  - [ ] Document API token deployment step
  - [ ] Document deployment order: secrets first, then app code
  - [ ] Document verification process for API endpoints
  - [ ] Add troubleshooting section for API issues

### 6. Production Deployment - Cigar App
- **Status**: TODO
- **Priority**: HIGH
- **Description**: Deploy cigar app with API token support
- **Subtasks**:
  - [ ] Run deploy-secure-sync.py to set API token
  - [ ] Deploy cigar app code
  - [ ] Verify API endpoint works with token
  - [ ] Check all routes for proper auth redirects
  - [ ] Login and verify all pages load
  - [ ] Check logs for errors

### 7. Production Deployment - Tobacco App
- **Status**: TODO
- **Priority**: HIGH
- **Description**: Deploy tobacco app with API token support
- **Subtasks**:
  - [ ] Run deploy-secure-sync.py to set API token
  - [ ] Deploy tobacco app code  
  - [ ] Verify API endpoint works with token
  - [ ] Check all routes for proper auth redirects
  - [ ] Login and verify all pages load
  - [ ] Check logs for errors

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

## 📊 Summary Statistics

- **Total Tasks**: 9
- **Completed**: 7
- **In Progress**: 0
- **TODO**: 9
- **High Priority**: 7
- **Medium Priority**: 2
