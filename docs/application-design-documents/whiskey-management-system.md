# Whiskey Management System - Complete Application Design

**Last Updated**: November 1, 2025  
**Version**: 1.1  
**Status**: ✅ **ACTIVE** - Production deployed at https://whiskey.remoteds.us

---

## 📋 Table of Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Database Schema](#database-schema)
- [Domain Model](#domain-model)
- ✨ [Features](#features)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Dependencies](#dependencies)
- [Testing](#testing)
- [Related Documentation](#related-documentation)

---

## 🎯 Overview

The Whiskey Management System is a Ruby on Rails 7.2.2 application designed to help enthusiasts manage their whiskey collection with detailed tracking of bottles, brands, locations, and whiskey characteristics.

### **Purpose**
Track whiskey collection with features for:
- Whiskey bottle management with detailed specifications
- ABV, proof, and age tracking
- Mash bill composition documentation
- Brand and location management
- Comprehensive whiskey type taxonomy
- Image storage for bottles

### **Production Information**
- **URL**: https://whiskey.remoteds.us
- **Port**: 3003
- **Service**: `puma-whiskey.service`
- **Document Root**: `/var/www/whiskey/`
- **Database**: `whiskey_management_system_production` (PostgreSQL)

---

## 🛠️ Technology Stack

### **Core Framework**
- **Language**: Ruby 3.3+
- **Framework**: Rails 7.2.2
- **Database**: 
  - Development/Test: SQLite3
  - Production: PostgreSQL
- **App Server**: Puma (4 workers)
- **Web Server**: Nginx (reverse proxy)
- **Authentication**: Devise

### **Frontend**
- **UI Framework**: Bootstrap 5 (amber/gold color scheme)
- **JavaScript**: Hotwire (Turbo + Stimulus)
- **Icons**: Bootstrap Icons
- **Asset Pipeline**: cssbundling-rails with Sass

### **Testing**
- **Test Framework**: RSpec 6.1
- **Factories**: FactoryBot
- **Fake Data**: Faker
- **Browser Testing**: Capybara
- **Matchers**: Shoulda Matchers

### **Storage**
- **File Storage**: ActiveStorage
- **Image Variants**: Bottle images with thumbnails

---

## 🗄️ Database Schema

### 1. **Whiskey Collection Management**
- Track individual bottles with detailed specifications
- Record ABV (Alcohol By Volume), proof, and age
- Document mash bill composition (grain ratios)
- Upload bottle images via ActiveStorage
- Monitor quantity in possession

### 2. **Whiskey Types**
Comprehensive categorization including:
- **Bourbon**: American whiskey (≥51% corn), aged in new charred oak
- **Rye Whiskey**: Made from ≥51% rye, spicier profile
- **Wheat Whiskey**: Made from ≥51% wheat, softer character
- **Scotch**: Scottish whisky, malted barley, aged ≥3 years
- **Irish Whiskey**: Triple-distilled Irish style
- **Tennessee Whiskey**: Bourbon-style with charcoal filtering
- **Canadian Whisky**: Light-bodied grain blends
- **Japanese Whisky**: Precision-crafted, influenced by Scotch
- **Single Malt**: 100% malted barley from one distillery
- **Blended Whiskey**: Mixed malt and grain whiskeys

### 3. **Brand Management**
- Brand profiles with country of origin
- Website URLs for reference
- Detailed descriptions
- Associated whiskey listings

### 4. **Location Tracking**
- Multiple storage locations (Home Bar, Cabinet, Cellar)
- Address and description for each location
- Inventory organization by location

---

## 🏗️ Domain Model

### **Core Relationships**
```
User (Devise)
  └── Manages all whiskey data

Location
  └── has_many :whiskeys

Brand
  ├── has_many :whiskeys
  └── attributes: name, description, website_url, country

WhiskeyType
  ├── has_many :whiskeys
  └── attributes: name, description

Whiskey
  ├── belongs_to :brand
  ├── belongs_to :whiskey_type
  ├── belongs_to :location (optional)
  ├── has_one_attached :bottle_image
  └── attributes: name, description, mash_bill, abv, proof, age, quantity
```

### **Database Schema (Production)**
- **Users**: Devise authentication
- **Locations**: name, description, address
- **Brands**: name, description, website_url, country
- **WhiskeyTypes**: name, description
- **Whiskeys**: name, description, mash_bill, abv, proof, age, quantity
- **Active Storage**: bottle_image attachments

---

## 🛠️ Technology Stack (Detailed)
- **Framework**: Rails 7.2.2
- **Authentication**: Devise
- **Frontend**: Bootstrap 5, Hotwire (Turbo + Stimulus)
- **Database**: 
  - Development/Test: SQLite3
  - Production: PostgreSQL (whiskey_management_system_production)
- **Image Storage**: ActiveStorage with variants
- **Testing**: RSpec 6.1, FactoryBot, Faker, Capybara, Shoulda Matchers
- **Asset Pipeline**: cssbundling-rails with Sass, Bootstrap, Bootstrap Icons

### Deployment
- **Local**: Port 3003
- **Production**: https://whiskey.remoteds.us
- **Server**: Puma (4 workers)
- **Reverse Proxy**: Nginx with SSL (Let's Encrypt)
- **Service**: systemd (puma-whiskey.service)

## Key Differentiators from Cigar/Tobacco Apps
1. **ABV & Proof Tracking**: Specific to spirits
2. **Mash Bill Documentation**: Grain composition unique to whiskey
3. **Age Statements**: Critical for whiskey valuation
4. **Whiskey Type Taxonomy**: More granular than cigar types
5. **No Humidor Concept**: Direct location-to-bottle relationship

## User Credentials
- **Production**: brian@thinkcreatebuildit.com
- **Development**: admin_whiskey@localhost
- **Password**: (stored in .secrets.json)

## API Endpoints
- `POST /users/sign_in` - Authentication
- `GET /whiskeys` - List all whiskeys
- `GET /whiskeys/:id` - Show whiskey details
- `GET /brands` - List all brands
- `GET /whiskey_types` - List all whiskey types
- `GET /locations` - List all locations

## Seed Data
- 10 whiskey types with detailed descriptions
- 8 premium brands (Buffalo Trace, Maker's Mark, Wild Turkey, Glenfiddich, Jameson, Jack Daniel's, Lagavulin, Yamazaki)
- 3 locations (Home Bar, Whiskey Cabinet, Cellar Storage)
- 6 sample whiskeys with complete specifications

## Testing
- **Test Suite**: 25 RSpec examples
- **Coverage**: Model validations, associations, factories
- **Status**: ✅ All tests passing

## Color Scheme
Different from cigar (brown/tobacco) and tobacco (green) apps, whiskey uses amber/gold tones representing whiskey color.

---

## 🚀 Deployment

### **Production Configuration**
- **Server**: Ubuntu 25.04 LTS
- **Location**: `/var/www/whiskey/`
- **Service**: `puma-whiskey.service` (systemd)
- **Port**: 3003 (internal)
- **Public URL**: https://whiskey.remoteds.us
- **SSL**: Let's Encrypt certificate
- **Nginx**: Reverse proxy on port 443

### **Deployment Method**
```bash
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system

# Full deployment
python manager.py deploy --app whiskey

# Includes:
# - Git pull from repository
# - bundle install
# - rails db:migrate
# - rails assets:precompile
# - Systemd service restart
# - Nginx configuration
```

### **Nginx Configuration**
```nginx
server {
    listen 443 ssl;
    server_name whiskey.remoteds.us;
    
    ssl_certificate /etc/letsencrypt/live/whiskey.remoteds.us/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/whiskey.remoteds.us/privkey.pem;
    
    root /var/www/whiskey/public;
    
    location / {
        try_files $uri @puma;
    }
    
    location @puma {
        proxy_pass http://unix:/var/www/whiskey/tmp/sockets/puma.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔐 Environment Variables

### **Production Environment (.env)**
Deployed via `deploy-secure-sync.py` to systemd service file:

```ini
[Service]
Environment=RAILS_ENV=production
Environment=SECRET_KEY_BASE=<from-database>
Environment=WHISKEY_DATABASE_PASSWORD=<from-database>
Environment=WHISKEY_API_TOKEN=<from-database>
```

**CRITICAL**: Secrets stored in `hosting_production` PostgreSQL database, NOT in .env files.

### **Required Variables**
- `RAILS_ENV`: production
- `SECRET_KEY_BASE`: Rails secret key
- `WHISKEY_DATABASE_PASSWORD`: PostgreSQL password
- `WHISKEY_API_TOKEN`: API authentication token (if API implemented)

---

## 📦 Dependencies

### **Gemfile**
```ruby
# Core
gem 'rails', '~> 7.2.2'
gem 'pg', '~> 1.1'  # Production
gem 'sqlite3', '~> 1.4'  # Development/Test
gem 'puma', '~> 6.0'

# Authentication
gem 'devise'

# Frontend
gem 'cssbundling-rails'
gem 'jsbundling-rails'
gem 'turbo-rails'
gem 'stimulus-rails'

# Image Storage
gem 'image_processing', '~> 1.2'

# Testing
group :development, :test do
  gem 'rspec-rails', '~> 6.1'
  gem 'factory_bot_rails'
  gem 'faker'
end

group :test do
  gem 'capybara'
  gem 'shoulda-matchers'
end
```

### **Installation**
```bash
bundle install
npm install  # For JavaScript dependencies
```

---

## 📚 Related Documentation

- **[ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)** - System architecture
- **[../agents.md](../agents.md)** - Master development rules
- **[SECURITY_GUIDE.md](SECURITY_GUIDE.md)** - Security protocols
- **[README.md](README.md)** - Documentation index
- **[CIGAR_DEPLOYMENT_GUIDE.md](CIGAR_DEPLOYMENT_GUIDE.md)** - Similar deployment patterns
- **[TOBACCO_DEPLOYMENT_GUIDE.md](TOBACCO_DEPLOYMENT_GUIDE.md)** - Similar deployment patterns

---

**This document serves as the complete design specification for the Whiskey Management System. All development, deployment, and documentation work should reference this as the single source of truth for application design.**

**Last Updated**: November 1, 2025  
**Maintained by**: Development Team + AI Agents
