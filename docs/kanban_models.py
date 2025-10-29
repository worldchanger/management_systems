"""
SQLAlchemy models for PostgreSQL-backed Kanban system.
Replaces the TODO.md file-based approach with proper database storage.

This file should be placed in: hosting-management-system/models/kanban.py
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    CheckConstraint, Index, func
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class KanbanTask(Base):
    """
    Main kanban task model.
    Represents individual tasks in the kanban board.
    """
    __tablename__ = 'kanban_tasks'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    content = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    priority = Column(String(10), default='medium')
    owner = Column(String(20), default='agent')
    section = Column(String(50), nullable=False, default='Backlog')
    
    # Classification
    epic = Column(String(100), nullable=True)
    area = Column(String(50), default='general')
    occurrence_count = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Position for drag-and-drop ordering
    position = Column(Integer, default=0)
    
    # Relationships
    history = relationship("KanbanTaskHistory", back_populates="task", cascade="all, delete-orphan")
    tags = relationship("KanbanTag", secondary="kanban_task_tags", back_populates="tasks")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'completed')", name='valid_status'),
        CheckConstraint("priority IN ('high', 'medium', 'low')", name='valid_priority'),
        CheckConstraint("section IN ('Backlog', 'To Do', 'In Progress', 'Completed')", name='valid_section'),
        CheckConstraint("owner IN ('user', 'agent')", name='valid_owner'),
        Index('idx_kanban_section', 'section'),
        Index('idx_kanban_status', 'status'),
        Index('idx_kanban_priority', 'priority'),
        Index('idx_kanban_created_at', 'created_at'),
        Index('idx_kanban_epic', 'epic'),
        Index('idx_kanban_position', 'section', 'position'),
    )
    
    @hybrid_property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == 'completed'
    
    @hybrid_property
    def is_high_priority(self) -> bool:
        """Check if task is high priority."""
        return self.priority == 'high'
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for API responses."""
        return {
            'id': self.id,
            'content': self.content,
            'status': self.status,
            'priority': self.priority,
            'owner': self.owner,
            'section': self.section,
            'epic': self.epic,
            'area': self.area,
            'occurrence_count': self.occurrence_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'position': self.position,
            'tags': [tag.name for tag in self.tags]
        }
    
    def __repr__(self):
        return f"<KanbanTask(id={self.id}, content='{self.content[:50]}...', section='{self.section}')>"


class KanbanTaskHistory(Base):
    """
    Audit log for task changes.
    Tracks all modifications to tasks for accountability.
    """
    __tablename__ = 'kanban_task_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('kanban_tasks.id', ondelete='CASCADE'), nullable=False)
    action = Column(String(50), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String(50), default='agent')
    changed_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationship
    task = relationship("KanbanTask", back_populates="history")
    
    # Indexes
    __table_args__ = (
        Index('idx_history_task_id', 'task_id'),
        Index('idx_history_changed_at', 'changed_at'),
    )
    
    def to_dict(self) -> dict:
        """Convert history entry to dictionary."""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'action': self.action,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }
    
    def __repr__(self):
        return f"<KanbanTaskHistory(id={self.id}, task_id={self.task_id}, action='{self.action}')>"


class KanbanTag(Base):
    """
    Tags for flexible task categorization.
    Allows multiple tags per task via many-to-many relationship.
    """
    __tablename__ = 'kanban_tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default='#6c757d')  # Hex color code
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationship
    tasks = relationship("KanbanTask", secondary="kanban_task_tags", back_populates="tags")
    
    def to_dict(self) -> dict:
        """Convert tag to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'task_count': len(self.tasks)
        }
    
    def __repr__(self):
        return f"<KanbanTag(id={self.id}, name='{self.name}')>"


class KanbanTaskTag(Base):
    """
    Many-to-many association table for tasks and tags.
    """
    __tablename__ = 'kanban_task_tags'
    
    task_id = Column(Integer, ForeignKey('kanban_tasks.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('kanban_tags.id', ondelete='CASCADE'), primary_key=True)


# ============================================================================
# Database Utility Functions
# ============================================================================

def create_all_tables(engine):
    """
    Create all tables in the database.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    """
    Drop all tables from the database.
    WARNING: This will delete all data!
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(engine)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """
    Example of how to use these models.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create engine (update with your connection string)
    engine = create_engine('postgresql://postgres:password@localhost/hosting_production')
    
    # Create tables
    create_all_tables(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create a new task
    task = KanbanTask(
        content="Test task from SQLAlchemy",
        priority="high",
        section="To Do",
        epic="Testing"
    )
    session.add(task)
    session.commit()
    
    # Query tasks
    tasks = session.query(KanbanTask).filter_by(section="To Do").all()
    for task in tasks:
        print(task.to_dict())
    
    # Close session
    session.close()
