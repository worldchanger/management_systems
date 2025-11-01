# Cigar Management System - Testing Strategy

**Last Updated**: November 1, 2025  
**Version**: 2.0 (Refactored - Links to Tests)  
**Application**: Cigar Management System  
**Production URL**: https://cigars.remoteds.us  
**Framework**: Ruby on Rails 7.2.2 with RSpec

---

## 📋 Testing Status

**Current Test Results**:
- **Total Examples**: 197
- **Failures**: 0
- **Pending**: 85 (view specs)
- **Coverage**: Models, Controllers, API, Integration tests all passing

**Test Command**: `cd cigar-management-system && bundle exec rspec`

---

## 🧪 Test Files and GitHub Links

### **Model Tests**

#### Cigar Model
- **File**: [spec/models/cigar_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/models/cigar_spec.rb)
- **Tests**: Associations, validations, business logic (total_quantity, locations)
- **Run**: `bundle exec rspec spec/models/cigar_spec.rb`
- **Dependencies**: Brand, HumidorCigar factories

#### Cigar Deletion Tests
- **File**: [spec/models/cigar_deletion_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/models/cigar_deletion_spec.rb)
- **Tests**: Deletion validation (can't delete with inventory)
- **Run**: `bundle exec rspec spec/models/cigar_deletion_spec.rb`
- **Expected**: 5 examples, 0 failures

#### Brand Model
- **File**: [spec/models/brand_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/models/brand_spec.rb)
- **Tests**: Associations, validations
- **Run**: `bundle exec rspec spec/models/brand_spec.rb`

#### Location Model
- **File**: [spec/models/location_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/models/location_spec.rb)
- **Tests**: Associations, validations
- **Run**: `bundle exec rspec spec/models/location_spec.rb`

#### Humidor Model
- **File**: [spec/models/humidor_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/models/humidor_spec.rb)
- **Tests**: Associations, validations, capacity calculations
- **Run**: `bundle exec rspec spec/models/humidor_spec.rb`

---

### **Request/Controller Tests**

#### All Request Specs
- **Location**: [spec/requests/](https://github.com/worldchanger/cigar-management-system/tree/main/spec/requests)
- **Files**:
  - `brands_spec.rb` - Brand CRUD with authentication
  - `cigars_spec.rb` - Cigar CRUD with authentication
  - `locations_spec.rb` - Location CRUD with authentication
  - `humidors_spec.rb` - Humidor CRUD with authentication
  - `cigar_types_spec.rb` - CigarType CRUD with authentication
  - `strengths_spec.rb` - Strength CRUD with authentication
  - `users_spec.rb` - User management with authentication
  - `humidor_cigars_spec.rb` - Inventory management
  - `ocr_scans_spec.rb` - OCR scanning endpoints
- **Run All**: `bundle exec rspec spec/requests/`
- **Expected**: 64 examples, 0 failures
- **Description**: All specs test both unauthenticated (302 redirect) and authenticated (200 success) states

#### Cigar Deletion Controller Tests
- **File**: [spec/controllers/cigars_controller_deletion_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/controllers/cigars_controller_deletion_spec.rb)
- **Tests**: DELETE action with inventory validation
- **Run**: `bundle exec rspec spec/controllers/cigars_controller_deletion_spec.rb`
- **Expected**: 5 examples, 0 failures

---

### **API Tests**

#### Public Inventory API
- **File**: [spec/requests/api_request_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/requests/api_request_spec.rb)
- **Tests**: JSON API endpoint `/api/inventory/:token`
- **Run**: `bundle exec rspec spec/requests/api_request_spec.rb`
- **Expected**: 5 examples, 0 failures
- **Dependencies**: Requires ENV['CIGAR_API_TOKEN'] set in tests

#### API Inventory Spec
- **File**: [spec/requests/api/inventory_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/requests/api/inventory_spec.rb)
- **Tests**: API authentication and response format
- **Run**: `bundle exec rspec spec/requests/api/inventory_spec.rb`
- **Expected**: 1 example, 0 failures

---

### **Service Tests**

#### OCR Service
- **File**: [spec/services/ocr_service_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/services/ocr_service_spec.rb)
- **Tests**: OCR text extraction, brand matching, cigar recognition
- **Run**: `bundle exec rspec spec/services/ocr_service_spec.rb`
- **Status**: 17 pending (requires test image file)
- **Dependencies**: OPENROUTER_API_KEY environment variable

---

### **View Tests**

#### Humidor Cigars Views
- **Files**: 
  - [spec/views/humidor_cigars/index_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/views/humidor_cigars/index_spec.rb)
  - [spec/views/humidor_cigars/new_spec.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/views/humidor_cigars/new_spec.rb)
- **Tests**: Rendering inventory lists, form display
- **Run**: `bundle exec rspec spec/views/humidor_cigars/`
- **Expected**: 6 examples, 0 failures

**Note**: Most view specs (85 total) are pending and need implementation or deletion.

---

## 🧰 Test Dependencies

### **Gemfile Test Group**
- **File**: [Gemfile](https://github.com/worldchanger/cigar-management-system/blob/main/Gemfile)
- **Gems**: rspec-rails, factory_bot_rails, capybara, selenium-webdriver

### **Factories**
- **Location**: [spec/factories/](https://github.com/worldchanger/cigar-management-system/tree/main/spec/factories)
- **Files**: cigars.rb, brands.rb, locations.rb, humidors.rb, humidor_cigars.rb, users.rb

### **Rails Helper**
- **File**: [spec/rails_helper.rb](https://github.com/worldchanger/cigar-management-system/blob/main/spec/rails_helper.rb)
- **Includes**: FactoryBot syntax methods, Devise test helpers

---

## 🚀 Running Tests

### **All Tests**
```bash
cd cigar-management-system && bundle exec rspec
```

### **Specific Test File**
```bash
bundle exec rspec spec/models/cigar_spec.rb
```

### **With Documentation Format**
```bash
bundle exec rspec --format documentation
```

### **Only Failures**
```bash
bundle exec rspec --only-failures
```

---

## 🔍 Local curl Testing

### **Test Script**
- **File**: `/test-apps-local.sh` (project root)
- **Run**: `./test-apps-local.sh`
- **Tests**: Health checks, login pages, authentication redirects
- **Endpoints Tested**: /up, /users/sign_in, /dashboard, /cigars, /brands, /locations, /humidors, /cigar_types, /strengths, /humidor_cigars, /users

### **Expected Results**
- `/up` - 200 OK
- `/users/sign_in` - 200 OK
- All other endpoints - 302 Redirect (auth required)

---

## 🌐 Remote Production Testing

### **Test Script**
- **File**: `/test-apps-remote.sh` (project root)
- **Run**: `./test-apps-remote.sh`
- **URL**: https://cigars.remoteds.us
- **Same endpoints as local tests**

### **Expected Results**
- All endpoints return proper status codes
- SSL certificate valid
- Authentication properly enforced

---

## 📊 Test Data

### **Factory Bot Syntax**
```ruby
# Create a cigar with associated brand
cigar = create(:cigar, cigar_name: 'Undercrown')

# Build without saving
brand = build(:brand, name: 'Drew Estate')

# Create with associations
humidor_cigar = create(:humidor_cigar, 
  humidor: create(:humidor),
  cigar: create(:cigar),
  quantity: 10
)
```

### **Test Database**
- Automatically managed by RSpec
- Uses Rails test environment
- Cleaned between tests via transactional fixtures

---

## ✅ Test Checklist

Before deployment, ensure:
- [ ] All unit tests passing (`bundle exec rspec`)
- [ ] Local curl tests passing (`./test-apps-local.sh`)
- [ ] Code committed and pushed to GitHub
- [ ] Remote curl tests passing after deployment (`./test-apps-remote.sh`)

---

## 📚 Related Documentation

- [Application Design Document](../application-design-documents/cigar-management-system.md)
- [Deployment Quick Reference](../deployment-guides/DEPLOYMENT_QUICK_REFERENCE.md)
- [Main Project README](../../README.md)
