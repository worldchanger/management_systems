# Kanban System PostgreSQL Migration - Implementation Guide

**Version**: 1.0  
**Date**: October 29, 2025  
**Status**: ✅ **READY FOR IMPLEMENTATION**

---

## 📋 Overview

This document provides complete instructions for migrating the kanban/TODO system from a file-based (TODO.md) approach to a PostgreSQL-backed relational database system.

### **Why This Migration?**

**Problems with TODO.md approach:**
- ❌ Sync issues between local `docs/TODO.md` and production `/opt/hosting-api/TODO.md`
- ❌ No ACID compliance - file corruption risks
- ❌ No relational integrity or constraints
- ❌ Difficult to query, filter, and aggregate
- ❌ No audit trail or change history
- ❌ Concurrent access issues

**Benefits of PostgreSQL approach:**
- ✅ Single source of truth (database)
- ✅ Included in existing PostgreSQL backup system
- ✅ Relational integrity with foreign keys and constraints
- ✅ Efficient querying and filtering
- ✅ Automatic audit trail via triggers
- ✅ Proper concurrent access handling
- ✅ Scalable to thousands of tasks

---

## 🗂️ Files Created

All implementation files are in `docs/` folder:

1. **DATABASE_MIGRATION_KANBAN.sql** - Database schema and migration
2. **kanban_models.py** - SQLAlchemy models
3. **kanban_api_routes_postgres.py** - Updated FastAPI routes
4. **test_kanban_postgres.py** - Comprehensive unit tests
5. **migrate_todo_to_postgres.py** - Migration script for existing TODO.md data
6. **KANBAN_POSTGRES_IMPLEMENTATION.md** - This implementation guide

---

## 📊 Database Schema

### **Main Tables**

**kanban_tasks**
- Primary task storage with full metadata
- Constraints for data integrity
- Indexes for query performance

**kanban_task_history**
- Audit log for all task changes
- Automatic logging via database triggers

**kanban_tags** & **kanban_task_tags**
- Flexible tagging system (optional enhancement)

### **Key Features**
- Auto-incrementing primary keys
- Timestamp triggers for automatic updates
- Check constraints for valid values
- Foreign key relationships
- Comprehensive indexing

---

## 🚀 Implementation Steps

### **Step 1: Update Configuration**

**1.1 Update config.json** ✅ COMPLETED
```json
"hosting": {
  "subdomain": "hosting",
  "remote_root": "/opt/hosting-api",
  "database": "hosting_production",
  "description": "Hosting management FastAPI application with PostgreSQL-backed kanban system"
}
```

**1.2 Update .secrets.json**
Add database credentials for hosting_production:
```json
{
  "databases": {
    "hosting_production": {
      "username": "postgres",
      "password": "your-secure-password",
      "host": "localhost",
      "port": 5432,
      "database": "hosting_production"
    }
  }
}
```

### **Step 2: Create Database**

**2.1 Connect to PostgreSQL on production server**
```bash
ssh root@asterra.remoteds.us
sudo -u postgres psql
```

**2.2 Run migration script**
```bash
# Copy migration script to server
scp docs/DATABASE_MIGRATION_KANBAN.sql root@asterra.remoteds.us:/tmp/

# On server, run migration
sudo -u postgres psql -f /tmp/DATABASE_MIGRATION_KANBAN.sql
```

**2.3 Verify database creation**
```sql
\c hosting_production
\dt  -- List tables
SELECT * FROM kanban_tasks LIMIT 5;
```

### **Step 3: Update Hosting Management System Code**

**3.1 Install Python dependencies**
```bash
cd hosting-management-system
pip install sqlalchemy psycopg2-binary alembic
```

Update `requirements.txt`:
```
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
```

**3.2 Copy model files**
```bash
# Create models directory if it doesn't exist
mkdir -p hosting-management-system/models

# Copy SQLAlchemy models
cp docs/kanban_models.py hosting-management-system/models/kanban.py
```

**3.3 Update FastAPI routes**
```bash
# Backup existing routes
cp hosting-management-system/routes/kanban_api_routes.py \
   hosting-management-system/routes/kanban_api_routes.py.backup

# Replace with PostgreSQL version
cp docs/kanban_api_routes_postgres.py \
   hosting-management-system/routes/kanban_api_routes.py
```

