# Tobacco Management System Deployment Guide

**Version**: 3.0  
**Last Updated**: October 29, 2025  
**Status**: ✅ **ACTIVE** - Rails application deployment procedures

---

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Deployment Process](#deployment-process)
- [Database Management](#database-management)
- [SSL Configuration](#ssl-configuration)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

The Tobacco Management System is a Ruby on Rails 7.2.2 application for tracking tobacco products and inventory management, analogous to the Cigar Management System but adapted for tobacco-specific needs.

### **Architecture**
```
Local Development                    Production Server
├── Ruby 3.3+                       ├── /var/www/tobacco/ (Rails app)
├── Rails 7.2.2                     ├── tobacco.service (systemd)
├── PostgreSQL                       └── Nginx reverse proxy
├── RSpec tests                      └── tobacco.remoteds.us
└── Local development server
```

### **Key Features**
- CRUD operations for tobacco products and storage
- Weight-based tracking (ounces)
- Tobacco type classification (Loose Leaf, Flake, etc.)
- JSON API for Home Assistant integration
- Modern Bootstrap UI with responsive design

---

## 🚀 Prerequisites

### **Development Environment**
```bash
# Ruby and Rails versions
ruby --version    # Should be 3.3+
rails --version   # Should be 7.2.2

# Required gems
bundle install

# Database setup
rails db:create
rails db:migrate
rails db:seed
```

### **System Requirements**
- Ubuntu 25.04 LTS server
- Ruby 3.3+ with Rails 7.2.2
- PostgreSQL database
- Nginx web server
- SSL certificate (Let's Encrypt)

---

## 💻 Local Development

### **Setup Instructions**
```bash
cd /Users/bpauley/Projects/mangement-systems/tobacco-management-system

# Install dependencies
bundle install

# Database setup
rails db:create db:migrate db:seed

# Start development server
rails server

# Run tests
bundle exec rspec
```

### **Testing Requirements**
```bash
# Run all tests
bundle exec rspec

# Run specific test files
bundle exec rspec spec/models/
bundle exec rspec spec/controllers/
bundle exec rspec/spec/api/

# Test coverage
bundle exec rspec --format documentation
```

### **Pre-Deployment Checklist**
- [ ] All RSpec tests passing
- [ ] Website loads correctly locally
- [ ] Manual testing of CRUD operations
- [ ] API endpoints functional
- [ ] No hardcoded credentials
- [ ] Code committed to Git

---

## 🚀 Deployment Process

### **Method 1: Full Deployment**
```bash
cd /Users/bpauley/Projects/mangement-systems/tobacco-management-system

# 1. Commit and push changes
git add -A
git commit -m "Deployment description"
git push origin main

# 2. Deploy using hosting management system
cd ../hosting-management-system
python manager.py deploy --app tobacco

# 3. Deploy SSL certificate
python manager.py certbot-install
python manager.py certbot-issue --app tobacco --prod
```

### **Method 2: Code-Only Updates**
```bash
# When only code changes, no database migrations
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system
python manager.py deploy --app tobacco --skip-migrations
```

### **Method 3: Database Migrations**
```bash
# When database schema changes
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system
python manager.py deploy --app tobacco --migrate-only
```

---

## 🗄️ Database Management

### **Database Configuration**
```bash
# Production database
tobacco_mangement_sytem_production

# Connection via environment variables
DATABASE_URL=postgresql://user:password@localhost/tobacco_mangement_sytem_production
```

### **Migration Procedures**
```bash
# Run migrations on production
python manager.py deploy --app tobacco --migrate

# Rollback migrations if needed
python manager.py rollback --app tobacco
```

### **Backup and Restore**
```bash
# Create database backup
python manager.py backup --app tobacco

# Restore from backup
python manager.py restore --app tobacco --backup-path /path/to/backup
```

---

## 🔐 SSL Configuration

### **Let's Encrypt Setup**
```bash
# Install SSL certificate
python manager.py certbot-issue --app tobacco --prod

# Verify SSL certificate
curl -I https://tobacco.remoteds.us

# Check certificate details
echo | openssl s_client -connect tobacco.remoteds.us:443 2>/dev/null | openssl x509 -noout -dates
```

### **Nginx Configuration**
```nginx
# /etc/nginx/sites-available/tobacco.remoteds.us
server {
    listen 443 ssl;
    server_name tobacco.remoteds.us;
    
    ssl_certificate /etc/letsencrypt/live/tobacco.remoteds.us/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tobacco.remoteds.us/privkey.pem;
    
    root /var/www/tobacco/public;
    
    location / {
        try_files $uri @puma;
    }
    
    location @puma {
        proxy_pass http://127.0.0.1:3002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔌 API Endpoints

### **Public Inventory API**
- **Endpoint**: `GET https://tobacco.remoteds.us/api/inventory/:token`
- **Purpose**: Home Assistant integration
- **Authentication**: Token-based
- **Format**:
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

### **Internal API Endpoints**
- `GET /api/tobaccos` - List all tobacco products
- `POST /api/tobaccos` - Create new tobacco product
- `PUT /api/tobaccos/:id` - Update tobacco product
- `DELETE /api/tobaccos/:id` - Delete tobacco product
- `GET /api/tobacco_storages` - List all storage units
- `POST /api/tobacco_storages` - Create new storage unit

---

## 🔧 Service Management

### **Systemd Service**
```bash
# Service name: tobacco.service
# Location: /etc/systemd/system/tobacco.service

# Check service status
ssh root@asterra.remoteds.us "systemctl status tobacco --no-pager"

# Restart service
ssh root@asterra.remoteds.us "systemctl restart tobacco"

# View logs
ssh root@asterra.remoteds.us "journalctl -u tobacco -n 50 --no-pager"
```

### **Puma Configuration**
```ruby
# config/puma.rb
threads_count = ENV.fetch("RAILS_MAX_THREADS") { 5 }
threads threads_count, threads_count
port        ENV.fetch("PORT") { 3002 }
environment ENV.fetch("RAILS_ENV") { "production" }
pidfile ENV.fetch("PIDFILE") { "tmp/pids/server.pid" }
```

---

## 🧪 Verification Checklist

### **Post-Deployment Verification**
- [ ] Service status: `active (running)`
- [ ] HTTPS accessible: `https://tobacco.remoteds.us`
- [ ] Login page functional
- [ ] Dashboard loads correctly
- [ ] CRUD operations working
- [ ] API endpoints responding
- [ ] Weight tracking functional
- [ ] Mobile responsive design

### **Security Verification**
- [ ] HTTPS redirect working
- [ ] SSL certificate valid
- [ ] No sensitive data exposed
- [ ] Authentication required for admin areas
- [ ] Database credentials secure

---

## 🚨 Troubleshooting

### **Common Issues**

#### **Service Won't Start**
```bash
# Check service logs
ssh root@asterra.remoteds.us "journalctl -u tobacco -n 20 --no-pager"

# Check Ruby/Rails versions
ssh root@asterra.remoteds.us "cd /var/www/tobacco && ruby --version && rails --version"

# Verify database connection
ssh root@asterra.remoteds.us "cd /var/www/tobacco && rails db:migrate:status"
```

#### **Database Connection Errors**
```bash
# Check PostgreSQL status
ssh root@asterra.remoteds.us "systemctl status postgresql"

# Test database connection
ssh root@asterra.remoteds.us "sudo -u postgres psql -l"

# Check environment variables
ssh root@asterra.remoteds.us "cat /var/www/tobacco/.env | grep DATABASE"
```

#### **Asset Compilation Issues**
```bash
# Precompile assets manually
ssh root@asterra.remoteds.us "cd /var/www/tobacco && RAILS_ENV=production rails assets:precompile"

# Clear cache
ssh root@asterra.remoteds.us "cd /var/www/tobacco && rails tmp:clear"
```

---

## 🔄 Maintenance Procedures

### **Regular Maintenance**
```bash
# Update Ruby gems
ssh root@asterra.remoteds.us "cd /var/www/tobacco && bundle update"

# Clean old logs
ssh root@asterra.remoteds.us "cd /var/www/tobacco && rails log:clear"

# Database maintenance
ssh root@asterra.remoteds.us "cd /var/www/tobacco && rails db:migrate"
```

### **Performance Monitoring**
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://tobacco.remoteds.us/

# Monitor resource usage
ssh root@asterra.remoteds.us "ps aux | grep puma"
ssh root@asterra.remoteds.us "free -h"
```

---

## 📊 Development Workflow

### **Feature Development**
1. Create feature branch
2. Write code and tests
3. Run `bundle exec rspec`
4. Test locally with `rails server`
5. Commit and push to main
6. Deploy via hosting management system

### **Code Quality Standards**
- All methods must have documentation
- RSpec tests for all models and controllers
- No hardcoded credentials
- Follow Ruby style guide
- Use meaningful variable names

---

## 📋 Domain-Specific Business Logic

### **Weight-Based Tracking**
- Track tobacco by weight in ounces (not individual units)
- Support partial usage with weight deduction
- Visual storage capacity indicators

### **Tobacco Type Classification**
- `type` field stores tobacco form (Loose Leaf, Flake, etc.)
- Supports empty type values for unclassified tobacco
- Useful for filtering and categorization in UI

### **Storage Management**
- Multiple storage units (tins, bags, bulk containers)
- Capacity tracking by weight/volume
- Transfer between storage units

---

## ✅ Deployment Success Criteria

### **Must Pass All Checks**
- [ ] All RSpec tests passing locally
- [ ] Website loading correctly locally
- [ ] Service running without errors
- [ ] HTTPS accessible with valid certificate
- [ ] All CRUD operations functional
- [ ] Weight tracking working correctly
- [ ] API endpoints responding correctly
- [ ] Mobile design responsive
- [ ] No security vulnerabilities

---

**Document Maintenance**: Update when deployment procedures change. All developers must re-read when updated.

**Last Updated**: October 29, 2025  
**Next Review**: January 29, 2026

---

## 🔗 Related Documentation

- **[agents.md](agents.md)** - Master development rules
- **[HOSTING_DEPLOYMENT_GUIDE.md](HOSTING_DEPLOYMENT_GUIDE.md)** - Hosting system deployment
- **[CIGAR_DEPLOYMENT_GUIDE.md](CIGAR_DEPLOYMENT_GUIDE.md)** - Cigar app deployment
- **[../README.md](../README.md)** - System overview
