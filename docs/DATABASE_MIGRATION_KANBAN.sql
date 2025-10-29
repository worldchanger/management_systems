-- ============================================================================
-- Kanban System Database Migration
-- Migrates from TODO.md file-based system to PostgreSQL database
-- Database: hosting_production
-- ============================================================================

-- Create the hosting_production database if it doesn't exist
-- (Run this manually as postgres superuser if needed)
-- CREATE DATABASE hosting_production OWNER postgres;

-- Connect to the database
\c hosting_production

-- ============================================================================
-- Main Tables
-- ============================================================================

-- Kanban tasks table
CREATE TABLE IF NOT EXISTS kanban_tasks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority VARCHAR(10) DEFAULT 'medium',
    owner VARCHAR(20) DEFAULT 'agent',
    section VARCHAR(50) NOT NULL DEFAULT 'Backlog',
    epic VARCHAR(100),
    area VARCHAR(50) DEFAULT 'general',
    occurrence_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    position INTEGER DEFAULT 0,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'completed')),
    CONSTRAINT valid_priority CHECK (priority IN ('high', 'medium', 'low')),
    CONSTRAINT valid_section CHECK (section IN ('Backlog', 'To Do', 'In Progress', 'Completed')),
    CONSTRAINT valid_owner CHECK (owner IN ('user', 'agent'))
);

-- Task history/audit log table
CREATE TABLE IF NOT EXISTS kanban_task_history (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES kanban_tasks(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(50) DEFAULT 'agent',
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Task tags for flexible categorization
CREATE TABLE IF NOT EXISTS kanban_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#6c757d',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Task-tag many-to-many relationship
CREATE TABLE IF NOT EXISTS kanban_task_tags (
    task_id INTEGER REFERENCES kanban_tasks(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES kanban_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_kanban_section ON kanban_tasks(section);
CREATE INDEX IF NOT EXISTS idx_kanban_status ON kanban_tasks(status);
CREATE INDEX IF NOT EXISTS idx_kanban_priority ON kanban_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_kanban_created_at ON kanban_tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_kanban_epic ON kanban_tasks(epic);
CREATE INDEX IF NOT EXISTS idx_kanban_position ON kanban_tasks(section, position);
CREATE INDEX IF NOT EXISTS idx_history_task_id ON kanban_task_history(task_id);
CREATE INDEX IF NOT EXISTS idx_history_changed_at ON kanban_task_history(changed_at DESC);

-- ============================================================================
-- Triggers for Auto-updating Timestamps
-- ============================================================================

CREATE OR REPLACE FUNCTION update_kanban_task_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_kanban_task_timestamp ON kanban_tasks;
CREATE TRIGGER trigger_update_kanban_task_timestamp
    BEFORE UPDATE ON kanban_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_kanban_task_timestamp();

-- ============================================================================
-- Functions for Task Management
-- ============================================================================

-- Function to log task changes
CREATE OR REPLACE FUNCTION log_kanban_task_change()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        -- Log section changes
        IF OLD.section != NEW.section THEN
            INSERT INTO kanban_task_history (task_id, action, old_value, new_value)
            VALUES (NEW.id, 'section_changed', OLD.section, NEW.section);
        END IF;
        
        -- Log status changes
        IF OLD.status != NEW.status THEN
            INSERT INTO kanban_task_history (task_id, action, old_value, new_value)
            VALUES (NEW.id, 'status_changed', OLD.status, NEW.status);
            
            -- Set completed_at when status changes to completed
            IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
                NEW.completed_at = CURRENT_TIMESTAMP;
            END IF;
        END IF;
        
        -- Log priority changes
        IF OLD.priority != NEW.priority THEN
            INSERT INTO kanban_task_history (task_id, action, old_value, new_value)
            VALUES (NEW.id, 'priority_changed', OLD.priority, NEW.priority);
        END IF;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO kanban_task_history (task_id, action, new_value)
        VALUES (NEW.id, 'created', NEW.content);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_log_kanban_task_change ON kanban_tasks;
CREATE TRIGGER trigger_log_kanban_task_change
    AFTER INSERT OR UPDATE ON kanban_tasks
    FOR EACH ROW
    EXECUTE FUNCTION log_kanban_task_change();

-- ============================================================================
-- Default Tags
-- ============================================================================

INSERT INTO kanban_tags (name, color) VALUES
    ('bug', '#dc3545'),
    ('feature', '#28a745'),
    ('documentation', '#17a2b8'),
    ('urgent', '#ffc107'),
    ('infrastructure', '#6610f2')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- Permissions
-- ============================================================================

-- Grant permissions (adjust user as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Insert a few sample tasks
INSERT INTO kanban_tasks (content, priority, section, epic, created_at) VALUES
    ('Set up PostgreSQL database for kanban system', 'high', 'Completed', 'Hosting Management System', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('Create database migration scripts', 'high', 'Completed', 'Hosting Management System', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('Update FastAPI to use PostgreSQL', 'high', 'In Progress', 'Hosting Management System', CURRENT_TIMESTAMP - INTERVAL '12 hours'),
    ('Create unit tests for kanban API', 'high', 'In Progress', 'Hosting Management System', CURRENT_TIMESTAMP - INTERVAL '6 hours'),
    ('Migrate existing TODO.md data', 'medium', 'To Do', 'Hosting Management System', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check table creation
SELECT 'Tables created:' as status;
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE 'kanban%';

-- Check indexes
SELECT 'Indexes created:' as status;
SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND tablename LIKE 'kanban%';

-- Check sample data
SELECT 'Sample tasks:' as status;
SELECT id, content, section, priority FROM kanban_tasks ORDER BY id;

-- Show task distribution by section
SELECT 'Task distribution:' as status;
SELECT section, COUNT(*) as count FROM kanban_tasks GROUP BY section ORDER BY section;

COMMIT;