**3.4 Update database connection configuration**

Create `hosting-management-system/config/database.py`:
```python
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load database credentials from .secrets.json
secrets_path = "/Users/bpauley/Projects/mangement-systems/.secrets.json"
with open(secrets_path) as f:
    secrets = json.load(f)

db_config = secrets["databases"]["hosting_production"]
DATABASE_URL = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **Step 4: Migrate Existing TODO.md Data**

**4.1 Run migration script locally (dry run)**
```bash
python docs/migrate_todo_to_postgres.py /opt/hosting-api/TODO.md --dry-run
```

**4.2 Run actual migration**
```bash
# On production server
python docs/migrate_todo_to_postgres.py /opt/hosting-api/TODO.md
```

This will:
- Parse existing TODO.md file
- Import all tasks to PostgreSQL
- Preserve all metadata (created_at, epic, etc.)
- Create backup of original TODO.md

### **Step 5: Testing**

**5.1 Run unit tests locally**
```bash
cd hosting-management-system
pytest tests/test_kanban_postgres.py -v
```

**5.2 Test API endpoints**
```bash
# Health check
curl http://localhost:8000/api/v1/kanban/health

# Get JWT token (update with actual credentials)
TOKEN=$(curl -X POST http://localhost:8000/login \
  -d "username=admin" -d "password=YOUR_PASSWORD" -d "next=/" \
  | jq -r '.token')

# List tasks
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/kanban/tasks

# Create test task
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test task","priority":"high","section":"To Do"}' \
  http://localhost:8000/api/v1/kanban/tasks

# Get stats
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/kanban/stats
```

**5.3 Test web interface**
- Navigate to https://hosting.remoteds.us/kanban
- Verify all tasks display correctly
- Test drag-and-drop functionality
- Test creating, editing, deleting tasks
- Verify filtering and sorting works

### **Step 6: Deploy to Production**

**6.1 Update hosting system code**
```bash
cd hosting-management-system
git add .
git commit -m "Migrate kanban system to PostgreSQL backend"
git push
```

**6.2 Deploy via manager.py**
```bash
cd /Users/bpauley/Projects/mangement-systems
python hosting-management-system/manager.py deploy-hosting-api --project-dir /opt/hosting-api
```

**6.3 Restart hosting API service**
```bash
ssh root@asterra.remoteds.us
systemctl restart hosting-api
systemctl status hosting-api
```

**6.4 Verify production deployment**
```bash
curl https://hosting.remoteds.us/api/v1/kanban/health
```

### **Step 7: Cleanup**

**7.1 Archive old TODO.md files**
```bash
# On production server
mv /opt/hosting-api/TODO.md /opt/hosting-api/TODO.md.archive
mv /opt/hosting-api/TODO.md.backup /opt/hosting-api/archive/

# Locally
rm docs/TODO.md  # No longer needed
```

**7.2 Remove old file-based code**
```bash
# Backup then remove old todo_manager.py
mv hosting-management-system/todo_manager.py \
   hosting-management-system/archive/todo_manager.py.backup

# Remove old todos.py if not used elsewhere
mv hosting-management-system/core/todos.py \
   hosting-management-system/archive/todos.py.backup
```

---

## 🧪 Testing Checklist

### **API Testing**
- [ ] Health check endpoint responds
- [ ] Authentication required for protected endpoints
- [ ] Create task successfully
- [ ] List tasks with various filters
- [ ] Update task fields
- [ ] Move task between sections
- [ ] Complete task (status + completed_at)
- [ ] Delete task
- [ ] Get statistics
- [ ] Pagination works correctly

### **Database Testing**
- [ ] Direct database connection works
- [ ] Constraints prevent invalid data
- [ ] Timestamps auto-update correctly
- [ ] Audit trail logs changes
- [ ] Indexes improve query performance
- [ ] Foreign keys maintain referential integrity

### **Web Interface Testing**
- [ ] Kanban board displays all sections
- [ ] Tasks render with correct data
- [ ] Drag-and-drop moves tasks
- [ ] Create new task via UI
- [ ] Edit task inline
- [ ] Delete task with confirmation
- [ ] Filter by priority/epic/section
- [ ] Real-time updates (if implemented)

### **Integration Testing**
- [ ] Complete task lifecycle (create → move → complete → delete)
- [ ] Multiple users can access simultaneously
- [ ] Changes persist after server restart
- [ ] Backup/restore procedures work
- [ ] Performance acceptable with 1000+ tasks

---

## 🔧 Troubleshooting

### **Database Connection Issues**
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Check connection
psql -U postgres -d hosting_production -c "SELECT 1"

# Check database exists
psql -U postgres -c "\l" | grep hosting_production
```

