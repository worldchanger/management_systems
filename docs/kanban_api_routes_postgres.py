"""
PostgreSQL-backed Kanban REST API routes.
Replaces the TODO.md file-based kanban system with database operations.

This file should replace: hosting-management-system/routes/kanban_api_routes.py
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from jose import JWTError, jwt

# Import the models (adjust import path as needed)
# from models.kanban import KanbanTask, KanbanTaskHistory, KanbanTag
# from auth_utils import JWT_SECRET, JWT_ALGORITHM

router = APIRouter(prefix="/api/v1/kanban", tags=["kanban"])
security = HTTPBearer()

# Database connection (will be configured from .secrets.json)
DATABASE_URL = "postgresql://postgres:password@localhost/hosting_production"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# Pydantic Models for Request/Response
# ============================================================================

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    content: str = Field(..., min_length=1, max_length=1000)
    priority: Optional[str] = Field(default="medium", regex="^(high|medium|low)$")
    owner: Optional[str] = Field(default="agent", regex="^(user|agent)$")
    section: Optional[str] = Field(default="Backlog", regex="^(Backlog|To Do|In Progress|Completed)$")
    epic: Optional[str] = Field(default=None, max_length=100)
    area: Optional[str] = Field(default="general", max_length=50)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    priority: Optional[str] = Field(None, regex="^(high|medium|low)$")
    owner: Optional[str] = Field(None, regex="^(user|agent)$")
    status: Optional[str] = Field(None, regex="^(pending|completed)$")
    epic: Optional[str] = Field(None, max_length=100)
    area: Optional[str] = Field(None, max_length=50)


class TaskMove(BaseModel):
    """Schema for moving a task to a different section."""
    section: str = Field(..., regex="^(Backlog|To Do|In Progress|Completed)$")
    position: Optional[int] = Field(default=0, ge=0)


class TaskPriority(BaseModel):
    """Schema for updating task priority."""
    priority: str = Field(..., regex="^(high|medium|low)$")


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    content: str
    status: str
    priority: str
    owner: str
    section: str
    epic: Optional[str]
    area: str
    occurrence_count: int
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    position: int
    tags: List[str] = []

    class Config:
        from_attributes = True


class SectionStats(BaseModel):
    """Schema for section statistics."""
    section: str
    count: int
    high_priority: int
    medium_priority: int
    low_priority: int


# ============================================================================
# Database Dependency
# ============================================================================

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Authentication Dependency
# ============================================================================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify JWT token from Authorization header.
    Returns decoded token payload.
    """
    try:
        # This should use your actual JWT_SECRET and JWT_ALGORITHM
        # from auth_utils import JWT_SECRET, JWT_ALGORITHM
        JWT_SECRET = "your-secret-key"  # Replace with actual secret
        JWT_ALGORITHM = "HS256"
        
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    section: Optional[str] = Query(None, regex="^(Backlog|To Do|In Progress|Completed)$"),
    priority: Optional[str] = Query(None, regex="^(high|medium|low)$"),
    status: Optional[str] = Query(None, regex="^(pending|completed)$"),
    epic: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """
    List all tasks with optional filtering.
    
    Query Parameters:
    - section: Filter by section (Backlog, To Do, In Progress, Completed)
    - priority: Filter by priority (high, medium, low)
    - status: Filter by status (pending, completed)
    - epic: Filter by epic name
    - limit: Maximum number of results (default: 100)
    - offset: Number of results to skip (default: 0)
    """
    from models.kanban import KanbanTask
    
    query = db.query(KanbanTask)
    
    if section:
        query = query.filter(KanbanTask.section == section)
    if priority:
        query = query.filter(KanbanTask.priority == priority)
    if status:
        query = query.filter(KanbanTask.status == status)
    if epic:
        query = query.filter(KanbanTask.epic == epic)
    
    # Order by position within section, then by created_at
    query = query.order_by(KanbanTask.section, KanbanTask.position, KanbanTask.created_at.desc())
    
    tasks = query.offset(offset).limit(limit).all()
    
    return [TaskResponse(**task.to_dict()) for task in tasks]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Get a specific task by ID."""
    from models.kanban import KanbanTask
    
    task = db.query(KanbanTask).filter(KanbanTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return TaskResponse(**task.to_dict())


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Create a new task."""
    from models.kanban import KanbanTask
    
    # Get the highest position in the target section
    max_position = db.query(func.max(KanbanTask.position)).filter(
        KanbanTask.section == task_data.section
    ).scalar() or 0
    
    new_task = KanbanTask(
        content=task_data.content,
        priority=task_data.priority,
        owner=task_data.owner,
        section=task_data.section,
        epic=task_data.epic,
        area=task_data.area,
        position=max_position + 1
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return TaskResponse(**new_task.to_dict())


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Update an existing task."""
    from models.kanban import KanbanTask
    
    task = db.query(KanbanTask).filter(KanbanTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Update only provided fields
    update_data = task_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # If status changed to completed, set completed_at
    if task_data.status == "completed" and task.status != "completed":
        task.completed_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse(**task.to_dict())


@router.post("/tasks/{task_id}/move", response_model=TaskResponse)
async def move_task(
    task_id: int,
    move_data: TaskMove,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Move a task to a different section."""
    from models.kanban import KanbanTask
    
    task = db.query(KanbanTask).filter(KanbanTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    old_section = task.section
    task.section = move_data.section
    task.position = move_data.position
    
    # If moving to Completed, set status and completed_at
    if move_data.section == "Completed" and task.status != "completed":
        task.status = "completed"
        task.completed_at = datetime.now()
    
    # If moving from Completed, reset status
    if old_section == "Completed" and move_data.section != "Completed":
        task.status = "pending"
        task.completed_at = None
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse(**task.to_dict())


@router.post("/tasks/{task_id}/priority", response_model=TaskResponse)
async def update_priority(
    task_id: int,
    priority_data: TaskPriority,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Update task priority."""
    from models.kanban import KanbanTask
    
    task = db.query(KanbanTask).filter(KanbanTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task.priority = priority_data.priority
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse(**task.to_dict())


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Mark a task as completed."""
    from models.kanban import KanbanTask
    
    task = db.query(KanbanTask).filter(KanbanTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task.status = "completed"
    task.section = "Completed"
    task.completed_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse(**task.to_dict())


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Delete a task."""
    from models.kanban import KanbanTask
    
    task = db.query(KanbanTask).filter(KanbanTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    db.delete(task)
    db.commit()
    
    return None


@router.get("/sections", response_model=List[str])
async def list_sections(token: dict = Depends(verify_token)):
    """Get list of available sections."""
    return ["Backlog", "To Do", "In Progress", "Completed"]


@router.get("/stats", response_model=List[SectionStats])
async def get_stats(
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Get kanban board statistics."""
    from models.kanban import KanbanTask
    
    sections = ["Backlog", "To Do", "In Progress", "Completed"]
    stats = []
    
    for section in sections:
        total = db.query(KanbanTask).filter(KanbanTask.section == section).count()
        high = db.query(KanbanTask).filter(
            KanbanTask.section == section,
            KanbanTask.priority == "high"
        ).count()
        medium = db.query(KanbanTask).filter(
            KanbanTask.section == section,
            KanbanTask.priority == "medium"
        ).count()
        low = db.query(KanbanTask).filter(
            KanbanTask.section == section,
            KanbanTask.priority == "low"
        ).count()
        
        stats.append(SectionStats(
            section=section,
            count=total,
            high_priority=high,
            medium_priority=medium,
            low_priority=low
        ))
    
    return stats


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify database connectivity."""
    try:
        # Try a simple query to verify database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
