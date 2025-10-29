#!/usr/bin/env python3
"""
Script to safely add hosting_production database credentials to .secrets.json
Generates a secure random password for the PostgreSQL database.
"""

import json
import secrets
import string
from pathlib import Path


def generate_secure_password(length=32):
    """Generate a cryptographically secure random password."""
    # Use letters, digits, and safe special characters
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return password


def update_secrets_file():
    """Add hosting_production database credentials to .secrets.json"""
    
    secrets_path = Path("/Users/bpauley/Projects/mangement-systems/.secrets.json")
    
    if not secrets_path.exists():
        print(f"ERROR: {secrets_path} not found!")
        return False
    
    # Read existing secrets
    with open(secrets_path, 'r') as f:
        secrets_data = json.load(f)
    
    # Generate secure password
    db_password = generate_secure_password(32)
    
    # Create or update databases section
    if 'databases' not in secrets_data:
        secrets_data['databases'] = {}
    
    # Add hosting_production database credentials
    secrets_data['databases']['hosting_production'] = {
        "username": "postgres",
        "password": db_password,
        "host": "localhost",
        "port": 5432,
        "database": "hosting_production"
    }
    
    # Create backup of original file
    backup_path = secrets_path.with_suffix('.json.backup')
    with open(backup_path, 'w') as f:
        json.dump(secrets_data, f, indent=2)
    print(f"✅ Created backup: {backup_path}")
    
    # Write updated secrets
    with open(secrets_path, 'w') as f:
        json.dump(secrets_data, f, indent=2)
    
    print(f"✅ Updated {secrets_path}")
    print(f"\n📋 Database Credentials Added:")
    print(f"   Database: hosting_production")
    print(f"   Username: postgres")
    print(f"   Password: {db_password}")
    print(f"   Host: localhost")
    print(f"   Port: 5432")
    print(f"\n⚠️  IMPORTANT: Save this password! It's needed for database setup.")
    print(f"\n🔒 The password has been randomly generated and is cryptographically secure.")
    
    # Return the password for use in database creation
    return db_password


if __name__ == "__main__":
    print("=" * 80)
    print("PostgreSQL Database Credentials Generator")
    print("=" * 80)
    print()
    
    password = update_secrets_file()
    
    if password:
        print("\n" + "=" * 80)
        print("Next Steps:")
        print("=" * 80)
        print()
        print("1. On the production server, create the PostgreSQL user and database:")
        print()
        print("   sudo -u postgres psql")
        print(f"   CREATE USER postgres WITH PASSWORD '{password}';")
        print("   CREATE DATABASE hosting_production OWNER postgres;")
        print("   GRANT ALL PRIVILEGES ON DATABASE hosting_production TO postgres;")
        print("   \\q")
        print()
        print("2. Run the database migration script:")
        print("   sudo -u postgres psql -d hosting_production -f /tmp/DATABASE_MIGRATION_KANBAN.sql")
        print()
        print("3. Test database connectivity:")
        print(f"   psql -U postgres -d hosting_production -h localhost -c 'SELECT 1'")
        print()
