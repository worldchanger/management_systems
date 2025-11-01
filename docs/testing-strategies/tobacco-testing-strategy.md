# Tobacco Management System - Testing Strategy

**Last Updated**: November 1, 2025  
**Version**: 2.0 (Refactored - Links to Tests)  
**Application**: Tobacco Management System  
**Production URL**: https://tobacco.remoteds.us  
**Framework**: Ruby on Rails 7.2.2 with RSpec

---

## 📋 Testing Status

**Current Test Results**:
- **RSpec Setup**: Complete
- **Total Examples**: 0 (tests need to be created)
- **Failures**: 0
- **Pending**: 0

**Test Command**: `cd tobacco-management-system && bundle exec rspec`

---

## 🚀 RSpec Setup (Completed November 1, 2025)

### **Gemfile Updates**
- **File**: [Gemfile](https://github.com/worldchanger/tobacco-management-system/blob/main/Gemfile)
- **Commit**: `8087107`
- **Added Gems**: 
  - rspec-rails (~> 6.1.0)
  - factory_bot_rails

### **Rails Helper Configuration**
- **File**: [spec/rails_helper.rb](https://github.com/worldchanger/tobacco-management-system/blob/main/spec/rails_helper.rb)
- **Includes**:
  - FactoryBot::Syntax::Methods
  - Devise::Test::IntegrationHelpers (for request specs)

### **Spec Helper**
- **File**: [spec/spec_helper.rb](https://github.com/worldchanger/tobacco-management-system/blob/main/spec/spec_helper.rb)
- **Status**: Generated with RSpec defaults

---

## 📝 Tests To Be Created

### **Model Tests Needed**

#### TobaccoProduct Model
- **Path**: `spec/models/tobacco_product_spec.rb`
- **Tests Needed**: 
  - Associations (brand, blends)
  - Validations (name, type, brand presence)
  - Aging calculations

#### Brand Model
- **Path**: `spec/models/brand_spec.rb`
- **Tests Needed**:
  - Association with tobacco products
  - Name validation

#### Blend Model
- **Path**: `spec/models/blend_spec.rb`
- **Tests Needed**:
  - Associations with tobacco products
  - Validation rules

---

### **Controller/Request Tests Needed**

#### TobaccoProducts Controller
- **Path**: `spec/requests/tobacco_products_spec.rb`
- **Tests Needed**:
  - Authentication redirects
  - CRUD operations
  - Index, show, new, edit endpoints

#### Brands Controller
- **Path**: `spec/requests/brands_spec.rb`
- **Tests Needed**:
  - Authentication redirects
  - CRUD operations

#### Dashboard
- **Path**: `spec/requests/dashboard_spec.rb`
- **Tests Needed**:
  - Authentication redirect
  - Successful render when authenticated

---

## 🧰 Factory Setup Needed

### **Factories To Create**

#### TobaccoProduct Factory
- **Path**: `spec/factories/tobacco_products.rb`
- **Attributes**: name, tobacco_type, brand_id, purchase_date, aging_start_date

#### Brand Factory
- **Path**: `spec/factories/brands.rb`
- **Attributes**: name, description

#### User Factory
- **Path**: `spec/factories/users.rb`
- **Attributes**: email, password, password_confirmation

---

## 🔍 Local curl Testing

### **Test Script**
- **File**: `/test-apps-local.sh` (project root)
- **Endpoints**: /up, /users/sign_in, /dashboard, /tobacco_products, /brands
- **Port**: 3002

### **Current Results** (November 1, 2025)
- `/up` - 200 OK ✅
- `/users/sign_in` - 200 OK ✅
- `/dashboard` - 302 Redirect ✅
- `/tobacco_products` - 302 Redirect ✅
- `/brands` - 302 Redirect ✅

---

## 🌐 Remote Production Testing

### **Test Script**
- **File**: `/test-apps-remote.sh` (project root)
- **URL**: https://tobacco.remoteds.us
- **Tests**: Same endpoints as local

### **Current Results** (November 1, 2025)
- All 5 endpoints passing ✅

---

## 🚀 Running Tests

### **Run All Tests** (when created)
```bash
cd tobacco-management-system && bundle exec rspec
```

### **Run Specific Test**
```bash
bundle exec rspec spec/models/tobacco_product_spec.rb
```

### **Generate Test for Model**
```bash
rails generate rspec:model TobaccoProduct
```

### **Generate Test for Controller**
```bash
rails generate rspec:request TobaccoProducts
```

---

## ✅ Current Status Checklist

Setup Complete:
- [x] RSpec installed and configured
- [x] FactoryBot added to Gemfile
- [x] rails_helper configured with Devise helpers
- [x] App deployed to production
- [x] Local curl tests passing (5/5)
- [x] Remote curl tests passing (5/5)

Tests To Create:
- [ ] Model tests for TobaccoProduct, Brand, Blend
- [ ] Request specs for all controllers
- [ ] Factories for all models
- [ ] Feature/integration tests
- [ ] Achieve 85%+ code coverage

---

## 📚 Related Documentation

- [Application Design Document](../application-design-documents/tobacco-management-system.md)
- [Deployment Quick Reference](../deployment-guides/DEPLOYMENT_QUICK_REFERENCE.md)
- [Main Project README](../../README.md)
