#!/usr/bin/env python3
"""
Add global admin user to .secrets.json and PostgreSQL
"""

import json
from pathlib import Path

# Configuration
SECRETS_PATH = Path("/Users/bpauley/Projects/mangement-systems/.secrets.json")
USERNAME = "bpauley"
EMAIL = "brianmpauley@icloud.com"
PASSWORD = "3e9zUL3BVrMCeXDoW8JbLurv$&h7Lqwg"

def update_secrets():
    """Add global admin user to .secrets.json"""
    
    # Read existing secrets
    with open(SECRETS_PATH, 'r') as f:
        secrets = json.load(f)
    
    # Create global_admin_users section if it doesn't exist
    if 'global_admin_users' not in secrets:
        secrets['global_admin_users'] = {}
    
    # Add the admin user
    secrets['global_admin_users'][USERNAME] = {
        "email": EMAIL,
        "password": PASSWORD,
        "postgres_superuser": True,
        "cigar_app_admin": True,
        "hosting_app_admin": True,
        "tobacco_app_admin": False  # Will add later
    }
    
    # Backup original
    backup_path = SECRETS_PATH.with_suffix('.json.backup-admin')
    with open(backup_path, 'w') as f:
        json.dump(secrets, f, indent=2)
    
    # Write updated secrets
    with open(SECRETS_PATH, 'w') as f:
        json.dump(secrets, f, indent=2)
    
    print("✅ Updated .secrets.json")
    print(f"\n📋 Admin User Created:")
    print(f"   Username: {USERNAME}")
    print(f"   Email: {EMAIL}")
    print(f"   Password: {PASSWORD}")
    print(f"   PostgreSQL: Superuser access")
    print(f"   Cigar App: Admin")
    print(f"   Hosting App: Admin")
    print(f"\n⚠️  SAVE THIS PASSWORD!")
    
    return PASSWORD

if __name__ == "__main__":
    print("=" * 80)
    print("Global Admin User Setup")
    print("=" * 80)
    print()
    
    password = update_secrets()
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("\n1. Create PostgreSQL superuser:")
    print(f"   ssh root@asterra.remoteds.us")
    print(f"   sudo -u postgres psql")
    print(f"   CREATE USER {USERNAME} WITH SUPERUSER PASSWORD '{password}';")
    print(f"   \\q")
    print()
    print("2. Configure PostgreSQL for remote access:")
    print("   Edit /etc/postgresql/17/main/postgresql.conf")
    print("   Set: listen_addresses = '*'")
    print()
    print("   Edit /etc/postgresql/17/main/pg_hba.conf")
    print("   Add: host all all 0.0.0.0/0 md5")
    print()
    print("   systemctl restart postgresql")
    print()
    print("3. Test remote connection:")
    print(f"   psql -h asterra.remoteds.us -U {USERNAME} -d hosting_production")
    print()
