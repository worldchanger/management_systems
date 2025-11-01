# Whiskey Management System - Testing Strategy

**Last Updated**: November 1, 2025  
**Version**: 1.0  
**Application**: Whiskey Management System  
**Production URL**: https://whiskey.remoteds.us  
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

The Whiskey Management System is a Ruby on Rails application for tracking whiskey collections with detailed product information including type, ABV, proof, age, and mash bill specifications.

### **Key Features to Test**
- CRUD operations for whiskeys, brands, whiskey types, and locations
- Inventory tracking with bottle quantity management
- Whiskey type classification (Bourbon, Rye, Scotch, etc.)
- ABV and Proof calculations and validations
- Age and mash bill tracking
- User authentication with Devise
- Image attachments with Active Storage (bottle photos)

---

## 🗄️ Database Schema

### **Schema Version**: `2025_10_31_184730`

### **Tables and Relationships**

#### **Core Models**
1. **users** - Authentication (Devise)
   - `email` (string, unique, not null)
   - `encrypted_password` (string, not null)
   - `reset_password_token` (string, unique)
   - Authentication fields (remember_created_at, reset_password_sent_at)

2. **locations** - Storage locations
   - `name` (string)
   - `description` (text)
   - `address` (text)
   - **Relationship**: has_many :whiskeys

3. **brands** - Whiskey manufacturers/distilleries
   - `name` (string)
   - `description` (text)
   - `website_url` (string)
   - `country` (string) - Country of origin
   - **Relationship**: has_many :whiskeys

4. **whiskey_types** - Whiskey classifications
   - `name` (string) - e.g., Bourbon, Rye, Scotch, Irish, Canadian
   - `description` (text)
   - **Relationship**: has_many :whiskeys

5. **whiskeys** - Whiskey products
   - `name` (string)
   - `description` (text)
   - `mash_bill` (text) - Grain composition (e.g., "75% Corn, 21% Rye, 4% Malted Barley")
   - `abv` (decimal) - Alcohol by volume percentage
   - `proof` (decimal) - Proof rating (ABV * 2 in US)
   - `age` (integer) - Age in years
   - `quantity` (integer) - Number of bottles in possession
   - `brand_id` (integer, foreign key, not null)
   - `whiskey_type_id` (integer, foreign key, not null)
   - `location_id` (integer, foreign key, not null)
   - **Relationships**:
     - belongs_to :brand
     - belongs_to :whiskey_type
     - belongs_to :location
     - has_many_attached :images (Active Storage)

6. **active_storage** tables - Image attachments
   - active_storage_blobs
   - active_storage_attachments
   - active_storage_variant_records

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
    it { should have_many(:whiskeys).dependent(:destroy) }
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

  describe 'methods' do
    let(:location) { create(:location) }
    
    it 'returns total bottle count' do
      create(:whiskey, location: location, quantity: 5)
      create(:whiskey, location: location, quantity: 3)
      expect(location.total_bottles).to eq(8)
    end
  end
end
```

### **Brand Model** (`spec/models/brand_spec.rb`)
```ruby
RSpec.describe Brand, type: :model do
  describe 'associations' do
    it { should have_many(:whiskeys).dependent(:restrict_with_error) }
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

  describe 'country validations' do
    it 'accepts valid countries' do
      valid_countries = ['USA', 'Scotland', 'Ireland', 'Canada', 'Japan']
      valid_countries.each do |country|
        brand = build(:brand, country: country)
        expect(brand).to be_valid
      end
    end
  end
end
```

### **WhiskeyType Model** (`spec/models/whiskey_type_spec.rb`)
```ruby
RSpec.describe WhiskeyType, type: :model do
  describe 'associations' do
    it { should have_many(:whiskeys) }
  end

  describe 'validations' do
    it { should validate_presence_of(:name) }
    it { should validate_uniqueness_of(:name) }
  end

  describe 'predefined types' do
    it 'includes standard whiskey types' do
      types = ['Bourbon', 'Rye', 'Scotch', 'Irish', 'Canadian', 'Japanese', 'Tennessee']
      types.each do |type|
        whiskey_type = create(:whiskey_type, name: type)
        expect(whiskey_type).to be_valid
      end
    end
  end
