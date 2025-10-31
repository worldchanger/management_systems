# Whiskey Management System

## Overview
The Whiskey Management System is a Ruby on Rails 7.2.2 application designed to help enthusiasts manage their whiskey collection with detailed tracking of bottles, brands, locations, and whiskey characteristics.

## Core Features

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

## Technical Architecture

### Database Schema
```
- Users (Devise authentication)
- Locations (name, description, address)
- Brands (name, description, website_url, country)
- WhiskeyTypes (name, description)
- Whiskeys (name, description, mash_bill, abv, proof, age, quantity)
  ├── belongs_to :brand
  ├── belongs_to :whiskey_type
  ├── belongs_to :location (optional)
  └── has_one_attached :bottle_image
```

### Technology Stack
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
