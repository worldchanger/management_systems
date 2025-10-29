# Management Systems Workspace

**Version**: 3.0  
**Last Updated**: October 29, 2025  
**Status**: ✅ **ACTIVE** - Consolidated documentation and deployment system

---

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Quick Start Guide](#quick-start-guide)
- [Applications](#applications)
- [Documentation Structure](#documentation-structure)
- [Development Workflow](#development-workflow)
- [Security & Configuration](#security--configuration)
- [Repository Structure](#repository-structure)

---

## 🎯 System Overview

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

---

## 🚀 Quick Start Guide

### **For New Development**
1. **Read the Rules**: Start with [agents.md](agents.md) - the master development rules document
2. **Choose Your Application**: 
   - Cigar app → [CIGAR_DEPLOYMENT_GUIDE.md](docs/CIGAR_DEPLOYMENT_GUIDE.md)
   - Tobacco app → [TOBACCO_DEPLOYMENT_GUIDE.md](docs/TOBACCO_DEPLOYMENT_GUIDE.md)
   - Hosting system → [HOSTING_DEPLOYMENT_GUIDE.md](docs/HOSTING_DEPLOYMENT_GUIDE.md)
3. **Set Up Local Environment**: Follow the application-specific setup instructions
4. **Run Tests**: Ensure all tests pass before making changes
5. **Deploy**: Use the hosting management system for deployment

### **For Deployment**
```bash
# Rails Applications (Cigar/Tobacco)
cd [application]-management-system
bundle exec rspec                    # Run tests
git add -A && git commit -m "Changes" && git push
cd ../hosting-management-system
python manager.py deploy --app [application]

# Hosting Management System
cd hosting-management-system
python -m pytest                    # Run tests
git add -A && git commit -m "Changes" && git push
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
python deploy-secure-sync.py
```

---

## 📱 Applications

### **1. Cigar Management System**
- **Repository**: `cigar-management-system/`
- **Purpose**: Track cigar inventory across multiple humidors
- **Features**: 
  - CRUD operations for cigars, humidors, and brands
  - OCR support for cigar band scanning
  - Capacity tracking and management
  - JSON API for Home Assistant integration
- **Technology**: Ruby on Rails 7.2.2, PostgreSQL, Bootstrap UI
- **Documentation**: [docs/CIGAR_DEPLOYMENT_GUIDE.md](docs/CIGAR_DEPLOYMENT_GUIDE.md)

### **2. Tobacco Management System**
- **Repository**: `tobacco-management-system/`
- **Purpose**: Track tobacco products and storage management
- **Features**:
  - Weight-based tracking (ounces)
  - Tobacco type classification
  - Multiple storage unit management
  - JSON API for Home Assistant integration
- **Technology**: Ruby on Rails 7.2.2, PostgreSQL, Bootstrap UI
- **Documentation**: [docs/TOBACCO_DEPLOYMENT_GUIDE.md](docs/TOBACCO_DEPLOYMENT_GUIDE.md)

### **3. Hosting Management System**
- **Repository**: `hosting-management-system/`
- **Purpose**: Deploy, monitor, and manage Rails applications
- **Features**:
  - Web-based dashboard for monitoring
  - REST API for programmatic management
  - TODO/Kanban system for task tracking
  - Log viewing and service control
- **Technology**: Python FastAPI, SQLite, Nginx, systemd
- **Documentation**: [docs/HOSTING_DEPLOYMENT_GUIDE.md](docs/HOSTING_DEPLOYMENT_GUIDE.md)

---

## 📚 Documentation Structure

### **🎯 Required Reading Order**
1. **[agents.md](agents.md)** - Master development rules and system architecture
2. **This README.md** - System overview and navigation (you are here)
3. **Application-specific deployment guide** based on your work

### **📖 Documentation Hierarchy**
```
agents.md (GOLDEN RULES)
├── README.md (System Overview)
├── docs/
│   ├── CIGAR_DEPLOYMENT_GUIDE.md (Cigar app procedures)
│   ├── TOBACCO_DEPLOYMENT_GUIDE.md (Tobacco app procedures)
│   ├── HOSTING_DEPLOYMENT_GUIDE.md (Hosting system procedures)
│   ├── CHANGELOG.md (System change tracking)
│   ├── TODO.md (Task tracking interface)
│   └── [Additional documentation files]
└── Individual repository README.md files
```

### **📋 Key Documents**
- **[agents.md](agents.md)** - Master rules, architecture, and development protocols
- **[docs/CIGAR_DEPLOYMENT_GUIDE.md](docs/CIGAR_DEPLOYMENT_GUIDE.md)** - Cigar app deployment and development
- **[docs/TOBACCO_DEPLOYMENT_GUIDE.md](docs/TOBACCO_DEPLOYMENT_GUIDE.md)** - Tobacco app deployment and development
- **[docs/HOSTING_DEPLOYMENT_GUIDE.md](docs/HOSTING_DEPLOYMENT_GUIDE.md)** - Hosting system deployment and management
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - System change tracking and release notes
- **[docs/TODO.md](docs/TODO.md)** - Task tracking via hosting management interface

---

## 🔄 Development Workflow

### **Core Principles**
- **Local Development First**: All development happens locally before deployment
- **Test-Driven**: Tests must pass before any deployment
- **Git Flow**: Commit to main branch, then deploy via management system
- **Security First**: Never commit secrets, use environment variables

### **Rails Application Development**
```bash
# 1. Setup and Development
cd [application]-management-system
bundle install
rails db:create db:migrate db:seed
rails server

# 2. Testing
bundle exec rspec
rubocop

# 3. Deployment
git add -A && git commit -m "Description" && git push
cd ../hosting-management-system
python manager.py deploy --app [application]
```

### **Hosting System Development**
```bash
# 1. Development
cd hosting-management-system
python -m pytest

# 2. Deployment
git add -A && git commit -m "Description" && git push
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
python deploy-secure-sync.py
```

---

## 🔒 Security & Configuration

### **Security Protocols (CRITICAL)**
- **❌ NEVER copy .secrets.json to any remote server**
- **❌ NEVER commit secrets to version control**
- **✅ ALWAYS use environment variables for production**
- **✅ ALWAYS verify file permissions (600)**
- **✅ ALWAYS use www-data:www-data ownership**

### **Configuration Files**
- **`config.json`** - Public configuration (domains, repositories, settings)
- **`.secrets.json`** - Private credentials (gitignored, workspace root only)
- **Individual `.env` files** - Production environment variables per application

### **Secrets Management**
- **Location**: `/Users/bpauley/Projects/mangement-systems/.secrets.json`
- **Purpose**: Central credential storage reference
- **Rule**: Never place secrets inside application repositories

---

## 📁 Repository Structure

```
/Users/bpauley/Projects/mangement-systems/
├── agents.md                         # Master development rules
├── README.md                         # System overview (this file)
├── config.json                       # Public configuration
├── .secrets.json                     # Private credentials (gitignored)
├── docs/                             # Consolidated documentation
│   ├── CHANGELOG.md                  # Change tracking
│   ├── CIGAR_DEPLOYMENT_GUIDE.md     # Cigar app procedures
│   ├── TOBACCO_DEPLOYMENT_GUIDE.md   # Tobacco app procedures
│   ├── HOSTING_DEPLOYMENT_GUIDE.md   # Hosting system procedures
│   ├── TODO.md                       # Task tracking
│   └── [Additional documentation]    # Other reference materials
├── cigar-management-system/          # Git repository
├── tobacco-management-system/        # Git repository
├── hosting-management-system/        # Git repository
└── qa-test-repo/                     # Testing repository
```

### **Individual Repository READMEs**
Each application repository contains its own README.md with:
- Application-specific setup instructions
- Local development guidelines
- Testing procedures
- Deployment references
- API documentation

---

## 🔌 JSON API Endpoints

### **Cigar App Inventory API**
- **Endpoint**: `GET https://cigars.remoteds.us/api/inventory/:token`
- **Purpose**: Home Assistant integration
- **Format**: Grouped by humidor with cigar details
- **Authentication**: Token-based access

### **Tobacco App Inventory API**
- **Endpoint**: `GET https://tobacco.remoteds.us/api/inventory/:token`
- **Purpose**: Home Assistant integration
- **Format**: Grouped by storage unit with tobacco details
- **Authentication**: Token-based access

### **Hosting Management API**
- **Endpoint**: `https://hosting.remoteds.us/api/`
- **Purpose**: System management and monitoring
- **Authentication**: JWT-based login required
- **Features**: Service control, log viewing, configuration management

---

## 🧪 Testing Requirements

### **Rails Applications (Cigar, Tobacco)**
```bash
bundle exec rspec                    # All tests
bundle exec rspec --format documentation  # Detailed output
rubocop                             # Code quality
```

### **Python Applications (Hosting Management)**
```bash
python -m pytest                    # All tests
python -m pytest --cov=.           # With coverage
pylint *.py                        # Code quality
```

### **Testing Checklist**
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] Code quality checks passing
- [ ] No security vulnerabilities

---

## 📞 Support and Troubleshooting

### **First Steps for Issues**
1. **Check Documentation**: Review relevant deployment guide in `docs/`
2. **Review agents.md**: Follow master development rules
3. **Check Logs**: Use hosting management interface for log viewing
4. **Verify Configuration**: Check environment variables and permissions
5. **Test Locally**: Reproduce issue in local development environment

### **Getting Help**
- **Documentation**: Start with [agents.md](agents.md) and application-specific guides
- **Monitoring**: Use https://hosting.remoteds.us for production monitoring
- **Logs**: Access via hosting management web interface
- **Emergency**: Use service management commands in deployment guides

---

## 📊 System Status

### **Current Version Information**
- **Documentation Version**: 3.0 (Consolidated structure)
- **Last Updated**: October 29, 2025
- **Next Review**: January 29, 2026

### **Recent Changes**
- ✅ Consolidated all documentation into `docs/` folder
- ✅ Created application-specific deployment guides
- ✅ Updated agents.md as master rules document
- ✅ Eliminated documentation duplication
- ✅ Established clear documentation hierarchy

---

## 🎯 Navigation Quick Links

### **Start Here**
- **[📋 agents.md](agents.md)** - Master development rules and architecture
- **[📖 CIGAR_DEPLOYMENT_GUIDE.md](docs/CIGAR_DEPLOYMENT_GUIDE.md)** - Cigar app procedures
- **[📖 TOBACCO_DEPLOYMENT_GUIDE.md](docs/TOBACCO_DEPLOYMENT_GUIDE.md)** - Tobacco app procedures
- **[📖 HOSTING_DEPLOYMENT_GUIDE.md](docs/HOSTING_DEPLOYMENT_GUIDE.md)** - Hosting system procedures

### **Reference**
- **[📊 CHANGELOG.md](docs/CHANGELOG.md)** - System change tracking
- **[✅ TODO.md](docs/TODO.md)** - Task tracking interface
- **[🔧 Individual Repository READMEs]** - Application-specific documentation

---

**This workspace follows the development rules outlined in [agents.md](agents.md). All team members must read and understand these protocols before making any changes.**