end
```

### **Whiskey Model** (`spec/models/whiskey_spec.rb`)
```ruby
RSpec.describe Whiskey, type: :model do
  describe 'associations' do
    it { should belong_to(:brand) }
    it { should belong_to(:whiskey_type) }
    it { should belong_to(:location) }
    it { should have_many_attached(:images) }
  end

  describe 'validations' do
    it { should validate_presence_of(:name) }
    it { should validate_presence_of(:brand_id) }
    it { should validate_presence_of(:whiskey_type_id) }
    it { should validate_presence_of(:location_id) }
    
    it { should validate_numericality_of(:abv).is_greater_than(0).is_less_than_or_equal_to(100).allow_nil }
    it { should validate_numericality_of(:proof).is_greater_than(0).is_less_than_or_equal_to(200).allow_nil }
    it { should validate_numericality_of(:age).is_greater_than_or_equal_to(0).only_integer.allow_nil }
    it { should validate_numericality_of(:quantity).is_greater_than_or_equal_to(0).only_integer }
  end

  describe 'ABV and Proof calculations' do
    it 'calculates proof from ABV' do
      whiskey = build(:whiskey, abv: 40.0, proof: nil)
      whiskey.calculate_proof_from_abv
      expect(whiskey.proof).to eq(80.0)
    end

    it 'calculates ABV from proof' do
      whiskey = build(:whiskey, abv: nil, proof: 90.0)
      whiskey.calculate_abv_from_proof
      expect(whiskey.abv).to eq(45.0)
    end

    it 'validates ABV and proof consistency' do
      whiskey = build(:whiskey, abv: 40.0, proof: 100.0) # Inconsistent
      expect(whiskey).not_to be_valid
      expect(whiskey.errors[:proof]).to include('does not match ABV')
    end
  end

  describe 'mash bill validations' do
    it 'validates bourbon mash bill requirements' do
      bourbon_type = create(:whiskey_type, name: 'Bourbon')
      whiskey = build(:whiskey, whiskey_type: bourbon_type, mash_bill: '75% Corn, 21% Rye, 4% Malted Barley')
      expect(whiskey).to be_valid
    end

    it 'rejects invalid bourbon mash bill (corn < 51%)' do
      bourbon_type = create(:whiskey_type, name: 'Bourbon')
      whiskey = build(:whiskey, whiskey_type: bourbon_type, mash_bill: '40% Corn, 50% Rye, 10% Malted Barley')
      expect(whiskey).not_to be_valid
      expect(whiskey.errors[:mash_bill]).to include('Bourbon must contain at least 51% corn')
    end

    it 'validates rye whiskey mash bill requirements' do
      rye_type = create(:whiskey_type, name: 'Rye')
      whiskey = build(:whiskey, whiskey_type: rye_type, mash_bill: '51% Rye, 39% Corn, 10% Malted Barley')
      expect(whiskey).to be_valid
    end
  end

  describe 'inventory methods' do
    let(:whiskey) { create(:whiskey, quantity: 10) }

    it 'adds bottles' do
      whiskey.add_bottles(5)
      expect(whiskey.reload.quantity).to eq(15)
    end

    it 'removes bottles' do
      whiskey.remove_bottles(3)
      expect(whiskey.reload.quantity).to eq(7)
    end

    it 'prevents negative quantity' do
      expect {
        whiskey.remove_bottles(15)
      }.to raise_error(ArgumentError, 'Cannot remove more bottles than available')
    end

    it 'checks if in stock' do
      expect(whiskey.in_stock?).to be true
      whiskey.update(quantity: 0)
      expect(whiskey.in_stock?).to be false
    end
  end

  describe 'scopes' do
    let!(:bourbon) { create(:whiskey, whiskey_type: create(:whiskey_type, name: 'Bourbon')) }
    let!(:rye) { create(:whiskey, whiskey_type: create(:whiskey_type, name: 'Rye')) }
    let!(:in_stock) { create(:whiskey, quantity: 5) }
    let!(:out_of_stock) { create(:whiskey, quantity: 0) }

    it 'filters by whiskey type' do
      expect(Whiskey.by_type('Bourbon')).to include(bourbon)
      expect(Whiskey.by_type('Bourbon')).not_to include(rye)
    end

    it 'filters in stock whiskeys' do
      expect(Whiskey.in_stock).to include(in_stock)
      expect(Whiskey.in_stock).not_to include(out_of_stock)
    end

    it 'filters by age range' do
      young = create(:whiskey, age: 4)
      aged = create(:whiskey, age: 12)
      very_aged = create(:whiskey, age: 18)
      
      expect(Whiskey.aged_between(10, 15)).to include(aged)
      expect(Whiskey.aged_between(10, 15)).not_to include(young, very_aged)
    end
  end
