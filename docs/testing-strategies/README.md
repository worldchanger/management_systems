# Testing Strategies

**Last Updated**: November 1, 2025  
**Version**: 1.0  
**Status**: ✅ ACTIVE

---

## 📋 Table of Contents
- [Overview](#overview)
- [Testing Philosophy](#testing-philosophy)
- [Application Testing Strategies](#application-testing-strategies)
- [Testing Tools](#testing-tools)
- [Test Coverage Requirements](#test-coverage-requirements)
- [Quick Reference](#quick-reference)

---

## 🎯 Overview

This folder contains comprehensive testing strategies for all applications in the management systems ecosystem. Each application has dedicated testing documentation covering unit tests, integration tests, and deployment verification.

### **Testing Hierarchy**
```
testing-strategies/
├── README.md (this file)              # Master testing index
├── cigar-testing-strategy.md          # Cigar app testing
├── tobacco-testing-strategy.md        # Tobacco app testing
├── whiskey-testing-strategy.md        # Whiskey app testing
└── hms-testing-strategy.md            # Hosting Management System testing
```

---

## 🧪 Testing Philosophy

### **Core Principles**
1. **Test Before Deploy** - All tests must pass before production deployment
2. **Test at Multiple Levels** - Unit, integration, and system tests
3. **Automate Everything** - No manual testing steps that can be automated
4. **Database-First** - Test database integrity and migrations
5. **Security-First** - Authentication and authorization are always tested

### **Testing Standards**
- **Minimum Code Coverage**: 85% across all applications
- **RSpec for Rails**: All Rails apps use RSpec for testing
- **Pytest for Python**: Hosting Management System uses Pytest
- **Integration Tests**: Must pass before any production push
- **Flaky Tests**: Mark as `@unstable` and quarantine until fixed

---

## 📱 Application Testing Strategies

### **Rails Applications**

#### **[Cigar Management System](cigar-testing-strategy.md)**
- **Database Schema**: 9 tables (users, cigars, brands, humidors, locations, etc.)
- **Test Coverage**: Model validations, controller actions, API endpoints
- **Special Focus**: OCR integration, inventory tracking, capacity management
- **Production URL**: https://cigars.remoteds.us

#### **[Tobacco Management System](tobacco-testing-strategy.md)**
- **Database Schema**: 6 tables (users, tobacco_products, brands, storages, locations)
- **Test Coverage**: Model validations, CRUD operations, capacity tracking
- **Special Focus**: Storage management, product relationships
- **Production URL**: https://tobacco.remoteds.us

#### **[Whiskey Management System](whiskey-testing-strategy.md)**
- **Database Schema**: 5 tables (users, whiskeys, brands, whiskey_types, locations)
- **Test Coverage**: Model validations, CRUD operations, inventory management
- **Special Focus**: Type classification, ABV/proof calculations
- **Production URL**: https://whiskey.remoteds.us

### **Python Application**

#### **[Hosting Management System](hms-testing-strategy.md)**
- **Framework**: FastAPI with PostgreSQL
- **Test Coverage**: API endpoints, deployment scripts, database operations
- **Special Focus**: Deployment automation, secrets management, app health checks
- **Production URL**: https://hosting.remoteds.us

---

## 🛠️ Testing Tools

### **Rails Applications (RSpec)**
```bash
# Run all tests
bundle exec rspec

# Run with coverage
bundle exec rspec --format documentation

# Run specific test file
bundle exec rspec spec/models/cigar_spec.rb

# Run tests matching pattern
bundle exec rspec spec/models --pattern "*_spec.rb"
```

### **Python Application (Pytest)**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_manager.py

# Run tests matching pattern
pytest -k "test_deploy"
```

---

## 📊 Test Coverage Requirements

### **Minimum Coverage by Component**
- **Models**: 90% coverage (critical business logic)
- **Controllers**: 85% coverage (all CRUD operations)
- **API Endpoints**: 100% coverage (all public APIs)
- **Authentication**: 100% coverage (security-critical)
- **Deployment Scripts**: 80% coverage (automation reliability)

### **What Must Be Tested**
1. **Model Validations**: All presence, uniqueness, and format validations
2. **Associations**: All has_many, belongs_to, has_many :through relationships
3. **Business Logic**: Capacity calculations, inventory tracking, aggregations
4. **Authentication**: Login, logout, password reset, session management
5. **Authorization**: Access control, role-based permissions
6. **API Endpoints**: Request/response formats, error handling, authentication
7. **Database Migrations**: All migrations can be applied and rolled back

### **What Should Be Tested**
- Edge cases and boundary conditions
- Error handling and validation failures
- Concurrent operations
- Performance under load
- Data integrity constraints

---

## 🚀 Quick Reference

### **Pre-Deployment Test Checklist**
```bash
# 1. Run local tests (Mac/Darwin)
cd /Users/bpauley/Projects/mangement-systems/{app}-management-system
bundle exec rspec

# 2. Verify database migrations
bundle exec rails db:migrate:status

# 3. Check test coverage
open coverage/index.html

# 4. Run health check after deployment (Linux)
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py health-check --app {app}"
```

### **Testing Commands by Environment**

#### **Local Development (Darwin/Mac)**
```bash
# Use local-rails-apps.sh for local deployment
./local-rails-apps.sh start cigar
./local-rails-apps.sh test cigar
./local-rails-apps.sh stop cigar
```

#### **Production Server (Linux)**
```bash
# Deploy with tests
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py deploy --app cigar --setup --local"

# Run health check
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py health-check --app cigar"

# Verify service status
ssh root@asterra.remoteds.us "systemctl status puma-cigar --no-pager"
```

---

## 📚 Related Documentation

### **Deployment Guides**
- [Cigar Deployment Guide](../deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md) - Full deployment procedures
- [Tobacco Deployment Guide](../deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md) - Full deployment procedures
- [Whiskey Deployment Guide](../deployment-guides/WHISKEY_DEPLOYMENT_GUIDE.md) - Full deployment procedures
- [Complete Deployment Guide](../deployment-guides/COMPLETE_DEPLOYMENT_GUIDE.md) - All applications

### **Application Design**
- [Cigar App Design](../application-design-documents/cigar-management-system.md) - Architecture and design
- [Tobacco App Design](../application-design-documents/tobacco-management-system.md) - Architecture and design
- [Whiskey App Design](../application-design-documents/whiskey-management-system.md) - Architecture and design

### **Architecture & Security**
- [Security Guide](../architecture-security/SECURITY_GUIDE.md) - Security testing requirements
- [Architecture Plan](../architecture-security/ARCHITECTURE_PLAN.md) - System architecture

---

## ✅ Testing Best Practices

### **Writing Good Tests**
1. **Descriptive Names**: Test names should describe what they test
2. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
3. **One Assertion**: Prefer one logical assertion per test
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Tests**: Keep tests fast to encourage frequent running

### **Test Data Management**
- Use **factories** (FactoryBot for Rails) for test data
- Use **fixtures** for static reference data
- **Clean up** after tests (use transactional fixtures)
- **Avoid hardcoded IDs** - use relationships instead

### **Continuous Integration**
- Tests run automatically on git push
- Deployment blocked if tests fail
- Coverage reports generated and tracked
- Failed tests must be fixed immediately

---

## 🆘 Troubleshooting

### **Common Issues**
| Issue | Solution |
|-------|----------|
| Tests pass locally but fail in CI | Check database state, environment variables |
| Flaky tests | Add `@unstable` tag, investigate race conditions |
| Slow test suite | Profile tests, parallelize, optimize database queries |
| Database errors | Check migrations, verify seed data |
| Authentication failures | Verify Devise configuration, check credentials |

### **Getting Help**
- Check application-specific testing strategy docs
- Review deployment guides for environment-specific issues
- Consult agents.md for testing requirements
- Check CI/CD logs for detailed error messages

---

**Last Updated**: November 1, 2025  
**Maintained By**: Development Team  
**Review Schedule**: Monthly or after major changes
