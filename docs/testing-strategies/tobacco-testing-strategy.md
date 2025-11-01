# Tobacco Management System - Testing Strategy

**Last Updated**: November 1, 2025  
**Version**: 1.0  
**Application**: Tobacco Management System  
**Production URL**: https://tobacco.remoteds.us  
**Framework**: Ruby on Rails 7.2.2 with RSpec

---

## 📋 Table of Contents
- [Overview](#overview)
- [Database Schema](#database-schema)
- [Test Coverage Requirements](#test-coverage-requirements)
- [Model Testing](#model-testing)
- [Controller Testing](#controller-testing)
- [Integration Testing](#integration-testing)
- [Authentication Testing](#authentication-testing)
- [Deployment Verification](#deployment-verification)

---

## 🎯 Overview

The Tobacco Management System is a Ruby on Rails application for tracking tobacco products across multiple storage containers with capacity management and product categorization.

### **Key Features to Test**
- CRUD operations for tobacco products, storages, brands, and locations
- Inventory tracking with quantity management (decimal for weight/volume)
- Capacity tracking for storage containers
- Product blend type and strength classification
- User authentication with Devise
- Multi-location storage management

---

## 🗄️ Database Schema

### **Schema Version**: `2025_10_30_183034`
### **Database**: PostgreSQL

### **Tables and Relationships**

#### **Core Models**
1. **users** - Authentication (Devise)
   - `email` (string, unique, not null)
   - `encrypted_password` (string, not null)
   - `reset_password_token` (string, unique)
   - Authentication fields (remember_created_at, reset_password_sent_at)

2. **locations** - Physical storage locations
   - `name` (string)
   - `address`, `city`, `state`, `zip`, `country` (strings)
   - **Relationship**: has_many :storages

3. **storages** - Storage containers
   - `name` (string)
   - `location_id` (bigint, foreign key, not null)
   - `max_capacity` (decimal)
   - `description` (text)
   - **Relationships**: 
     - belongs_to :location
     - has_many :storage_tobaccos
     - has_many :tobacco_products, through: :storage_tobaccos

4. **brands** - Tobacco manufacturers
   - `name` (string)
   - `website_url` (string)
   - **Relationship**: has_many :tobacco_products

5. **tobacco_products** - Tobacco products
   - `name` (string)
   - `brand_id` (bigint, foreign key, not null)
   - `blend_type` (string) - e.g., Virginia, English, Aromatic
   - `strength` (string) - e.g., Mild, Medium, Full
   - `cut` (string) - e.g., Ribbon, Flake, Plug
   - `rating` (integer) - 1-5 scale
   - `description` (text)
   - **Relationships**:
     - belongs_to :brand
     - has_many :storage_tobaccos
     - has_many :storages, through: :storage_tobaccos

6. **storage_tobaccos** - Join table for inventory tracking
   - `storage_id` (bigint, foreign key, not null)
   - `tobacco_product_id` (bigint, foreign key, not null)
   - `quantity` (decimal) - Weight or volume
   - `notes` (text)
   - **Relationships**:
     - belongs_to :storage
     - belongs_to :tobacco_product

---

## 📊 Test Coverage Requirements

### **Target Coverage**
- **Overall**: 85%+ code coverage
- **Models**: 90%+ (critical business logic)
- **Controllers**: 85%+ (all CRUD operations)
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

### **Location Model** (`spec/models/location_spec.rb`)
```ruby
RSpec.describe Location, type: :model do
  describe 'associations' do
    it { should have_many(:storages).dependent(:destroy) }
  end

  describe 'validations' do
    it { should validate_presence_of(:name) }
    it { should validate_uniqueness_of(:name) }
  end

  describe 'factory' do
    it 'has a valid factory' do
      expect(build(:location)).to be_valid
    end
  end
end
```

### **Storage Model** (`spec/models/storage_spec.rb`)
```ruby
RSpec.describe Storage, type: :model do
  describe 'associations' do
    it { should belong_to(:location) }
    it { should have_many(:storage_tobaccos) }
    it { should have_many(:tobacco_products).through(:storage_tobaccos) }
  end

  describe 'validations' do
    it { should validate_presence_of(:name) }
    it { should validate_presence_of(:location_id) }
    it { should validate_numericality_of(:max_capacity).is_greater_than(0) }
  end

  describe 'capacity methods' do
    let(:storage) { create(:storage, max_capacity: 1000.0) }
    
    before do
      create(:storage_tobacco, storage: storage, quantity: 250.5)
      create(:storage_tobacco, storage: storage, quantity: 300.25)
    end

    it 'calculates used_capacity correctly' do
      expect(storage.used_capacity).to eq(550.75)
    end

    it 'calculates available_capacity correctly' do
      expect(storage.available_capacity).to eq(449.25)
    end

    it 'calculates capacity_percentage correctly' do
      expect(storage.capacity_percentage).to be_within(0.01).of(55.08)
    end

    it 'prevents exceeding max capacity' do
      storage_tobacco = build(:storage_tobacco, storage: storage, quantity: 500.0)
      expect(storage_tobacco).not_to be_valid
      expect(storage_tobacco.errors[:quantity]).to include('would exceed storage capacity')
    end
  end
end
```

### **Brand Model** (`spec/models/brand_spec.rb`)
```ruby
RSpec.describe Brand, type: :model do
  describe 'associations' do
    it { should have_many(:tobacco_products).dependent(:restrict_with_error) }
  end

  describe 'validations' do
    it { should validate_presence_of(:name) }
    it { should validate_uniqueness_of(:name) }
    
    context 'website_url format' do
      it 'accepts valid URLs' do
        brand = build(:brand, website_url: 'https://example.com')
        expect(brand).to be_valid
      end

      it 'accepts nil website_url' do
        brand = build(:brand, website_url: nil)
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

### **TobaccoProduct Model** (`spec/models/tobacco_product_spec.rb`)
```ruby
RSpec.describe TobaccoProduct, type: :model do
  describe 'associations' do
    it { should belong_to(:brand) }
    it { should have_many(:storage_tobaccos) }
    it { should have_many(:storages).through(:storage_tobaccos) }
  end

  describe 'validations' do
    it { should validate_presence_of(:name) }
    it { should validate_presence_of(:brand_id) }
    it { should validate_inclusion_of(:rating).in_range(1..5).allow_nil }
    
    it 'validates blend_type is from allowed list' do
      valid_types = ['Virginia', 'English', 'Aromatic', 'Burley', 'Oriental', 'Latakia']
      valid_types.each do |type|
        product = build(:tobacco_product, blend_type: type)
        expect(product).to be_valid
      end
    end

    it 'validates strength is from allowed list' do
      valid_strengths = ['Mild', 'Mild-Medium', 'Medium', 'Medium-Full', 'Full']
      valid_strengths.each do |strength|
        product = build(:tobacco_product, strength: strength)
        expect(product).to be_valid
      end
    end
  end

  describe 'business logic methods' do
    let(:product) { create(:tobacco_product) }
    
    it 'calculates total_quantity across all storages' do
      create(:storage_tobacco, tobacco_product: product, quantity: 100.5)
      create(:storage_tobacco, tobacco_product: product, quantity: 75.25)
      expect(product.total_quantity).to eq(175.75)
    end

    it 'returns storage locations with quantities' do
      storage1 = create(:storage, name: 'Basement')
      storage2 = create(:storage, name: 'Cellar')
      create(:storage_tobacco, tobacco_product: product, storage: storage1, quantity: 100.0)
      create(:storage_tobacco, tobacco_product: product, storage: storage2, quantity: 50.0)
      
      locations = product.storage_locations
      expect(locations).to include(
        { storage: 'Basement', quantity: 100.0 },
        { storage: 'Cellar', quantity: 50.0 }
      )
    end
  end
end
```

### **StorageTobacco Model** (`spec/models/storage_tobacco_spec.rb`)
```ruby
RSpec.describe StorageTobacco, type: :model do
  describe 'associations' do
    it { should belong_to(:storage) }
    it { should belong_to(:tobacco_product) }
  end

  describe 'validations' do
    it { should validate_presence_of(:storage_id) }
    it { should validate_presence_of(:tobacco_product_id) }
    it { should validate_numericality_of(:quantity).is_greater_than(0) }
  end

  describe 'callbacks' do
    let(:storage_tobacco) { create(:storage_tobacco, quantity: 5.5) }

    it 'destroys record when quantity reaches zero' do
      storage_tobacco.update(quantity: 0)
      expect(StorageTobacco.find_by(id: storage_tobacco.id)).to be_nil
    end
  end

  describe 'quantity management methods' do
    let(:storage1) { create(:storage) }
    let(:storage2) { create(:storage) }
    let(:storage_tobacco) { create(:storage_tobacco, storage: storage1, quantity: 100.0) }

    it 'transfers quantity to another storage' do
      storage_tobacco.transfer_quantity(storage2, 40.0)
      expect(storage_tobacco.reload.quantity).to eq(60.0)
      expect(StorageTobacco.find_by(storage: storage2).quantity).to eq(40.0)
    end

    it 'adds quantity' do
      storage_tobacco.add_quantity(25.5)
      expect(storage_tobacco.reload.quantity).to eq(125.5)
    end

    it 'removes quantity' do
      storage_tobacco.remove_quantity(30.0)
      expect(storage_tobacco.reload.quantity).to eq(70.0)
    end

    it 'prevents negative quantities' do
      expect {
        storage_tobacco.remove_quantity(150.0)
      }.to raise_error(ArgumentError, 'Cannot remove more than available quantity')
    end
  end
end
```

---

## 🎮 Controller Testing

### **Example: StoragesController** (`spec/controllers/storages_controller_spec.rb`)
```ruby
RSpec.describe StoragesController, type: :controller do
  let(:user) { create(:user) }
  let(:location) { create(:location) }
  let(:valid_attributes) { 
    { name: 'Test Storage', location_id: location.id, max_capacity: 1000.0, description: 'Test' }
  }
  let(:invalid_attributes) { { name: '', location_id: nil } }

  before { sign_in user }

  describe 'GET #index' do
    it 'returns a success response' do
      get :index
      expect(response).to be_successful
    end

    it 'assigns @storages' do
      storage = create(:storage)
      get :index
      expect(assigns(:storages)).to include(storage)
    end
  end

  describe 'GET #show' do
    let(:storage) { create(:storage) }

    it 'returns a success response' do
      get :show, params: { id: storage.id }
      expect(response).to be_successful
    end

    it 'displays capacity information' do
      create(:storage_tobacco, storage: storage, quantity: 250.0)
      get :show, params: { id: storage.id }
      expect(assigns(:storage).used_capacity).to eq(250.0)
    end
  end

  describe 'POST #create' do
    context 'with valid params' do
      it 'creates a new Storage' do
        expect {
          post :create, params: { storage: valid_attributes }
        }.to change(Storage, :count).by(1)
      end

      it 'redirects to the created storage' do
        post :create, params: { storage: valid_attributes }
        expect(response).to redirect_to(Storage.last)
      end
    end

    context 'with invalid params' do
      it 'does not create a new Storage' do
        expect {
          post :create, params: { storage: invalid_attributes }
        }.not_to change(Storage, :count)
      end
    end
  end

  describe 'PATCH #update' do
    let(:storage) { create(:storage) }
    let(:new_attributes) { { name: 'Updated Storage', max_capacity: 2000.0 } }

    it 'updates the storage' do
      patch :update, params: { id: storage.id, storage: new_attributes }
      storage.reload
      expect(storage.name).to eq('Updated Storage')
      expect(storage.max_capacity).to eq(2000.0)
    end
  end

  describe 'DELETE #destroy' do
    let!(:storage) { create(:storage) }

    it 'destroys the storage' do
      expect {
        delete :destroy, params: { id: storage.id }
      }.to change(Storage, :count).by(-1)
    end

    it 'redirects to the storages list' do
      delete :destroy, params: { id: storage.id }
      expect(response).to redirect_to(storages_url)
    end
  end
end
```

---

## 🔗 Integration Testing

### **Feature Tests** (`spec/features/tobacco_management_spec.rb`)
```ruby
RSpec.describe 'Tobacco Management', type: :feature do
  let(:user) { create(:user) }
  let(:brand) { create(:brand, name: 'Peterson') }
  let(:location) { create(:location, name: 'Home') }
  let(:storage) { create(:storage, name: 'Cabinet', location: location) }

  before do
    login_as(user, scope: :user)
  end

  scenario 'User creates a new tobacco product' do
    visit new_tobacco_product_path
    
    fill_in 'Name', with: 'Early Morning Pipe'
    select brand.name, from: 'Brand'
    select 'English', from: 'Blend type'
    select 'Medium', from: 'Strength'
    fill_in 'Description', with: 'Classic English blend'
    
    click_button 'Create Tobacco product'
    
    expect(page).to have_content('Tobacco product was successfully created')
    expect(page).to have_content('Early Morning Pipe')
  end

  scenario 'User adds tobacco to storage' do
    product = create(:tobacco_product, name: 'Test Blend')
    
    visit storage_path(storage)
    click_link 'Add Tobacco'
    
    select product.name, from: 'Tobacco product'
    fill_in 'Quantity', with: '100.5'
    fill_in 'Notes', with: 'Fresh tin'
    
    click_button 'Add to Storage'
    
    expect(page).to have_content('Test Blend')
    expect(page).to have_content('100.5')
  end

  scenario 'User views storage capacity' do
    product = create(:tobacco_product)
    create(:storage_tobacco, storage: storage, tobacco_product: product, quantity: 250.0)
    storage.update(max_capacity: 1000.0)

    visit storage_path(storage)

    expect(page).to have_content('Used: 250.0')
    expect(page).to have_content('Available: 750.0')
    expect(page).to have_content('25%')
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
    visit tobacco_products_path
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
systemctl status puma-tobacco --no-pager | grep "active (running)"
```

#### **2. HTTP Accessibility Check**
```bash
# Verify app responds
curl -I https://tobacco.remoteds.us | grep "200 OK"

# Verify login page contains app name
curl -s https://tobacco.remoteds.us/users/sign_in | grep -i "tobacco"
```

#### **3. Authentication Check**
```bash
# Test that auth is required
curl -s -o /dev/null -w "%{http_code}" https://tobacco.remoteds.us/tobacco_products | grep "302"
```

#### **4. Database Connectivity Check**
```bash
# Via Rails console
ssh root@asterra.remoteds.us "cd /var/www/tobacco/current && RAILS_ENV=production bundle exec rails runner 'puts TobaccoProduct.count'"
```

### **Automated Health Check Command**
```bash
# Run via manager.py
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py health-check --app tobacco"
```

This command should verify:
- ✅ Puma service is active
- ✅ App responds to HTTP requests
- ✅ Authentication is enforced
- ✅ Database is accessible
- ✅ PostgreSQL connection is working

---

## 📚 Related Documentation

- **[Application Design](../application-design-documents/tobacco-management-system.md)** - Full architecture
- **[Deployment Guide](../deployment-guides/TOBACCO_DEPLOYMENT_GUIDE.md)** - Deployment procedures
- **[Testing Strategies Index](README.md)** - Testing overview

---

**Last Updated**: November 1, 2025  
**Maintained By**: Development Team