end
```

---

## 🎮 Controller Testing

### **Example: WhiskeysController** (`spec/controllers/whiskeys_controller_spec.rb`)
```ruby
RSpec.describe WhiskeysController, type: :controller do
  let(:user) { create(:user) }
  let(:brand) { create(:brand) }
  let(:whiskey_type) { create(:whiskey_type) }
  let(:location) { create(:location) }
  let(:valid_attributes) { 
    { 
      name: 'Buffalo Trace',
      brand_id: brand.id,
      whiskey_type_id: whiskey_type.id,
      location_id: location.id,
      abv: 45.0,
      age: 8,
      quantity: 3,
      mash_bill: '75% Corn, 21% Rye, 4% Malted Barley'
    }
  }
  let(:invalid_attributes) { { name: '', brand_id: nil } }

  before { sign_in user }

  describe 'GET #index' do
    it 'returns a success response' do
      get :index
      expect(response).to be_successful
    end

    it 'assigns @whiskeys' do
      whiskey = create(:whiskey)
      get :index
      expect(assigns(:whiskeys)).to include(whiskey)
    end

    it 'filters by whiskey type' do
      bourbon = create(:whiskey, whiskey_type: create(:whiskey_type, name: 'Bourbon'))
      rye = create(:whiskey, whiskey_type: create(:whiskey_type, name: 'Rye'))
      
      get :index, params: { whiskey_type: 'Bourbon' }
      expect(assigns(:whiskeys)).to include(bourbon)
      expect(assigns(:whiskeys)).not_to include(rye)
    end
  end

  describe 'GET #show' do
    let(:whiskey) { create(:whiskey) }

    it 'returns a success response' do
      get :show, params: { id: whiskey.id }
      expect(response).to be_successful
    end

    it 'displays calculated proof' do
      whiskey = create(:whiskey, abv: 45.0)
      get :show, params: { id: whiskey.id }
      expect(assigns(:whiskey).proof).to eq(90.0)
    end
  end

  describe 'POST #create' do
    context 'with valid params' do
      it 'creates a new Whiskey' do
        expect {
          post :create, params: { whiskey: valid_attributes }
        }.to change(Whiskey, :count).by(1)
      end

      it 'redirects to the created whiskey' do
        post :create, params: { whiskey: valid_attributes }
        expect(response).to redirect_to(Whiskey.last)
      end
    end

    context 'with invalid params' do
      it 'does not create a new Whiskey' do
        expect {
          post :create, params: { whiskey: invalid_attributes }
        }.not_to change(Whiskey, :count)
      end
    end
  end

  describe 'PATCH #update' do
    let(:whiskey) { create(:whiskey, quantity: 3) }

    it 'updates the whiskey quantity' do
      patch :update, params: { id: whiskey.id, whiskey: { quantity: 5 } }
      whiskey.reload
      expect(whiskey.quantity).to eq(5)
    end
  end
