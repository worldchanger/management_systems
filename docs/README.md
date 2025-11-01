# Documentation Master Index

**Last Updated**: November 1, 2025  
**Version**: 5.0  
**Status**: ✅ **ACTIVE** - Reorganized with folder structure

---

## 📋 Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Application Documentation](#application-documentation)
- [System Architecture](#system-architecture)
- [Deployment Guides](#deployment-guides)
- [Testing Strategies](#testing-strategies)
- [Development Guidelines](#development-guidelines)
- [Reference Documentation](#reference-documentation)

---

## 🎯 Overview

This directory contains the complete documentation for the Management Systems workspace, which includes four interconnected applications:

1. **Cigar Management System** - Track cigar inventory across multiple humidors
2. **Tobacco Management System** - Manage tobacco products and storage
3. **Whiskey Management System** - Track whiskey collection with detailed specifications
4. **Hosting Management System** - Deploy, monitor, and manage all Rails applications

All documentation follows a hierarchical structure with **agents.md** as the master rules document.

---

## 🚀 Getting Started

### **Required Reading Order**
1. **[../agents.md](../agents.md)** - Master development rules (MUST READ FIRST)
2. **This README.md** - Documentation navigation (you are here)
3. **Application-specific documentation** - Based on your work area

### **New Developer Onboarding**
```bash
# 1. Read the master rules
cat ../agents.md

# 2. Navigate documentation
cat docs/README.md

# 3. Review architecture
cat docs/ARCHITECTURE_PLAN.md

# 4. Check deployment guides for your app
cat docs/[APP]_DEPLOYMENT_GUIDE.md
```

---

## 📱 Application Documentation

### **📁 application-design-documents/**

Complete application design documents with database schemas, business logic, API endpoints, and deployment configuration.

#### **Cigar Management System**
- **[cigar-management-system.md](application-design-documents/cigar-management-system.md)**
  - Database schema and models
  - Business logic and features
  - OCR integration
  - API endpoints
  - Technology stack
  - Deployment configuration

#### **Tobacco Management System**
- **[tobacco-management-system.md](application-design-documents/tobacco-management-system.md)**
  - Database schema and models
  - Weight-based tracking system
  - Tobacco type classification
  - API endpoints
  - Technology stack
  - Deployment configuration

#### **Whiskey Management System**
- **[whiskey-management-system.md](application-design-documents/whiskey-management-system.md)**
  - Database schema and models
  - Whiskey type taxonomy
  - Brand and location management
  - API endpoints
  - Technology stack
  - Deployment configuration

---

## 🏗️ System Architecture

### **📁 architecture-security/**

Architecture documents, security protocols, and operational guidelines.

#### **Architecture**
- **[ARCHITECTURE_PLAN.md](architecture-security/ARCHITECTURE_PLAN.md)** - Complete system architecture
  - Overall system design
  - Component relationships
  - Database schema (all apps)
  - Deployment strategy
  - Security architecture
  - Technology stack

- **[ARCHITECTURE_SUMMARY.md](architecture-security/ARCHITECTURE_SUMMARY.md)** - Quick reference summary
  - High-level overview
  - Key components
  - Integration points

#### **Security & Operations**
- **[SECURITY_GUIDE.md](architecture-security/SECURITY_GUIDE.md)** - Complete security protocols
  - Secret management rules
  - Database-first architecture
  - Environment variable handling
  - File permissions
  - Access control

- **[SSL_SETUP.md](architecture-security/SSL_SETUP.md)** - SSL certificate management
  - Let's Encrypt setup
  - Certbot configuration
  - Auto-renewal
  - Troubleshooting

- **[DEPLOYMENT_PRACTICES.md](architecture-security/DEPLOYMENT_PRACTICES.md)** - Security deployment methods
  - deploy-secure-sync.py usage
  - Systemd service configuration
  - Secret deployment workflow

---

## 🚀 Deployment Guides

### **📁 deployment-guides/**

Step-by-step deployment procedures for all applications.

- **[CIGAR_DEPLOYMENT_GUIDE.md](deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md)** - Cigar app procedures
  - Local development setup
  - Deployment process
  - Database management
  - SSL configuration
  - Troubleshooting

- **[TOBACCO_DEPLOYMENT_GUIDE.md](deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md)** - Tobacco app procedures
  - Local development setup
  - Deployment process
  - Database management
  - SSL configuration
  - Troubleshooting

- **[HOSTING_DEPLOYMENT_GUIDE.md](deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md)** - HMS procedures
  - Local CLI tool usage
  - Web interface deployment
  - Secret management
  - Service management
  - Troubleshooting

- **[COMPLETE_DEPLOYMENT_GUIDE.md](deployment-guides/COMPLETE_DEPLOYMENT_GUIDE.md)** - Comprehensive guide
  - All applications
  - Full deployment workflows
  - Cross-application dependencies

---

## 🧪 Testing Strategies

### **📁 testing-strategies/**

Comprehensive testing strategies and requirements for all applications.

- **[README.md](testing-strategies/README.md)** - Testing overview and standards
  - Testing philosophy
  - Coverage requirements
  - Testing tools and frameworks
  - Best practices
  - Quick reference commands

#### **Application-Specific Testing**
- **[cigar-testing-strategy.md](testing-strategies/cigar-testing-strategy.md)** - Cigar app testing
  - Database schema validation
  - Model testing (9 tables)
  - Controller testing
  - Integration testing
  - API testing (inventory endpoint)
  - Authentication testing
  - Deployment verification

- **[tobacco-testing-strategy.md](testing-strategies/tobacco-testing-strategy.md)** - Tobacco app testing
  - Database schema validation
  - Model testing (6 tables)
  - Controller testing
  - Integration testing
  - Authentication testing
  - Deployment verification

- **[whiskey-testing-strategy.md](testing-strategies/whiskey-testing-strategy.md)** - Whiskey app testing
  - Database schema validation
  - Model testing (5 tables)
  - ABV/Proof calculations
  - Controller testing
  - Integration testing
  - Authentication testing
  - Deployment verification

- **[hms-testing-strategy.md](testing-strategies/hms-testing-strategy.md)** - HMS testing
  - API endpoint testing
  - Deployment script testing
  - Database operations testing
  - Health check system testing
  - Integration testing
  - Security testing

---

## 💻 Development Guidelines

See **[reference/](reference/)** folder for development resources and quick start guides.

---

## 📊 Reference Documentation

### **📁 reference/**

Change tracking, implementation notes, development guides, and historical references.

#### **Change Management**
- **[CHANGELOG.md](reference/CHANGELOG.md)** - System change tracking
  - Release history
  - Feature additions
  - Bug fixes
  - Breaking changes

#### **Development Resources**
- **[LOCAL_RAILS_DEVELOPMENT.md](reference/LOCAL_RAILS_DEVELOPMENT.md)** - Rails development setup
  - Environment configuration
  - Testing requirements
  - Pre-deployment checklist

- **[DEPLOYMENT_CHECKLIST.md](reference/DEPLOYMENT_CHECKLIST.md)** - Verification procedures
  - Pre-deployment checks
  - Post-deployment verification
  - Security validation

- **[QUICK_START.md](reference/QUICK_START.md)** - Quick reference commands
  - Common tasks
  - Testing commands
  - Deployment shortcuts

#### **Task Management**
- **[TODO.md](reference/TODO.md)** - ⚠️ **DEPRECATED**
  - Use Kanban API instead
  - Historical reference only

- **[KANBAN_POSTGRES_IMPLEMENTATION.md](reference/KANBAN_POSTGRES_IMPLEMENTATION.md)** - Kanban system design
  - PostgreSQL schema
  - API endpoints
  - Migration from file-based TODO

#### **Implementation Notes**
- **[IMPLEMENTATION_PLAN.md](reference/IMPLEMENTATION_PLAN.md)** - System implementation details
- **[IMPLEMENTATION_SUMMARY.md](reference/IMPLEMENTATION_SUMMARY.md)** - Implementation summary
- **[DEPLOYMENT_COMPLETE.md](reference/DEPLOYMENT_COMPLETE.md)** - Deployment completion notes
- **[DECOMMISSION_SCRIPT_FIX.md](reference/DECOMMISSION_SCRIPT_FIX.md)** - Script fix documentation

---

## 🗂️ Documentation Organization

### **Documentation Hierarchy**
```
/docs/
├── README.md                                      # Master index (this file)
│
├── application-design-documents/                  # 📁 App Design Docs
│   ├── cigar-management-system.md                 # Cigar app complete design
│   ├── tobacco-management-system.md               # Tobacco app complete design
│   └── whiskey-management-system.md               # Whiskey app complete design
│
├── deployment-guides/                             # 📁 Deployment Procedures
│   ├── CIGAR_DEPLOYMENT_GUIDE.md                  # Cigar deployment
│   ├── TOBACCO_DEPLOYMENT_GUIDE.md                # Tobacco deployment
│   ├── HOSTING_DEPLOYMENT_GUIDE.md                # HMS deployment
│   └── COMPLETE_DEPLOYMENT_GUIDE.md               # Comprehensive guide
│
├── architecture-security/                         # 📁 Architecture & Security
│   ├── ARCHITECTURE_PLAN.md                       # System architecture
│   ├── ARCHITECTURE_SUMMARY.md                    # Quick reference
│   ├── SECURITY_GUIDE.md                          # Security protocols
│   ├── SSL_SETUP.md                               # SSL management
│   └── DEPLOYMENT_PRACTICES.md                    # Secure deployment
│
└── reference/                                     # 📁 Reference & History
    ├── CHANGELOG.md                               # Change tracking
    ├── LOCAL_RAILS_DEVELOPMENT.md                 # Dev setup
    ├── DEPLOYMENT_CHECKLIST.md                    # Verification
    ├── QUICK_START.md                             # Quick reference
    ├── KANBAN_POSTGRES_IMPLEMENTATION.md          # Kanban system
    ├── IMPLEMENTATION_PLAN.md                     # Implementation notes
    ├── IMPLEMENTATION_SUMMARY.md                  # Summary
    ├── DEPLOYMENT_COMPLETE.md                     # Completion notes
    ├── DECOMMISSION_SCRIPT_FIX.md                 # Script fixes
    └── TODO.md                                    # ⚠️ DEPRECATED
```

---

## 📖 Documentation Standards

### **Document Requirements**
All documentation must include:
- **Last Updated** date at the top
- **Status** indicator (Active, Deprecated, Draft)
- **Table of Contents** for documents > 100 lines
- **Related Documentation** links at bottom
- **Navigation links** to parent/child documents

### **Update Process**
When updating documentation:
1. Update the "Last Updated" date
2. Increment version number if major changes
3. Update CHANGELOG.md with changes
4. Update this README.md index if structure changes
5. Cross-check related documents for consistency

### **Document Types**
- **Master Rules**: agents.md (workspace root)
- **Architecture**: ARCHITECTURE_PLAN.md, app design docs
- **Procedures**: Deployment guides, security guides
- **Reference**: CHANGELOG.md, implementation notes
- **Quick Start**: QUICK_START.md, checklists

---

## 🔍 Finding Information

### **By Task**
| Task | Document |
|------|----------|
| Starting development | [../agents.md](../agents.md) |
| Understanding architecture | [ARCHITECTURE_PLAN.md](architecture-security/ARCHITECTURE_PLAN.md) |
| Deploying cigar app | [CIGAR_DEPLOYMENT_GUIDE.md](deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md) |
| Deploying tobacco app | [TOBACCO_DEPLOYMENT_GUIDE.md](deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md) |
| Deploying hosting system | [HOSTING_DEPLOYMENT_GUIDE.md](deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md) |
| Managing secrets | [SECURITY_GUIDE.md](architecture-security/SECURITY_GUIDE.md) |
| Setting up SSL | [SSL_SETUP.md](architecture-security/SSL_SETUP.md) |
| Local Rails development | [LOCAL_RAILS_DEVELOPMENT.md](reference/LOCAL_RAILS_DEVELOPMENT.md) |
| Understanding app design | See [application-design-documents/](application-design-documents/) |

### **By Application**
| Application | Design Doc | Deployment Guide |
|-------------|------------|------------------|
| Cigar | [cigar-management-system.md](application-design-documents/cigar-management-system.md) | [CIGAR_DEPLOYMENT_GUIDE.md](deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md) |
| Tobacco | [tobacco-management-system.md](application-design-documents/tobacco-management-system.md) | [TOBACCO_DEPLOYMENT_GUIDE.md](deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md) |
| Whiskey | [whiskey-management-system.md](application-design-documents/whiskey-management-system.md) | TBD |
| Hosting | TBD | [HOSTING_DEPLOYMENT_GUIDE.md](deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md) |

---

## ✅ Documentation Integrity

### **Verification Checklist**
- [ ] All documents have "Last Updated" dates
- [ ] Navigation links are valid and working
- [ ] Related documentation cross-references are current
- [ ] No duplicate or conflicting information
- [ ] All app design docs exist and are complete
- [ ] Deployment guides match current procedures
- [ ] Security protocols are documented correctly
- [ ] ARCHITECTURE_PLAN.md includes all apps

### **Single Source of Truth**
- **Master Rules**: [../agents.md](../agents.md)
- **System Architecture**: [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)
- **Security Protocols**: [SECURITY_GUIDE.md](SECURITY_GUIDE.md)
- **App Designs**: Individual app .md files in this directory

### **Conflict Resolution**
If conflicts exist between documents:
1. **agents.md** takes precedence (master rules)
2. **ARCHITECTURE_PLAN.md** for architectural decisions
3. **SECURITY_GUIDE.md** for security protocols
4. Application-specific docs for app-level details

---

## 🔗 Quick Links

### **Essential Documents**
- [Master Rules (agents.md)](../agents.md)
- [System Overview (README.md)](../README.md)
- [Architecture Plan](architecture-security/ARCHITECTURE_PLAN.md)
- [Security Guide](architecture-security/SECURITY_GUIDE.md)

### **Application Design**
- [Cigar App Design](application-design-documents/cigar-management-system.md)
- [Tobacco App Design](application-design-documents/tobacco-management-system.md)
- [Whiskey App Design](application-design-documents/whiskey-management-system.md)

### **Deployment**
- [Cigar Deployment](deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md)
- [Tobacco Deployment](deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md)
- [Hosting Deployment](deployment-guides/HOSTING_DEPLOYMENT_GUIDE.md)

---

## 📝 Maintenance

### **Regular Reviews**
- **Monthly**: Verify all "Last Updated" dates are current
- **Quarterly**: Review entire documentation structure
- **After Major Changes**: Update CHANGELOG.md and affected docs
- **After Deployment Issues**: Update troubleshooting sections

### **Document Ownership**
- **Technical Lead**: Overall documentation integrity
- **Developers**: Keep deployment guides current
- **AI Agents**: Update docs when making changes
- **Users**: Report documentation issues

---

**This index is maintained as the single navigation point for all workspace documentation. Keep it current, accurate, and comprehensive.**

**Last Updated**: November 1, 2025  
**Next Review**: December 1, 2025  
**Maintained by**: AI Agent + Developer Team
