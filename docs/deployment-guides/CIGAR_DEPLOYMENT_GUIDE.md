# Cigar Management System Deployment Guide

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

The Cigar Management System is a Ruby on Rails 7.2.2 application for tracking cigar inventory across multiple humidors with OCR support.

### **Architecture**
```
Local Development                    Production Server
├── Ruby 3.3+                       ├── /var/www/cigar/ (Rails app)
├── Rails 7.2.2                     ├── cigar.service (systemd)
├── PostgreSQL                       └── Nginx reverse proxy
├── RSpec tests                      └── cigars.remoteds.us
└── Local development server
```

### **Key Features**
- CRUD operations for cigars, humidors, and brands
- OCR integration for cigar band scanning
- Capacity tracking and management
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
cd /Users/bpauley/Projects/mangement-systems/cigar-management-system

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
cd /Users/bpauley/Projects/mangement-systems/cigar-management-system

# 1. Commit and push changes
git add -A
git commit -m "Deployment description"
git push origin main

# 2. Deploy using hosting management system
cd ../hosting-management-system
python manager.py deploy --app cigar

# 3. Deploy SSL certificate
python manager.py certbot-install
python manager.py certbot-issue --app cigar --prod
```

### **Method 2: Code-Only Updates**
```bash
# When only code changes, no database migrations
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system
python manager.py deploy --app cigar --skip-migrations
```

### **Method 3: Database Migrations**
```bash
# When database schema changes
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system
python manager.py deploy --app cigar --migrate-only
```

---

## 🗄️ Database Management

### **Database Configuration**
```bash
# Production database
cigar_mangement_sytem_production

# Connection via environment variables
DATABASE_URL=postgresql://user:password@localhost/cigar_mangement_sytem_production
```

### **Migration Procedures**
```bash
# Run migrations on production
python manager.py deploy --app cigar --migrate

# Rollback migrations if needed
python manager.py rollback --app cigar
```

### **Backup and Restore**
```bash
# Create database backup
python manager.py backup --app cigar

# Restore from backup
python manager.py restore --app cigar --backup-path /path/to/backup
```

---

## 🔐 SSL Configuration

### **Let's Encrypt Setup**
```bash
# Install SSL certificate
python manager.py certbot-issue --app cigar --prod

# Verify SSL certificate
curl -I https://cigars.remoteds.us

# Check certificate details
echo | openssl s_client -connect cigars.remoteds.us:443 2>/dev/null | openssl x509 -noout -dates
```

### **Nginx Configuration**
```nginx
# /etc/nginx/sites-available/cigars.remoteds.us
server {
    listen 443 ssl;
    server_name cigars.remoteds.us;
    
    ssl_certificate /etc/letsencrypt/live/cigars.remoteds.us/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cigars.remoteds.us/privkey.pem;
    
    root /var/www/cigar/public;
    
    location / {
        try_files $uri @puma;
    }
    
    location @puma {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔌 API Endpoints

### **Public Inventory API**
- **Endpoint**: `GET https://cigars.remoteds.us/api/inventory/:token`
- **Purpose**: Home Assistant integration
- **Authentication**: Token-based
- **Format**:
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

### **Internal API Endpoints**
- `GET /api/cigars` - List all cigars
- `POST /api/cigars` - Create new cigar
- `PUT /api/cigars/:id` - Update cigar
- `DELETE /api/cigars/:id` - Delete cigar
- `GET /api/humidors` - List all humidors
- `POST /api/scan` - OCR scan processing

---

## 🔧 Service Management

### **Systemd Service**
```bash
# Service name: cigar.service
# Location: /etc/systemd/system/cigar.service

# Check service status
ssh root@asterra.remoteds.us "systemctl status cigar --no-pager"

# Restart service
ssh root@asterra.remoteds.us "systemctl restart cigar"

# View logs
ssh root@asterra.remoteds.us "journalctl -u cigar -n 50 --no-pager"
```

### **Puma Configuration**
```ruby
# config/puma.rb
threads_count = ENV.fetch("RAILS_MAX_THREADS") { 5 }
threads threads_count, threads_count
port        ENV.fetch("PORT") { 3001 }
environment ENV.fetch("RAILS_ENV") { "production" }
pidfile ENV.fetch("PIDFILE") { "tmp/pids/server.pid" }
```

---

## 🧪 Verification Checklist

### **Post-Deployment Verification**
- [ ] Service status: `active (running)`
- [ ] HTTPS accessible: `https://cigars.remoteds.us`
- [ ] Login page functional
- [ ] Dashboard loads correctly
- [ ] CRUD operations working
- [ ] API endpoints responding
- [ ] OCR functionality (if applicable)
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
ssh root@asterra.remoteds.us "journalctl -u cigar -n 20 --no-pager"

# Check Ruby/Rails versions
ssh root@asterra.remoteds.us "cd /var/www/cigar && ruby --version && rails --version"

# Verify database connection
ssh root@asterra.remoteds.us "cd /var/www/cigar && rails db:migrate:status"
```

#### **Database Connection Errors**
```bash
# Check PostgreSQL status
ssh root@asterra.remoteds.us "systemctl status postgresql"

# Test database connection
ssh root@asterra.remoteds.us "sudo -u postgres psql -l"

# Check environment variables
ssh root@asterra.remoteds.us "cat /var/www/cigar/.env | grep DATABASE"
```

#### **Asset Compilation Issues**
```bash
# Precompile assets manually
ssh root@asterra.remoteds.us "cd /var/www/cigar && RAILS_ENV=production rails assets:precompile"

# Clear cache
ssh root@asterra.remoteds.us "cd /var/www/cigar && rails tmp:clear"
```

---

## 🔄 Maintenance Procedures

### **Regular Maintenance**
```bash
# Update Ruby gems
ssh root@asterra.remoteds.us "cd /var/www/cigar && bundle update"

# Clean old logs
ssh root@asterra.remoteds.us "cd /var/www/cigar && rails log:clear"

# Database maintenance
ssh root@asterra.remoteds.us "cd /var/www/cigar && rails db:migrate"
```

### **Performance Monitoring**
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://cigars.remoteds.us/

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

## ✅ Deployment Success Criteria

### **Must Pass All Checks**
- [ ] All RSpec tests passing locally
- [ ] Website loading correctly locally
- [ ] Service running without errors
- [ ] HTTPS accessible with valid certificate
- [ ] All CRUD operations functional
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
- **[TOBACCO_DEPLOYMENT_GUIDE.md](TOBACCO_DEPLOYMENT_GUIDE.md)** - Tobacco app deployment
- **[../README.md](../README.md)** - System overview
