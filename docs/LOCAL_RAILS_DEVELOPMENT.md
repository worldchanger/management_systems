# Local Rails Development Guide

This guide explains how to run all three Rails applications concurrently on your local machine for development and testing.

## Overview

The management system consists of four Rails applications:
- **Cigar Management System** - Runs on port 3001
- **Tobacco Management System** - Runs on port 3002
- **Whiskey Management System** - Runs on port 3003
- **QA Test Repo** - Runs on port 3004

All three applications can run simultaneously on different ports for integrated development and testing.

## Prerequisites

- Ruby 3.4.7 (managed via mise)
- PostgreSQL database server running
- Python 3.x for the local Rails manager script
- psutil Python package (`pip install psutil`)

## Quick Start

### Using the Local Rails Manager (Recommended)

The `local_rails_manager.py` script provides easy management of all Rails apps.

```bash
cd /Users/bpauley/Projects/mangement-systems/hosting-management-system
```

**Start all applications:**
```bash
python local_rails_manager.py start
```

**Check status:**
```bash
python local_rails_manager.py status
```

**Stop all applications:**
```bash
python local_rails_manager.py stop
```

**Restart all applications:**
```bash
python local_rails_manager.py restart
```

**Force stop (if graceful stop fails):**
```bash
python local_rails_manager.py stop --force
```

### Managing Individual Apps

**Start a specific app:**
```bash
python local_rails_manager.py start --app cigar
python local_rails_manager.py start --app tobacco  
python local_rails_manager.py start --app qa
```

**Stop a specific app:**
```bash
python local_rails_manager.py stop --app cigar
```

**Restart a specific app:**
```bash
python local_rails_manager.py restart --app tobacco
```

**Check status of a specific app:**
```bash
python local_rails_manager.py status --app qa
```

## Manual Start (Alternative Method)

If you prefer to start applications manually:

```bash
# Cigar Management System
cd /Users/bpauley/Projects/mangement-systems/cigar-management-system
rails server -p 3001 -d

# Tobacco Management System
cd /Users/bpauley/Projects/mangement-systems/tobacco-management-system
rails server -p 3002 -d

# QA Test Repo
cd /Users/bpauley/Projects/mangement-systems/qa-test-repo
rails server -p 3003 -d
```

## Accessing the Applications

Once started, access the applications at:

- **Cigar Management**: http://localhost:3001
- **Tobacco Management**: http://localhost:3002
- **QA Test Repo**: http://localhost:3003

## Database Setup

### First Time Setup

Each application requires database setup before first run:

```bash
# Cigar Management System
cd /Users/bpauley/Projects/mangement-systems/cigar-management-system
rails db:create db:migrate db:seed

# Tobacco Management System
cd /Users/bpauley/Projects/mangement-systems/tobacco-management-system
rails db:create db:migrate db:seed

# QA Test Repo
cd /Users/bpauley/Projects/mangement-systems/qa-test-repo
rails db:create db:migrate db:seed
```

### Resetting Databases

To reset a database (WARNING: Destroys all data):

```bash
rails db:drop db:create db:migrate db:seed
```

## Default User Accounts

After running `db:seed`, you can login with:

**Cigar Management System:**
- Email: admin@example.com
- Password: password123

**Tobacco Management System:**
- Email: admin@example.com
- Password: password123

**QA Test Repo:**
- Email: admin@remoteds.us
- Password: password123

## Running Tests

### RSpec Tests

```bash
# Run all tests
bundle exec rspec

# Run specific test file
bundle exec rspec spec/models/location_spec.rb

# Run with documentation format
bundle exec rspec --format documentation

# Run tests for specific directory
bundle exec rspec spec/models/
```

### Test Database Setup

```bash
# Prepare test database
RAILS_ENV=test rails db:create db:migrate

# Reset test database
RAILS_ENV=test rails db:reset
```

## Troubleshooting

### Port Already in Use

If a port is already in use, stop the application using that port:

```bash
# Find process using port (e.g., 3001)
lsof -ti:3001

# Kill the process
kill -9 $(lsof -ti:3001)

# Or use the manager with force stop
python local_rails_manager.py stop --force
```

### Application Won't Start

1. Check if PostgreSQL is running:
```bash
pg_isready
```

2. Check database configuration in `config/database.yml`

3. Ensure all gems are installed:
```bash
bundle install
```

4. Check Rails logs:
```bash
tail -f log/development.log
```

### Stale PID Files

If an app shows as running but isn't responding:

```bash
# Remove stale PID file
rm tmp/pids/server.pid

# Restart the app
python local_rails_manager.py restart --app <app_name>
```

### Permission Errors

Ensure you have write permissions in the application directory:

```bash
chmod -R u+w tmp/ log/
```

## Development Workflow

### Typical Development Session

1. **Start all applications:**
   ```bash
   python local_rails_manager.py start
   ```

2. **Check they're all running:**
   ```bash
   python local_rails_manager.py status
   ```

3. **Make code changes** in your editor

4. **Restart specific app after changes:**
   ```bash
   python local_rails_manager.py restart --app cigar
   ```

5. **Run tests:**
   ```bash
   cd cigar-management-system
   bundle exec rspec
   ```

6. **Stop all when done:**
   ```bash
   python local_rails_manager.py stop
   ```

### Working with Migrations

```bash
# Create a new migration
rails generate migration AddFieldToModel field:type

# Run migrations
rails db:migrate

# Rollback last migration
rails db:rollback

# Check migration status
rails db:migrate:status
```

### Console Access

Access Rails console for debugging:

```bash
# Development console
rails console

# Production console (use with caution)
RAILS_ENV=production rails console
```

## Best Practices

1. **Always run tests locally** before committing code
2. **Check application status** before starting to avoid port conflicts
3. **Use the manager script** for consistent app lifecycle management
4. **Run migrations** on all environments (development, test) after creating them
5. **Seed data regularly** to ensure you have realistic test data
6. **Monitor logs** when debugging issues
7. **Clean up** stale processes and PID files if apps won't start

## Additional Resources

- [Rails Guides](https://guides.rubyonrails.org/)
- [RSpec Documentation](https://rspec.info/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Support

For issues or questions about local development:
1. Check the troubleshooting section above
2. Review application logs in `log/development.log`
3. Refer to the main `agents.md` documentation
4. Check the `/docs` folder for additional guides
