# Whiskey App Deployment - Infrastructure Improvements

## Current Issues
1. ❌ Database user not created before deployment
2. ❌ No proper cleanup/teardown method
3. ❌ Migrations fail because user can't create database
4. ❌ Assets compilation not integrated into deploy flow

## Required Changes to manager.py

### 1. Add cleanup_app() method
```python
def cleanup_app(self, key: str) -> None:
    """Remove an app completely from production"""
    - Stop and disable systemd service
    - Remove /var/www/{app} directory
    - Remove nginx config from sites-enabled/available
    - Remove SSL certificates
    - Drop PostgreSQL database and user
    - Remove from backup scripts
```

### 2. Add setup_database_user() method
```python
def setup_database_user(self, app_key: str, db_password: str) -> None:
    """Create PostgreSQL user/role with CREATE DATABASE privilege"""
    - Connect as postgres superuser
    - CREATE ROLE {app_key}_user WITH LOGIN PASSWORD '{db_password}' CREATEDB;
    - Grant necessary privileges
```

### 3. Modify deploy_app() to accept setup flag
```python
def deploy_app(self, key: str, branch: str = "main", setup: bool = False) -> None:
    if setup:
        # First time setup
        self.setup_database_user(key, db_password)
    
    # Existing deploy flow
    self._ensure_directories(conn, app)
    self._sync_repo(conn, app, branch)
    self._link_shared(conn, app)
    self._bundle_install(conn, app)
    
    # Deploy secrets BEFORE migrations
    self._deploy_secrets(key)
    
    # Now run migrations (can create database)
    self._run_migrations(conn, app)
    self._precompile_assets(conn, app)
    
    # Rest of setup
    self._write_puma_config(conn, app)
    self._write_systemd_service(conn, app)
    self._write_nginx_config(conn, app)
    self._reload_services(conn, app)
```

### 4. Add CLI commands
```python
@cli.command("cleanup-app")
@click.option("--app", required=True)
def cleanup_app_cmd(manager, app_key):
    """Remove app from production"""
    
@cli.command("deploy")
@click.option("--app", required=True)
@click.option("--branch", default="main")
@click.option("--setup", is_flag=True, help="First-time setup for new app")
def deploy_cmd(manager, app_key, branch, setup):
    """Deploy app (use --setup for first time)"""
```

## Deployment Flow for New App

```bash
# 1. Clean up existing broken deployment
python manager.py cleanup-app --app whiskey

# 2. Deploy with setup flag (creates DB user, etc.)
python manager.py deploy --app whiskey --branch main --setup

# 3. Verify deployment
curl -I https://whiskey.remoteds.us
```

## Database Configuration

The database.yml should read password from environment:
```yaml
production:
  adapter: postgresql
  database: whiskey_management_system_production
  username: whiskey_user  # Created by setup
  password: <%= ENV['WHISKEY_DATABASE_PASSWORD'] %>
  host: localhost
```

## Status
- [ ] Add cleanup_app method
- [ ] Add setup_database_user method  
- [ ] Modify deploy_app for setup flag
- [ ] Add CLI commands
- [ ] Test cleanup on whiskey
- [ ] Test full setup+deploy
- [ ] Update local_rails_manager.py
- [ ] Document in agents.md