end
```

---

## 🔗 Integration Testing

### **Feature Tests** (`spec/features/whiskey_management_spec.rb`)
```ruby
RSpec.describe 'Whiskey Management', type: :feature do
  let(:user) { create(:user) }
  let(:brand) { create(:brand, name: 'Buffalo Trace') }
  let(:whiskey_type) { create(:whiskey_type, name: 'Bourbon') }
  let(:location) { create(:location, name: 'Home Bar') }

  before do
    login_as(user, scope: :user)
  end

  scenario 'User creates a new whiskey' do
    visit new_whiskey_path
    
    fill_in 'Name', with: 'Eagle Rare 10 Year'
    select brand.name, from: 'Brand'
    select whiskey_type.name, from: 'Whiskey type'
    select location.name, from: 'Location'
    fill_in 'ABV', with: '45'
    fill_in 'Age', with: '10'
    fill_in 'Quantity', with: '2'
    fill_in 'Mash bill', with: '75% Corn, 21% Rye, 4% Malted Barley'
    
    click_button 'Create Whiskey'
    
    expect(page).to have_content('Whiskey was successfully created')
    expect(page).to have_content('Eagle Rare 10 Year')
    expect(page).to have_content('Proof: 90.0') # Auto-calculated
  end

  scenario 'User views whiskey collection' do
    whiskey1 = create(:whiskey, name: 'Bourbon 1', brand: brand, quantity: 3)
    whiskey2 = create(:whiskey, name: 'Bourbon 2', brand: brand, quantity: 0)

    visit whiskeys_path

    expect(page).to have_content('Bourbon 1')
    expect(page).to have_content('In Stock: 3 bottles')
    expect(page).to have_content('Bourbon 2')
    expect(page).to have_content('Out of Stock')
  end

  scenario 'User filters by whiskey type' do
    bourbon = create(:whiskey, name: 'Buffalo Trace', whiskey_type: create(:whiskey_type, name: 'Bourbon'))
    rye = create(:whiskey, name: 'Rittenhouse Rye', whiskey_type: create(:whiskey_type, name: 'Rye'))

    visit whiskeys_path
    select 'Bourbon', from: 'Whiskey Type'
    click_button 'Filter'

    expect(page).to have_content('Buffalo Trace')
    expect(page).not_to have_content('Rittenhouse Rye')
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
    visit whiskeys_path
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
systemctl status puma-whiskey --no-pager | grep "active (running)"
```

#### **2. HTTP Accessibility Check**
```bash
# Verify app responds
curl -I https://whiskey.remoteds.us | grep "200 OK"

# Verify login page contains app name
curl -s https://whiskey.remoteds.us/users/sign_in | grep -i "whiskey"
```

#### **3. Authentication Check**
```bash
# Test that auth is required
curl -s -o /dev/null -w "%{http_code}" https://whiskey.remoteds.us/whiskeys | grep "302"
```

#### **4. Database Connectivity Check**
```bash
# Via Rails console
ssh root@asterra.remoteds.us "cd /var/www/whiskey/current && RAILS_ENV=production bundle exec rails runner 'puts Whiskey.count'"
```

### **Automated Health Check Command**
```bash
# Run via manager.py
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python manager.py health-check --app whiskey"
```

This command should verify:
- ✅ Puma service is active
- ✅ App responds to HTTP requests
- ✅ Authentication is enforced
- ✅ Database is accessible
- ✅ ABV/Proof calculations work correctly

---

## 📚 Related Documentation

- **[Application Design](../application-design-documents/whiskey-management-system.md)** - Full architecture
- **[Deployment Guide](../deployment-guides/WHISKEY_DEPLOYMENT_GUIDE.md)** - Deployment procedures  
- **[Testing Strategies Index](README.md)** - Testing overview

---

**Last Updated**: November 1, 2025  
**Maintained By**: Development Team
