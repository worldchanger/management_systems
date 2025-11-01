# Cigar Management System - Complete Application Design

**Last Updated**: November 1, 2025  
**Version**: 1.0  
**Status**: ✅ **ACTIVE** - Production deployed at https://cigars.remoteds.us

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
- [OCR Integration](#ocr-integration)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Dependencies](#dependencies)
- [Testing](#testing)
- [Related Documentation](#related-documentation)

---

## 🎯 Overview

The Cigar Management System is a web-based inventory tracker for cigars across multiple humidors with OCR support for cigar band scanning.

### **Purpose**
Track cigar inventory with features for:
- Multiple humidor management
- Brand and cigar cataloging
- Quantity tracking with capacity management
- OCR-based cigar band recognition
- JSON API for Home Assistant integration
- Aggregated dashboard views

### **Production Information**
- **URL**: https://cigars.remoteds.us
- **Port**: 3001
- **Service**: `puma-cigar.service`
- **Document Root**: `/var/www/cigar/`
- **Database**: `cigar_mangement_sytem_production` (PostgreSQL)

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
- **UI Framework**: Bootstrap 5
- **JavaScript**: Hotwire (Turbo + Stimulus)
- **Icons**: Bootstrap Icons
- **Asset Pipeline**: cssbundling-rails with Sass

### **Image Processing & OCR**
- **OCR Engine**: Tesseract
- **Gems**: 
  - `tesseract-ffi` - OCR integration
  - `rmagick` - Image manipulation
  - `fuzzy-string-match` - Fuzzy matching for brand/cigar recognition

### **Testing**
- **Test Framework**: RSpec 6.1
- **Factories**: FactoryBot
- **Fake Data**: Faker
- **Browser Testing**: Capybara
- **Matchers**: Shoulda Matchers

### **Storage**
- **File Storage**: ActiveStorage
- **Image Variants**: ActiveStorage transformations for OCR

---

## 🗄️ Database Schema

### **Tables**

#### **locations**
```ruby
create_table "locations" do |t|
  t.string "name", null: false
  t.string "address"
  t.string "city"
  t.string "state"
  t.string "zip"
  t.string "country"
  t.timestamps
  
  t.index ["name"], unique: true
end
```

#### **humidors**
```ruby
create_table "humidors" do |t|
  t.string "name", null: false
  t.bigint "location_id", null: false
  t.integer "max_qty", default: 0
  t.timestamps
  
  t.index ["location_id"]
  t.index ["name"], unique: true
end
```

#### **brands**
```ruby
create_table "brands" do |t|
  t.string "name", null: false
  t.string "website_url"
  t.timestamps
  
  t.index ["name"], unique: true
end
```

#### **cigars**
```ruby
create_table "cigars" do |t|
  t.string "cigar_name", null: false
  t.bigint "brand_id", null: false
  t.integer "rating", inclusion: { in: 1..5 }
  t.timestamps
  
  t.index ["brand_id"]
  t.index ["cigar_name", "brand_id"], unique: true
end
```

#### **humidor_cigars** (Join Table)
```ruby
create_table "humidor_cigars" do |t|
  t.bigint "humidor_id", null: false
  t.bigint "cigar_id", null: false
  t.integer "quantity", default: 0
  t.timestamps
  
  t.index ["humidor_id", "cigar_id"], unique: true
  t.index ["cigar_id"]
end
```

#### **active_storage_blobs** & **active_storage_attachments**
Rails ActiveStorage tables for OCR image storage.

---

## 🏗️ Domain Model

### **Core Relationships**

```
Location
  ├── has_many :humidors
  
Humidor
  ├── belongs_to :location
  ├── has_many :humidor_cigars
  ├── has_many :cigars, through: :humidor_cigars
  └── has_many :brands, through: :cigars
  
Brand
  └── has_many :cigars
  
Cigar
  ├── belongs_to :brand
  ├── has_many :humidor_cigars
  ├── has_many :humidors, through: :humidor_cigars
  └── has_one_attached :cigar_image (for OCR)
  
HumidorCigar (Join Model)
  ├── belongs_to :humidor
  ├── belongs_to :cigar
  └── [tracks quantity]
```

### **Model Specifications**

#### **Location Model**
```ruby
class Location < ApplicationRecord
  has_many :humidors, dependent: :destroy
  
  validates :name, presence: true, uniqueness: true
  validates :address, :city, :state, :zip, :country, allow_blank: true
end
```

#### **Humidor Model**
```ruby
class Humidor < ApplicationRecord
  belongs_to :location
  has_many :humidor_cigars, dependent: :destroy
  has_many :cigars, through: :humidor_cigars
  has_many :brands, through: :cigars
  has_one_attached :image
  
  validates :name, presence: true
  validates :location_id, presence: true
  validates :max_qty, numericality: { greater_than: 0 }
  
  def available_capacity
    max_qty - used_capacity
  end
  
  def used_capacity
    humidor_cigars.sum(:quantity)
  end
  
  def capacity_percentage
    return 0 if max_qty.zero?
    (used_capacity.to_f / max_qty * 100).round(1)
  end
end
```

#### **Brand Model**
```ruby
class Brand < ApplicationRecord
  has_many :cigars, dependent: :restrict_with_error
  
  validates :name, presence: true, uniqueness: true
  validates :website_url, format: URI::DEFAULT_PARSER.make_regexp(%w[http https]), allow_blank: true
end
```

#### **Cigar Model**
```ruby
class Cigar < ApplicationRecord
  belongs_to :brand
  has_many :humidor_cigars, dependent: :destroy
  has_many :humidors, through: :humidor_cigars
  has_one_attached :cigar_image
  
  validates :cigar_name, presence: true
  validates :brand_id, presence: true
  validates :rating, inclusion: { in: 1..5 }, allow_nil: true
  validates :cigar_name, uniqueness: { scope: :brand_id }
  
  def total_qty
    humidor_cigars.sum(:quantity)
  end
  
  def locations
    humidor_cigars.includes(:humidor).map do |hc|
      { humidor: hc.humidor.name, qty: hc.quantity }
    end
  end
  
  def self.totals
    joins(:humidor_cigars)
      .group(:id)
      .sum("humidor_cigars.quantity")
  end
end
```

#### **HumidorCigar Model** (Join Table with Quantity)
```ruby
class HumidorCigar < ApplicationRecord
  belongs_to :humidor
  belongs_to :cigar
  
  validates :humidor_id, presence: true
  validates :cigar_id, presence: true
  validates :quantity, numericality: { greater_than_or_equal_to: 0 }
  validates :cigar_id, uniqueness: { scope: :humidor_id }
  
  after_update :destroy_if_zero_quantity
  
  def add_quantity(amount)
    increment!(:quantity, amount)
  end
  
  def remove_quantity(amount)
    new_qty = quantity - amount
    if new_qty <= 0
      destroy
    else
      update!(quantity: new_qty)
    end
  end
  
  def transfer_quantity(to_humidor, amount)
    raise ArgumentError if amount > quantity
    
    transaction do
      remove_quantity(amount)
      
      target = HumidorCigar.find_or_initialize_by(
        humidor: to_humidor,
        cigar: cigar
      )
      target.quantity ||= 0
      target.add_quantity(amount)
    end
  end
  
  private
  
  def destroy_if_zero_quantity
    destroy if quantity.zero?
  end
end
```

---

## 💼 Business Logic

### **Quantity Management**
- Use `has_many :through` with `HumidorCigar` join table
- Track quantities on the relationship, not duplicate cigar records
- When quantity reaches 0, automatically delete `HumidorCigar` record
- Support bulk adding (box purchase) and individual tracking

### **Capacity Management**
- `max_qty` on humidor prevents overfilling
- Real-time capacity tracking across all humidors
- Visual indicators for capacity status (green/yellow/red)
- Callbacks prevent exceeding capacity

### **OCR Integration Workflow**
1. User uploads image of cigar band
2. `cigar_image` stored via ActiveStorage
3. Tesseract OCR extracts text from image
4. Fuzzy string matching identifies existing cigars/brands
5. If match found: update quantity
6. If no match: prompt for manual entry
7. Manual fallback for unrecognized cigars

---

## ✨ Features

### **1. CRUD Operations**
- **Locations**: Create, read, update, delete storage locations
- **Humidors**: Manage humidor units with capacity tracking
- **Brands**: Catalog cigar brands with website links
- **Cigars**: Track individual cigar types with ratings
- **Inventory**: Add/remove cigars to/from humidors

### **2. OCR Support**
- Camera/upload interface for cigar band images
- Tesseract-based text extraction
- Fuzzy matching to existing database
- Manual entry fallback

### **3. Capacity Tracking**
- Real-time capacity calculations
- Visual capacity indicators
- Overflow prevention
- Transfer between humidors

### **4. Aggregation Dashboard**
- Total cigar counts by type
- Location distribution
- Capacity utilization
- Quick access to all resources

### **5. JSON API**
- Public inventory endpoint with token auth
- Home Assistant integration format
- Grouped by humidor with details

---

## 🔌 API Endpoints

### **Public Inventory API**

#### **GET /api/inventory/:token**
Returns JSON inventory for Home Assistant integration.

**Authentication**: Token-based (UUID in URL)  
**Format**:
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

**Security**: 
- UUID token with expiration tracking
- Rotation capability
- Read-only access
- No authentication required (token provides security)

### **Internal API Endpoints**

#### **Cigars**
- `GET /api/cigars` - List all cigars with quantities
- `GET /api/cigars/:id` - Show cigar details
- `POST /api/cigars` - Create new cigar
- `PUT /api/cigars/:id` - Update cigar
- `DELETE /api/cigars/:id` - Delete cigar (if no inventory)

#### **Humidors**
- `GET /api/humidors` - List all humidors with capacity
- `GET /api/humidors/:id` - Show humidor with contents
- `POST /api/humidors` - Create new humidor
- `PUT /api/humidors/:id` - Update humidor
- `DELETE /api/humidors/:id` - Delete humidor (if empty)

#### **Scans**
- `POST /api/scan` - Process OCR image
  - Params: `image` (file), `mode` (add/remove), `humidor_id`
  - Returns: Match results or error for manual entry

---

## 🎮 Controllers

### **HumidorsController** (RESTful)
```ruby
# Actions: index, show, new, create, edit, update, destroy
# Before filters: authenticate_user!
# Strong params: :name, :max_qty, :location_id, :image
```
- **Index**: List all humidors with capacity/used/available
- **Show**: Details + list of inventories
- **New/Create**: Form for name/capacity/location
- **Edit/Update**: Same form
- **Destroy**: Delete if no inventories

### **CigarsController** (RESTful)
```ruby
# Actions: index, show, new, create, edit, update, destroy
# Before filters: authenticate_user!
# Strong params: :cigar_name, :brand_id, :rating, :cigar_image
```
- **Index**: List all with total_qty and locations
- **Show**: Details + locations array
- **New/Create**: Form for name/brand/rating
- **Edit/Update**: Same form
- **Destroy**: Delete if no inventories

### **InventoriesController** (RESTful)
```ruby
# Actions: index, show, new, create, edit, update, destroy
# Before filters: authenticate_user!
# Strong params: :humidor_id, :cigar_id, :quantity
```
- **Index**: All entries with humidor/cigar details
- **Show**: Single inventory entry
- **Create/Update**: Handle qty changes with capacity check
- **Destroy**: Remove from humidor

### **ScansController** (OCR Processing)
```ruby
# Actions: create
# Before filters: authenticate_user!
# Strong params: :image, :mode, :humidor_id
```
- **Create (POST /scan)**: 
  - Upload image
  - Run OCR (Tesseract)
  - Fuzzy match to known cigars
  - Update inventory based on mode (add/remove)
  - Return error if unrecognized (prompt manual entry)

### **Api::InventoryController** (Namespaced API)
```ruby
# Actions: index
# Before filters: verify_api_token
# No params (token in URL)
```
- **Index**: Return JSON grouped by humidor
- Secure with API key param (check in before_action)

### **HomeController** (Dashboard)
```ruby
# Actions: index
# Before filters: authenticate_user!
```
- **Index**: Aggregate view with totals, locations, capacities
- Load via JS/AJAX for dynamic updates

---

## 🎨 Views

### **Layout**
- `application.html.erb` with Bootstrap 5
- Navigation bar with app links
- Flash message display
- Responsive design

### **Humidors Views**
- `index.html.erb`: Table with name, capacity, available, actions
- `show.html.erb`: Details + inventories table with add/remove
- `_form.html.erb`: Form with name, capacity, location dropdown, image upload

### **Cigars Views**
- `index.html.erb`: Table with name, brand, rating, total qty, locations
- `show.html.erb`: Details + locations list with quantities
- `_form.html.erb`: Form with name, brand dropdown, rating select, image upload

### **Inventories Views**
- `index.html.erb`: Table with humidor, cigar, quantity, actions
- `_form.html.erb`: Form with humidor/cigar dropdowns, quantity input

### **Dashboard (home/index.html.erb)**
- **Totals Section**: List of cigars with quantities
- **Capacities Section**: List of humidors with usage
- **Scan Interface**: Camera/upload with humidor select and mode (add/remove)
- **Quick Actions**: Links to create humidors/cigars

### **Partials**
- `_cigar.html.erb`: Reusable cigar display
- `_humidor.html.erb`: Reusable humidor card
- `_capacity_bar.html.erb`: Visual capacity indicator

---

## 📸 OCR Integration

### **Workflow**
1. User accesses scan interface (camera icon or dashboard)
2. Select mode: Add or Remove
3. Select target humidor
4. Capture/upload image of cigar band
5. FormData POST to `/scan`
6. Server processes with Tesseract
7. Fuzzy match against database
8. If match: Update quantity
9. If no match: Return error with manual entry form

### **Implementation**
```ruby
# In ScansController#create
def create
  image_path = params[:image].tempfile.path
  text = Tesseract.convert(image_path)
  
  # Extract cigar name and brand from OCR text
  cigar = find_best_match(text)
  
  if cigar
    update_inventory(cigar, params[:humidor_id], params[:mode])
    render json: { success: true, cigar: cigar }
  else
    render json: { success: false, extracted_text: text }, status: 422
  end
end

private

def find_best_match(text)
  # Use FuzzyStringMatch gem
  brands = Brand.all
  cigars = Cigar.all
  
  # Fuzzy match logic here
  # Return best match or nil
end
```

### **Dependencies**
- `tesseract-ffi` gem
- `rmagick` or `mini_magick` for image preprocessing
- `fuzzy-string-match` for matching
- JavaScript for camera API access

---

## 🚀 Deployment

### **Production Configuration**
- **Server**: Ubuntu 25.04 LTS
- **Location**: `/var/www/cigar/`
- **Service**: `puma-cigar.service` (systemd)
- **Port**: 3001 (internal)
- **Public URL**: https://cigars.remoteds.us
- **SSL**: Let's Encrypt certificate
- **Nginx**: Reverse proxy on port 443

### **Deployment Method**
```bash
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system

# Full deployment
python manager.py deploy --app cigar

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
    server_name cigars.remoteds.us;
    
    ssl_certificate /etc/letsencrypt/live/cigars.remoteds.us/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cigars.remoteds.us/privkey.pem;
    
    root /var/www/cigar/public;
    
    location / {
        try_files $uri @puma;
    }
    
    location @puma {
        proxy_pass http://unix:/var/www/cigar/tmp/sockets/puma.sock;
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
Environment=CIGAR_DATABASE_PASSWORD=<from-database>
Environment=CIGAR_API_TOKEN=<from-database>
Environment=OPENROUTER_API_KEY=<from-database>
```

**CRITICAL**: Secrets stored in `hosting_production` PostgreSQL database, NOT in .env files.

### **Required Variables**
- `RAILS_ENV`: production
- `SECRET_KEY_BASE`: Rails secret key
- `CIGAR_DATABASE_PASSWORD`: PostgreSQL password
- `CIGAR_API_TOKEN`: API authentication token
- `OPENROUTER_API_KEY`: Optional AI integration

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

# Image & OCR
gem 'image_processing', '~> 1.2'
gem 'tesseract-ffi'
gem 'rmagick'
gem 'fuzzy-string-match'

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
- **Models**: Validations, associations, methods
- **Controllers**: CRUD operations, authentication
- **API**: JSON format, authentication, error handling
- **Integration**: Full workflows (add cigar, OCR scan, etc.)

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
- All controllers must test CRUD operations
- API endpoints must test JSON format
- Authentication must be tested
- OCR integration must have integration tests

---

## 📚 Related Documentation

- **[CIGAR_DEPLOYMENT_GUIDE.md](CIGAR_DEPLOYMENT_GUIDE.md)** - Deployment procedures
- **[ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)** - System architecture
- **[../agents.md](../agents.md)** - Master development rules
- **[SECURITY_GUIDE.md](SECURITY_GUIDE.md)** - Security protocols
- **[README.md](README.md)** - Documentation index

---

**This document serves as the complete design specification for the Cigar Management System. All development, deployment, and documentation work should reference this as the single source of truth for application design.**

**Last Updated**: November 1, 2025  
**Maintained by**: Development Team + AI Agents