### **Migration Issues**
```bash
# Check for existing tasks
psql -U postgres -d hosting_production -c "SELECT COUNT(*) FROM kanban_tasks"

# View recent tasks
psql -U postgres -d hosting_production -c "SELECT id, content, section FROM kanban_tasks ORDER BY created_at DESC LIMIT 10"

# Check for duplicate content
psql -U postgres -d hosting_production -c "SELECT content, COUNT(*) FROM kanban_tasks GROUP BY content HAVING COUNT(*) > 1"
```

### **API Issues**
```bash
# Check hosting API logs
journalctl -u hosting-api -n 50 -f

# Check database connectivity from Python
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:password@localhost/hosting_production'); print(engine.execute('SELECT 1').scalar())"

# Test endpoint directly
curl -v http://localhost:8000/api/v1/kanban/health
```

---

## 📊 Performance Considerations

### **Indexing**
All critical fields are indexed:
- `section` - For filtering tasks by column
- `status` - For filtering active vs completed
- `priority` - For sorting by priority
- `created_at` - For chronological ordering
- `epic` - For project grouping

### **Query Optimization**
- Use `limit` and `offset` for pagination
- Filter at database level, not application level
- Use appropriate indexes for common queries
- Monitor slow queries with `EXPLAIN ANALYZE`

### **Scaling**
- Current schema supports 10,000+ tasks efficiently
- Connection pooling configured for concurrent users
- Can add read replicas if needed in future

---

## 🔒 Security Considerations

1. **Database Credentials**
   - Stored in .secrets.json (gitignored)
   - Never committed to version control
   - Environment variables in production

2. **API Authentication**
   - JWT tokens required for all endpoints
   - Tokens expire after configured duration
   - HTTPS enforced in production

3. **SQL Injection Prevention**
   - SQLAlchemy ORM prevents SQL injection
   - Parameterized queries used throughout
   - Input validation via Pydantic models

4. **Access Control**
   - Only authenticated users can access API
   - Web interface requires login
   - Database user has minimal required permissions

---

## 📝 Rollback Plan

If issues arise, rollback procedure:

1. **Restore previous hosting-api code**
```bash
cd hosting-management-system
git revert HEAD
git push
python manager.py deploy-hosting-api --project-dir /opt/hosting-api
```

2. **Restore TODO.md file**
```bash
cp /opt/hosting-api/TODO.md.backup /opt/hosting-api/TODO.md
```

3. **Restart with old code**
```bash
systemctl restart hosting-api
```

4. **Export database for future retry**
```bash
pg_dump -U postgres hosting_production > hosting_production_backup.sql
```

---

## ✅ Success Criteria

Migration is successful when:
- ✅ All existing TODO tasks migrated to database
- ✅ Web interface displays all tasks correctly
- ✅ API endpoints respond with correct data
- ✅ Tasks can be created, updated, moved, deleted
- ✅ No sync issues between systems
- ✅ Backups include kanban data
- ✅ Performance is acceptable (<100ms for list queries)
- ✅ All unit tests passing
- ✅ Documentation updated

---

## 📞 Support

For issues or questions:
1. Check logs: `journalctl -u hosting-api -f`
2. Review database: `psql -U postgres hosting_production`
3. Test API: `curl -v http://localhost:8000/api/v1/kanban/health`
4. Check this implementation guide
5. Review agents.md for system rules

---

**Implementation Complete!** 🎉

The kanban system is now backed by a proper relational database with all the benefits of ACID compliance, proper backups, and scalable architecture.
