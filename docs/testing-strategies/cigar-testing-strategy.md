# Cigar Management System - Testing Strategy

**Last Updated**: November 1, 2025  
**Version**: 1.0  
**Application**: Cigar Management System  
**Production URL**: https://cigars.remoteds.us  
**Framework**: Ruby on Rails 7.2.2 with RSpec

---

## 📋 Table of Contents
- [Overview](#overview)
- [Database Schema](#database-schema)
- [Test Coverage Requirements](#test-coverage-requirements)
- [Model Testing](#model-testing)
- [Controller Testing](#controller-testing)
- [Integration Testing](#integration-testing)
- [API Testing](#api-testing)
- [Authentication Testing](#authentication-testing)
- [Deployment Verification](#deployment-verification)

---

## 🎯 Overview

The Cigar Management System is a Ruby on Rails application for tracking cigar inventory across multiple humidors with OCR support for cigar band recognition.

### **Key Features to Test**
- CRUD operations for cigars, humidors, brands, and locations
- Inventory tracking with quantity management
- Capacity tracking and validation
- OCR integration for cigar band scanning
- Public JSON API for Home Assistant integration
- User authentication with Devise
- Image attachments with Active Storage

---

## 🗄️ Database Schema

### **Schema Version**: `2025_10_31_160704`

###  **Tables and Relationships**

#### **Core Models**
1. **users** - Authentication (Devise)
   - `email` (string, unique, not null)
   - `encrypted_password` (string, not null)
   - `reset_password_token` (string, unique)
   - Authentication fields (remember_created_at, reset_password_sent_at)

2. **locations** - Physical storage locations
   - `name` (string)
   - `address`, `city`, `state`, `zip`, `country` (strings)
   - **Relationship**: has_many :humidors

3. **humidors** - Storage containers
   - `name` (string)
   - `location_id` (integer, foreign key, not null)
   - `max_qty` (integer)
   - **Relationships**: 
     - belongs_to :location
     - has_many :humidor_cigars
     - has_many :cigars, through: :humidor_cigars

4. **brands** - Cigar manufacturers
   - `name` (string)
   - `website_url` (string)
   - **Relationship**: has_many :cigars

5. **cigar_types** - Cigar classifications
   - `name` (string)
   - `description` (text)
   - **Relationship**: has_many :cigars

6. **strengths** - Strength ratings
   - `name` (string)
   - `description` (text)
   - **Relationship**: has_many :cigars

7. **cigars** - Cigar products
   - `cigar_name` (string)
   - `brand_id` (integer, foreign key, not null)
   - `cigar_type_id` (integer, foreign key)
   - `strength_id` (integer, foreign key)
   - Physical attributes: `wrapper`, `binder`, `filler`, `style`
   - Measurements: `length` (decimal), `ring_gauge` (integer)
   - Notes: `tasting_notes`, `summary` (text)
   - OCR fields: `ai_extracted_text`, `ai_match` (text)
   - **Relationships**:
     - belongs_to :brand
     - belongs_to :cigar_type (optional)
     - belongs_to :strength (optional)
     - has_many :humidor_cigars
     - has_many :humidors, through: :humidor_cigars

8. **humidor_cigars** - Join table for inventory tracking
   - `humidor_id` (integer, foreign key, not null)
   - `cigar_id` (integer, foreign key, not null)
   - `quantity` (integer)
   - **Relationships**:
     - belongs_to :humidor
     - belongs_to :cigar

9. **active_storage** tables - Image attachments
   - active_storage_blobs
   - active_storage_attachments
   - active_storage_variant_records

---

## 📊 Test Coverage Requirements

### **Target Coverage**
- **Overall**: 85%+ code coverage
- **Models**: 90%+ (critical business logic)
- **Controllers**: 85%+ (all CRUD operations)
- **API Endpoints**: 100% (public API must be fully tested)
- **Authentication**: 100% (security-critical)

### **Testing Framework**
```ruby
# Gemfile test group
group :development, :test do
  gem 'rspec-rails'
  gem 'factory_bot_rails'
  gem 'faker'
  gem 'shoulda-matchers'
  gem 'database_cleaner-active_record'
end

group :test do
  gem 'simplecov', require: false
  gem 'capybara'
  gem 'selenium-webdriver'
end
```

---

## 🧪 Model Testing

### **Test Files Location**
All model tests are located in: `cigar-management-system/spec/models/`

### **Required Model Tests**

**Location Model** (`spec/models/location_spec.rb`):
- Test associations (has_many :humidors with dependent destroy)
- Test validations (name presence and uniqueness)
- Test factory validity

**Run tests**: `cd cigar-management-system && bundle exec rspec spec/models/location_spec.rb`

**Humidor Model** (`spec/models/humidor_spec.rb`):
- Test associations (belongs_to :location, has_many :cigars through :humidor_cigars)
- Test validations (name, location_id presence, max_qty numericality)
- Test capacity calculation methods:
  - `used_capacity` - sum of all cigar quantities
  - `available_capacity` - max_qty minus used capacity
  - `capacity_percentage` - percentage of capacity used

**Run tests**: `bundle exec rspec spec/models/humidor_spec.rb`

### **Brand Model** (`spec/models/brand_spec.rb`)
```ruby
RSpec.describe Brand, type: :model do
  describe 'associations' do
    it { should have_many(:cigars).dependent(:restrict_with_error) }
  end

  describe 'validations' do
    it { should validate_presence_of(:name) }
    it { should validate_uniqueness_of(:name) }
    
    context 'website_url format' do
      it 'accepts valid URLs' do
        brand = build(:brand, website_url: 'https://example.com')
        expect(brand).to be_valid
      end

      it 'rejects invalid URLs' do
        brand = build(:brand, website_url: 'not-a-url')
        expect(brand).not_to be_valid
      end
    end
  end
end
```

### **Cigar Model** (`spec/models/cigar_spec.rb`)
```ruby
RSpec.describe Cigar, type: :model do
  describe 'associations' do
    it { should belong_to(:brand) }
    it { should belong_to(:cigar_type).optional }
    it { should belong_to(:strength).optional }
    it { should have_many(:humidor_cigars) }
    it { should have_many(:humidors).through(:humidor_cigars) }
  end

  describe 'validations' do
    it { should validate_presence_of(:cigar_name) }
    it { should validate_presence_of(:brand_id) }
  end

  describe 'business logic methods' do
    let(:cigar) { create(:cigar) }
    
    it 'calculates total_qty across all humidors' do
      create(:humidor_cigar, cigar: cigar, quantity: 10)
      create(:humidor_cigar, cigar: cigar, quantity: 15)
      expect(cigar.total_qty).to eq(25)
    end

    it 'returns locations with quantities' do
      humidor1 = create(:humidor, name: 'Large')
      humidor2 = create(:humidor, name: 'Small')
      create(:humidor_cigar, cigar: cigar, humidor: humidor1, quantity: 10)
      create(:humidor_cigar, cigar: cigar, humidor: humidor2, quantity: 5)
      
      locations = cigar.locations
      expect(locations).to include(
        { humidor: 'Large', qty: 10 },
        { humidor: 'Small', qty: 5 }
      )
    end
  end
end
```

### **HumidorCigar Model** (`spec/models/humidor_cigar_spec.rb`)
```ruby
RSpec.describe HumidorCigar, type: :model do
  describe 'associations' do
    it { should belong_to(:humidor) }
    it { should belong_to(:cigar) }
  end

  describe 'validations' do
    it { should validate_presence_of(:humidor_id) }
    it { should validate_presence_of(:cigar_id) }
    it { should validate_numericality_of(:quantity).is_greater_than_or_equal_to(0) }
  end

  describe 'callbacks' do
    let(:humidor_cigar) { create(:humidor_cigar, quantity: 5) }

    it 'destroys record when quantity reaches zero' do
      humidor_cigar.update(quantity: 0)
      expect(HumidorCigar.find_by(id: humidor_cigar.id)).to be_nil
    end
  end

  describe 'quantity management methods' do
    let(:humidor1) { create(:humidor) }
    let(:humidor2) { create(:humidor) }
    let(:humidor_cigar) { create(:humidor_cigar, humidor: humidor1, quantity: 10) }

    it 'transfers quantity to another humidor' do
      humidor_cigar.transfer_quantity(humidor2, 5)
      expect(humidor_cigar.reload.quantity).to eq(5)
      expect(HumidorCigar.find_by(humidor: humidor2).quantity).to eq(5)
    end

    it 'adds quantity' do
      humidor_cigar.add_quantity(5)
      expect(humidor_cigar.reload.quantity).to eq(15)
    end

    it 'removes quantity' do
      humidor_cigar.remove_quantity(3)
      expect(humidor_cigar.reload.quantity).to eq(7)
    end
  end
end
```

---

## 🎮 Controller Testing

### **Test Structure**
All controllers should test:
1. Authentication requirements
2. Successful CRUD operations
3. Failed operations (validation errors)
4. Redirects and flash messages
5. Authorization (if role-based access exists)

### **Example: HumidorsController** (`spec/controllers/humidors_controller_spec.rb`)
```ruby
RSpec.describe HumidorsController, type: :controller do
  let(:user) { create(:user) }
  let(:location) { create(:location) }
  let(:valid_attributes) { { name: 'Test Humidor', location_id: location.id, max_qty: 100 } }
  let(:invalid_attributes) { { name: '', location_id: nil } }

  before { sign_in user }

  describe 'GET #index' do
    it 'returns a success response' do
      get :index
      expect(response).to be_successful
    end

    it 'assigns @humidors' do
      humidor = create(:humidor)
      get :index
      expect(assigns(:humidors)).to include(humidor)
    end
  end

  describe 'GET #show' do
    let(:humidor) { create(:humidor) }

    it 'returns a success response' do
      get :show, params: { id: humidor.id }
      expect(response).to be_successful
    end
  end

  describe 'POST #create' do
    context 'with valid params' do
      it 'creates a new Humidor' do
        expect {
          post :create, params: { humidor: valid_attributes }
        }.to change(Humidor, :count).by(1)
      end

      it 'redirects to the created humidor' do
        post :create, params: { humidor: valid_attributes }
        expect(response).to redirect_to(Humidor.last)
      end
    end

    context 'with invalid params' do
      it 'does not create a new Humidor' do
        expect {
          post :create, params: { humidor: invalid_attributes }
        }.not_to change(Humidor, :count)
      end

      it 'renders the new template' do
        post :create, params: { humidor: invalid_attributes }
        expect(response).to render_template(:new)
      end
    end
  end
end
```

---

## 🔗 Integration Testing

### **Feature Tests** (`spec/features/`)

```ruby
# spec/features/cigar_management_spec.rb
RSpec.describe 'Cigar Management', type: :feature do
  let(:user) { create(:user) }
  let(:brand) { create(:brand) }

  before do
    login_as(user, scope: :user)
  end

  scenario 'User creates a new cigar' do
    visit new_cigar_path
    
    fill_in 'Cigar name', with: 'Undercrown'
    select brand.name, from: 'Brand'
    fill_in 'Ring gauge', with: '52'
    
    click_button 'Create Cigar'
    
    expect(page).to have_content('Cigar was successfully created')
    expect(page).to have_content('Undercrown')
  end

  scenario 'User views cigar inventory' do
    humidor = create(:humidor, name: 'Large Humidor')
    cigar = create(:cigar, cigar_name: 'Test Cigar')
    create(:humidor_cigar, humidor: humidor, cigar: cigar, quantity: 10)

    visit cigar_path(cigar)

    expect(page).to have_content('Large Humidor: 10')
  end
end
```

---

## 🌐 API Testing

### **Public Inventory API** (`spec/requests/api/inventory_spec.rb`)
```ruby
RSpec.describe 'API::Inventory', type: :request do
  let(:api_token) { ENV['CIGAR_API_TOKEN'] || 'test-token' }
  let(:humidor) { create(:humidor, name: 'LargeHumidor') }
  let(:brand) { create(:brand, name: 'Drew Estate') }
  let(:cigar) { create(:cigar, cigar_name: 'Undercrown', brand: brand) }

  before do
    create(:humidor_cigar, humidor: humidor, cigar: cigar, quantity: 6)
  end

  describe 'GET /api/inventory/:token' do
    it 'returns inventory data in correct format' do
      get "/api/inventory/#{api_token}"
      
      expect(response).to have_http_status(:success)
      
      json = JSON.parse(response.body)
      expect(json['cigars']).to have_key('LargeHumidor')
      expect(json['cigars']['LargeHumidor']).to include(
        hash_including(
          'cigar_name' => 'Undercrown',
          'brand' => 'Drew Estate',
          'qty' => 6
        )
      )
    end

    it 'requires valid token' do
      get '/api/inventory/invalid-token'
      expect(response).to have_http_status(:unauthorized)
    end
  end
end
```

---

## 🔐 Authentication Testing

### **Devise Authentication** (`spec/features/authentication_spec.rb`)
```ruby
RSpec.describe 'Authentication', type: :feature do
  let(:user) { create(:user, email: 'test@example.com', password: 'password123') }

  scenario 'User logs in successfully' do
    visit new_user_session_path
    
    fill_in 'Email', with: user.email
    fill_in 'Password', with: 'password123'
    click_button 'Log in'
    
    expect(page).to have_content('Signed in successfully')
    expect(current_path).to eq(root_path)
  end

  scenario 'User cannot access protected pages without login' do
    visit cigars_path
    expect(current_path).to eq(new_user_session_path)
    expect(page).to have_content('You need to sign in')
  end

  scenario 'User logs out successfully' do
    login_as(user, scope: :user)
    visit root_path
    
    click_link 'Logout'
    
    expect(page).to have_content('Signed out successfully')
  end
end
```

---

## ✅ Deployment Verification

### **Health Check Tests**

After deployment, the following automated checks should run:

#### **1. Service Status Check**
```bash
# Verify systemd service is running
systemctl status puma-cigar --no-pager | grep "active (running)"
```

#### **2. HTTP Accessibility Check**
```bash
# Verify app responds
curl -I https://cigars.remoteds.us | grep "200 OK"

# Verify login page contains app name
curl -s https://cigars.remoteds.us/users/sign_in | grep -i "cigar"
```

#### **3. Authentication Check**
```bash
# Test that auth is required
curl -s -o /dev/null -w "%{http_code}" https://cigars.remoteds.us/cigars | grep "302"
```

#### **4. Database Connectivity Check**
```bash
# Via Rails console
ssh root@asterra.remoteds.us "cd /var/www/cigar/current && RAILS_ENV=production bundle exec rails runner 'puts Cigar.count'"
```

#### **5. API Endpoint Check**
```bash
# Test public API with token
curl -s "https://cigars.remoteds.us/api/inventory/${CIGAR_API_TOKEN}" | jq '.cigars'
```

### **Automated Health Check Command**
```bash
# Run via manager.py
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py health-check --app cigar"
```

This command should verify:
- ✅ Puma service is active
- ✅ App responds to HTTP requests
- ✅ Authentication is enforced
- ✅ Database is accessible
- ✅ API endpoints function correctly

---

## 📚 Related Documentation

- **[Application Design](../application-design-documents/cigar-management-system.md)** - Full architecture
- **[Deployment Guide](../deployment-guides/CIGAR_DEPLOYMENT_GUIDE.md)** - Deployment procedures
- **[Testing Strategies Index](README.md)** - Testing overview

---

**Last Updated**: November 1, 2025  
**Maintained By**: Development Team
