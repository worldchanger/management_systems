"""
Migration script to import existing TODO.md data into PostgreSQL.
Parses the TODO.md file and imports all tasks into the kanban_tasks table.

Usage:
    python migrate_todo_to_postgres.py /opt/hosting-api/TODO.md

This should be run once to migrate from file-based to database-backed system.
"""

import re
import json
import argparse
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional

# Database configuration (will be loaded from .secrets.json)
DATABASE_URL = "postgresql://postgres:password@localhost/hosting_production"


class TodoParser:
    """Parser for TODO.md markdown format."""
    
    SECTION_PATTERN = r'^##\s+(.+)$'
    TASK_PATTERN = r'^\s*-\s+\[([ x])\]\s+(.+)$'
    
    def __init__(self, todo_file: Path):
        self.todo_file = todo_file
        self.tasks = []
    
    def parse(self) -> List[Dict]:
        """Parse TODO.md file and extract all tasks."""
        if not self.todo_file.exists():
            raise FileNotFoundError(f"TODO.md file not found: {self.todo_file}")
        
        content = self.todo_file.read_text()
        lines = content.split('\n')
        
        current_section = "Backlog"
        position = 0
        
        for line in lines:
            # Check for section header
            section_match = re.match(self.SECTION_PATTERN, line)
            if section_match:
                section_name = section_match.group(1).strip()
                # Normalize section names
                if "Backlog" in section_name or "Not Yet" in section_name:
                    current_section = "Backlog"
                elif "To Do" in section_name:
                    current_section = "To Do"
                elif "In Progress" in section_name:
                    current_section = "In Progress"
                elif "Completed" in section_name:
                    current_section = "Completed"
                position = 0  # Reset position for new section
                continue
            
            # Check for task line
            task_match = re.match(self.TASK_PATTERN, line)
            if task_match:
                is_completed = task_match.group(1) == 'x'
                content = task_match.group(2).strip()
                
                # Parse task content and metadata
                task_data = self._parse_task_content(content, current_section, is_completed, position)
                self.tasks.append(task_data)
                position += 1
        
        return self.tasks
    
    def _parse_task_content(self, content: str, section: str, is_completed: bool, position: int) -> Dict:
        """Parse individual task content to extract metadata."""
        # Extract metadata JSON if present
        metadata = {}
        json_match = re.search(r'\{[^}]+\}', content)
        if json_match:
            try:
                metadata = json.loads(json_match.group(0))
                # Remove JSON from content
                content = content[:json_match.start()].strip()
            except json.JSONDecodeError:
                pass
        
        # Extract priority
        priority = "medium"  # default
        priority_match = re.search(r'\((high|medium|low)\)', content)
        if priority_match:
            priority = priority_match.group(1)
            content = re.sub(r'\s*\((high|medium|low)\)', '', content)
        
        # Extract ID
        id_match = re.search(r'\(id:(\d+)\)', content)
        task_id = None
        if id_match:
            task_id = int(id_match.group(1))
            content = re.sub(r'\s*\(id:\d+\)', '', content)
        
        # Extract epic from content
        epic = metadata.get('epic', None)
        if not epic and ':' in content:
            parts = content.split(':', 1)
            if len(parts[0]) < 50:  # Likely an epic prefix
                epic = parts[0].strip()
        
        # Build task data
        return {
            'original_id': task_id,
            'content': content.strip(),
            'status': 'completed' if is_completed else 'pending',
            'priority': priority,
            'section': section,
            'epic': epic,
            'area': 'general',
            'occurrence_count': metadata.get('occurrence_count', 1),
            'created_at': metadata.get('created_at', None),
            'completed_at': metadata.get('completed_at', None) if is_completed else None,
            'position': position
        }


class DatabaseMigrator:
    """Migrator to import tasks into PostgreSQL."""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def migrate_tasks(self, tasks: List[Dict]) -> int:
        """
        Import tasks into the database.
        Returns the number of tasks migrated.
        """
        from models.kanban import KanbanTask
        
        migrated_count = 0
        
        for task_data in tasks:
            # Check if task already exists (by content and section)
            existing = self.session.query(KanbanTask).filter_by(
                content=task_data['content'],
                section=task_data['section']
            ).first()
            
            if existing:
                print(f"  SKIP: Task already exists - {task_data['content'][:50]}...")
                continue
            
            # Create new task
            new_task = KanbanTask(
                content=task_data['content'],
                status=task_data['status'],
                priority=task_data['priority'],
                owner='agent',  # Default owner
                section=task_data['section'],
                epic=task_data['epic'],
                area=task_data['area'],
                occurrence_count=task_data['occurrence_count'],
                position=task_data['position']
            )
            
            # Parse and set timestamps
            if task_data.get('created_at'):
                try:
                    new_task.created_at = datetime.fromisoformat(task_data['created_at'])
                except:
                    pass
            
            if task_data.get('completed_at'):
                try:
                    new_task.completed_at = datetime.fromisoformat(task_data['completed_at'])
                except:
                    pass
            
            self.session.add(new_task)
            migrated_count += 1
            print(f"  ADDED: {task_data['content'][:70]}...")
        
        # Commit all changes
        self.session.commit()
        return migrated_count
    
    def close(self):
        """Close database session."""
        self.session.close()


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description='Migrate TODO.md to PostgreSQL')
    parser.add_argument('todo_file', help='Path to TODO.md file')
    parser.add_argument('--database-url', default=DATABASE_URL, help='PostgreSQL database URL')
    parser.add_argument('--dry-run', action='store_true', help='Parse but do not import')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("TODO.md to PostgreSQL Migration Tool")
    print("=" * 80)
    
    # Parse TODO.md file
    print(f"\n1. Parsing TODO.md file: {args.todo_file}")
    todo_parser = TodoParser(Path(args.todo_file))
    tasks = todo_parser.parse()
    print(f"   Found {len(tasks)} tasks")
    
    # Show task distribution
    sections = {}
    for task in tasks:
        section = task['section']
        sections[section] = sections.get(section, 0) + 1
    
    print("\n   Task distribution by section:")
    for section, count in sorted(sections.items()):
        print(f"     {section}: {count} tasks")
    
    if args.dry_run:
        print("\n   DRY RUN: No changes made to database")
        return
    
    # Migrate to database
    print(f"\n2. Migrating tasks to PostgreSQL")
    print(f"   Database: {args.database_url}")
    
    migrator = DatabaseMigrator(args.database_url)
    try:
        migrated_count = migrator.migrate_tasks(tasks)
        print(f"\n3. Migration complete!")
        print(f"   Tasks migrated: {migrated_count}")
        print(f"   Tasks skipped: {len(tasks) - migrated_count}")
    except Exception as e:
        print(f"\nERROR: Migration failed: {e}")
        raise
    finally:
        migrator.close()
    
    print("\n" + "=" * 80)
    print("Migration finished successfully!")
    print("=" * 80)
    
    # Create backup of original file
    backup_path = Path(args.todo_file).with_suffix('.md.backup')
    print(f"\nBacking up original TODO.md to: {backup_path}")
    Path(args.todo_file).rename(backup_path)
    print("Original TODO.md has been backed up.")
    

if __name__ == "__main__":
    main()
