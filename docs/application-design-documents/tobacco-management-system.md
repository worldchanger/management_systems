# Tobacco Management System - Complete Application Design

**Last Updated**: November 1, 2025  
**Version**: 1.0  
**Status**: ✅ **ACTIVE** - Production deployed at https://tobacco.remoteds.us

---

## 📋 Table of Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Database Schema](#database-schema)
- [Domain Model](#domain-model)
- [Business Logic](#business-logic)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Controllers](#controllers)
- [Views](#views)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Dependencies](#dependencies)
- [Testing](#testing)
- [Related Documentation](#related-documentation)

---

## 🎯 Overview

The Tobacco Management System is a web-based inventory tracker for tobacco products and storage management, analogous to the Cigar Management System but adapted for tobacco-specific needs.

### **Purpose**
Track tobacco inventory with features for:
- Multiple storage unit management
- Weight-based tracking (ounces)
- Tobacco type classification (Loose Leaf, Flake, etc.)
- Image management for tin/bag identification
- JSON API for Home Assistant integration
- Dashboard views with totals

### **Production Information**
- **URL**: https://tobacco.remoteds.us
- **Port**: 3002
- **Service**: `puma-tobacco.service`
- **Document Root**: `/var/www/tobacco/`
- **Database**: `tobacco_mangement_sytem_production` (PostgreSQL)

---

## 🛠️ Technology Stack

### **Core Framework**
- **Language**: Ruby 3.3+
- **Framework**: Rails 7.2.2
- **Database**: PostgreSQL
- **App Server**: Puma (4 workers)
- **Web Server**: Nginx (reverse proxy)
- **Authentication**: Devise

### **Frontend**
- **UI Framework**: Bootstrap 5 (green color scheme)
- **JavaScript**: Hotwire (Turbo + Stimulus)
- **Icons**: Bootstrap Icons
- **Asset Pipeline**: cssbundling-rails with Sass

### **Image Storage**
- **Storage**: ActiveStorage
- **Purpose**: Upload tobacco tin/bag images for reference
- **Variants**: Image thumbnails and previews

### **Testing**
- **Test Framework**: RSpec 6.1
- **Factories**: FactoryBot
- **Fake Data**: Faker
- **Browser Testing**: Capybara
- **Matchers**: Shoulda Matchers

---

## 🗄️ Database Schema

### **Tables**

#### **tobacco_storages**
```ruby
create_table "tobacco_storages" do |t|
  t.string "name", null: false
  t.string "location"
  t.timestamps
  
  t.index ["name"], unique: true
end
```

#### **tobaccos**
```ruby
create_table "tobaccos" do |t|
  t.string "tobacco_name", null: false
  t.string "type"  # Loose Leaf, Flake, etc.
  t.bigint "tobacco_storage_id", null: false
  t.decimal "qty_weight", precision: 8, scale: 2, default: 0.0  # in ounces
  t.timestamps
  
  t.index ["tobacco_storage_id"]
  t.index ["tobacco_name", "tobacco_storage_id"], unique: true
end
```

#### **active_storage_blobs** & **active_storage_attachments**
Rails ActiveStorage tables for tobacco image storage.

---

## 🏗️ Domain Model

### **Core Relationships**

```
TobaccoStorage
  └── has_many :tobaccos
  
Tobacco
  ├── belongs_to :tobacco_storage
  └── has_one_attached :tobacco_image
```

### **Model Specifications**

#### **TobaccoStorage Model**
```ruby
class TobaccoStorage < ApplicationRecord
  has_many :tobaccos, dependent: :destroy
  has_one_attached :image
  
  validates :name, presence: true, uniqueness: true
  validates :location, allow_blank: true
  
  def total_weight
    tobaccos.sum(:qty_weight)
  end
  
  def tobacco_count
    tobaccos.count
  end
  
  def tobacco_types
    tobaccos.pluck(:type).compact.uniq
  end
end
```

#### **Tobacco Model**
```ruby
class Tobacco < ApplicationRecord
  belongs_to :tobacco_storage
  has_one_attached :tobacco_image
  
  validates :tobacco_name, presence: true
  validates :tobacco_storage_id, presence: true
  validates :qty_weight, numericality: { greater_than_or_equal_to: 0 }
  validates :tobacco_name, uniqueness: { scope: :tobacco_storage_id }
  validates :type, allow_blank: true
  
  # Tobacco types enum (optional)
  TOBACCO_TYPES = [
    'Loose Leaf',
    'Flake',
    'Plug',
    'Cake',
    'Twist',
    'Rope',
    'Shag'
  ].freeze
  
  def add_weight(ounces)
    increment!(:qty_weight, ounces)
  end
  
  def remove_weight(ounces)
    new_weight = qty_weight - ounces
    if new_weight <= 0
      destroy
    else
      update!(qty_weight: new_weight)
    end
  end
  
  def transfer_weight(to_storage, ounces)
    raise ArgumentError if ounces > qty_weight
    
    transaction do
      remove_weight(ounces)
      
      target = Tobacco.find_or_initialize_by(
        tobacco_storage: to_storage,
        tobacco_name: tobacco_name,
        type: type
      )
      target.qty_weight ||= 0.0
      target.add_weight(ounces)
    end
  end
end
```

---

## 💼 Business Logic

### **Weight-Based Tracking**
- Track tobacco by weight in ounces (not individual units)
- Support partial usage with weight deduction
- Decimal precision for accurate measurements
- Auto-delete tobacco records when weight reaches zero

### **Tobacco Type Classification**
- `type` field stores tobacco form (Loose Leaf, Flake, etc.)
- Supports empty type values for unclassified tobacco
- Useful for filtering and categorization in UI
- No OCR integration (manual data entry)

### **Storage Management**
- Multiple storage units (tins, bags, bulk containers)
- Transfer tobacco between storage units
- Track total weight per storage unit
- Visual indicators for storage contents

### **Image Management**
- Upload tobacco tin/bag images for reference
- No OCR processing (unlike cigar app)
- Image gallery for storage identification
- ActiveStorage for file management

---

## ✨ Features

### **1. CRUD Operations**
- **Tobacco Storages**: Create, read, update, delete storage units
- **Tobaccos**: Track individual tobacco products with weight
- **Inventory**: Add/remove tobacco by weight

### **2. Weight Tracking**
- Decimal-based weight in ounces
- Partial weight deductions
- Weight transfer between storages
- Total weight calculations

### **3. Type Classification**
- Tobacco type dropdown (Loose Leaf, Flake, etc.)
- Type-based filtering
- Optional type field (can be blank)
- Custom types supported

### **4. Dashboard**
- Total tobacco count
- Total weight across all storage
- Storage breakdown
- Quick access to resources

### **5. JSON API**
- Public inventory endpoint with token auth
- Home Assistant integration format
- Grouped by storage unit with details

---

## 🔌 API Endpoints

### **Public Inventory API**

#### **GET /api/inventory/:token**
Returns JSON inventory for Home Assistant integration.

**Authentication**: Token-based (UUID in URL)  
**Format**:
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

**Security**: 
- UUID token with expiration tracking
- Rotation capability
- Read-only access
- Same token mechanism as cigar app

### **Internal API Endpoints**

#### **Tobaccos**
- `GET /api/tobaccos` - List all tobaccos with weights
- `GET /api/tobaccos/:id` - Show tobacco details
- `POST /api/tobaccos` - Create new tobacco
- `PUT /api/tobaccos/:id` - Update tobacco
- `DELETE /api/tobaccos/:id` - Delete tobacco

#### **Tobacco Storages**
- `GET /api/tobacco_storages` - List all storage units
- `GET /api/tobacco_storages/:id` - Show storage with contents
- `POST /api/tobacco_storages` - Create new storage
- `PUT /api/tobacco_storages/:id` - Update storage
- `DELETE /api/tobacco_storages/:id` - Delete storage (if empty)

---

## 🎮 Controllers

### **TobaccoStoragesController** (RESTful)
```ruby
# Actions: index, show, new, create, edit, update, destroy
# Before filters: authenticate_user!
# Strong params: :name, :location, :image
```
- **Index**: List all storage units with total weight and count
- **Show**: Details + list of tobaccos
- **New/Create**: Form for name/location
- **Edit/Update**: Same form
- **Destroy**: Delete if empty

### **TobaccosController** (RESTful)
```ruby
# Actions: index, show, new, create, edit, update, destroy
# Before filters: authenticate_user!
# Strong params: :tobacco_name, :type, :tobacco_storage_id, :qty_weight, :tobacco_image
```
- **Index**: List all with weight and storage location
- **Show**: Details including image
- **New/Create**: Form for name/type/storage/weight
- **Edit/Update**: Same form
- **Destroy**: Delete tobacco

### **Api::InventoryController** (Namespaced API)
```ruby
# Actions: index
# Before filters: verify_api_token
# No params (token in URL)
```
- **Index**: Return JSON grouped by storage unit
- Secure with API key param (check in before_action)

### **HomeController** (Dashboard)
```ruby
# Actions: index
# Before filters: authenticate_user!
```
- **Index**: Aggregate view with totals, weights, storage breakdown

---

## 🎨 Views

### **Layout**
- `application.html.erb` with Bootstrap 5 (green theme)
- Navigation bar with app links
- Flash message display
- Responsive design

### **Tobacco Storages Views**
- `index.html.erb`: Table with name, location, total weight, tobacco count
- `show.html.erb`: Details + tobaccos table with add/remove weight
- `_form.html.erb`: Form with name, location, image upload

### **Tobaccos Views**
- `index.html.erb`: Table with name, type, storage, weight
- `show.html.erb`: Details including image and storage info
- `_form.html.erb`: Form with name, type dropdown, storage dropdown, weight input, image upload

### **Dashboard (home/index.html.erb)**
- **Totals Section**: List of tobaccos with weights
- **Storage Section**: List of storage units with contents
- **Quick Actions**: Links to create storage/tobaccos

### **Partials**
- `_tobacco.html.erb`: Reusable tobacco display
- `_storage.html.erb`: Reusable storage card
- `_weight_display.html.erb`: Formatted weight display

---

## 🚀 Deployment

### **Production Configuration**
- **Server**: Ubuntu 25.04 LTS
- **Location**: `/var/www/tobacco/`
- **Service**: `puma-tobacco.service` (systemd)
- **Port**: 3002 (internal)
- **Public URL**: https://tobacco.remoteds.us
- **SSL**: Let's Encrypt certificate
- **Nginx**: Reverse proxy on port 443

### **Deployment Method**
```bash
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system

# Full deployment
python manager.py deploy --app tobacco

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
    server_name tobacco.remoteds.us;
    
    ssl_certificate /etc/letsencrypt/live/tobacco.remoteds.us/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tobacco.remoteds.us/privkey.pem;
    
    root /var/www/tobacco/public;
    
    location / {
        try_files $uri @puma;
    }
    
    location @puma {
        proxy_pass http://unix:/var/www/tobacco/tmp/sockets/puma.sock;
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
Environment=TOBACCO_DATABASE_PASSWORD=<from-database>
Environment=TOBACCO_API_TOKEN=<from-database>
```

**CRITICAL**: Secrets stored in `hosting_production` PostgreSQL database, NOT in .env files.

### **Required Variables**
- `RAILS_ENV`: production
- `SECRET_KEY_BASE`: Rails secret key
- `TOBACCO_DATABASE_PASSWORD`: PostgreSQL password
- `TOBACCO_API_TOKEN`: API authentication token

---

## 📦 Dependencies

### **Gemfile**
```ruby
# Core
gem 'rails', '~> 7.2.2'
gem 'pg', '~> 1.1'
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

## 🧪 Testing

### **Test Coverage**
- **Models**: Validations, associations, weight methods
- **Controllers**: CRUD operations, authentication
- **API**: JSON format, authentication, error handling
- **Integration**: Full workflows (add tobacco, weight tracking, etc.)

### **Running Tests**
```bash
# All tests
bundle exec rspec

# Specific test types
bundle exec rspec spec/models/
bundle exec rspec spec/controllers/
bundle exec rspec spec/requests/api/

# With documentation format
bundle exec rspec --format documentation

# Coverage report
bundle exec rspec --require rails_helper --format html --out coverage/index.html
```

### **Test Requirements**
- All models must have validation tests
- Weight tracking methods must be tested
- Controllers must test CRUD operations
- API endpoints must test JSON format
- Authentication must be tested
- Transfer operations must have integration tests

---

## 🔄 Key Differences from Cigar App

### **1. Weight vs. Quantity**
- Tobacco tracks weight in ounces (decimal)
- Cigar tracks quantity (integer)
- Support partial weight deductions

### **2. No OCR**
- Manual data entry only
- Image upload for reference, not processing
- Simpler workflow

### **3. Simpler Relationships**
- Two-level hierarchy: Storage → Tobacco
- No join table for quantities
- Direct belongs_to relationship

### **4. Type Classification**
- Tobacco type field (Loose Leaf, Flake, etc.)
- Cigars have ratings instead
- Both support optional classification

### **5. No Capacity Limits**
- Storage units don't have max capacity
- Cigar humidors do track capacity
- Focus on weight totals instead

---

## 📚 Related Documentation

- **[TOBACCO_DEPLOYMENT_GUIDE.md](TOBACCO_DEPLOYMENT_GUIDE.md)** - Deployment procedures
- **[ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)** - System architecture
- **[../agents.md](../agents.md)** - Master development rules
- **[SECURITY_GUIDE.md](SECURITY_GUIDE.md)** - Security protocols
- **[README.md](README.md)** - Documentation index

---

**This document serves as the complete design specification for the Tobacco Management System. All development, deployment, and documentation work should reference this as the single source of truth for application design.**

**Last Updated**: November 1, 2025  
**Maintained by**: Development Team + AI Agents
