"""
Comprehensive unit tests for PostgreSQL-backed Kanban API.
Tests both API endpoints and database operations.

This file should be placed in: hosting-management-system/tests/test_kanban_postgres.py

Run with: pytest tests/test_kanban_postgres.py -v
"""

import pytest
import requests
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional

# Test configuration
API_BASE_URL = "https://hosting.remoteds.us/api/v1/kanban"
LOCAL_API_URL = "http://localhost:8000/api/v1/kanban"  # For local testing
DATABASE_URL = "postgresql://postgres:password@localhost/hosting_production"


class TestKanbanAPIConnection:
    """Test suite for API connectivity and authentication."""
    
    @pytest.fixture
    def api_url(self):
        """Return the appropriate API URL."""
        # Try local first, fall back to production
        return LOCAL_API_URL
    
    @pytest.fixture
    def auth_token(self):
        """
        Get authentication token for API access.
        This should authenticate via the hosting system login.
        """
        # TODO: Implement actual authentication
        # This is a placeholder - replace with actual login flow
        login_url = "http://localhost:8000/login"
        response = requests.post(
            login_url,
            data={
                "username": "admin",
                "password": "your_password",  # From .secrets.json
                "next": "/"
            }
        )
        
        if response.status_code == 200:
            # Extract JWT token from response
            # This depends on your auth implementation
            return "Bearer your-jwt-token-here"
        else:
            pytest.skip("Unable to authenticate - check credentials")
    
    def test_health_check(self, api_url):
        """Test the health check endpoint (no auth required)."""
        response = requests.get(f"{api_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
    
    def test_authentication_required(self, api_url):
        """Test that endpoints require authentication."""
        response = requests.get(f"{api_url}/tasks")
        
        # Should return 401 or 403 without authentication
        assert response.status_code in [401, 403]


class TestKanbanTaskOperations:
    """Test suite for CRUD operations on kanban tasks."""
    
    @pytest.fixture
    def api_url(self):
        """Return the appropriate API URL."""
        return LOCAL_API_URL
    
    @pytest.fixture
    def auth_headers(self):
        """Return authentication headers for requests."""
        # TODO: Replace with actual token from login
        return {"Authorization": "Bearer your-jwt-token-here"}
    
    @pytest.fixture
    def sample_task_data(self):
        """Return sample task data for testing."""
        return {
            "content": "Test task created by pytest",
            "priority": "high",
            "section": "To Do",
            "epic": "Testing",
            "area": "qa"
        }
    
    def test_create_task(self, api_url, auth_headers, sample_task_data):
        """Test creating a new task."""
        response = requests.post(
            f"{api_url}/tasks",
            json=sample_task_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["content"] == sample_task_data["content"]
        assert data["priority"] == sample_task_data["priority"]
        assert data["section"] == sample_task_data["section"]
        assert data["epic"] == sample_task_data["epic"]
        assert "id" in data
        assert "created_at" in data
        
        # Store task ID for cleanup
        return data["id"]
    
    def test_list_tasks(self, api_url, auth_headers):
        """Test listing all tasks."""
        response = requests.get(f"{api_url}/tasks", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            task = data[0]
            assert "id" in task
            assert "content" in task
            assert "section" in task
            assert "priority" in task
    
    def test_get_task_by_id(self, api_url, auth_headers, sample_task_data):
        """Test retrieving a specific task by ID."""
        # First create a task
        create_response = requests.post(
            f"{api_url}/tasks",
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Then retrieve it
        response = requests.get(f"{api_url}/tasks/{task_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["content"] == sample_task_data["content"]
        
        # Cleanup
        requests.delete(f"{api_url}/tasks/{task_id}", headers=auth_headers)
    
    def test_update_task(self, api_url, auth_headers, sample_task_data):
        """Test updating a task."""
        # Create task
        create_response = requests.post(
            f"{api_url}/tasks",
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Update task
        update_data = {"priority": "low", "content": "Updated content"}
        response = requests.put(
            f"{api_url}/tasks/{task_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "low"
        assert data["content"] == "Updated content"
        
        # Cleanup
        requests.delete(f"{api_url}/tasks/{task_id}", headers=auth_headers)
    
    def test_move_task(self, api_url, auth_headers, sample_task_data):
        """Test moving a task to a different section."""
        # Create task
        create_response = requests.post(
            f"{api_url}/tasks",
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Move task
        move_data = {"section": "In Progress", "position": 0}
        response = requests.post(
            f"{api_url}/tasks/{task_id}/move",
            json=move_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["section"] == "In Progress"
        
        # Cleanup
        requests.delete(f"{api_url}/tasks/{task_id}", headers=auth_headers)
    
    def test_complete_task(self, api_url, auth_headers, sample_task_data):
        """Test marking a task as completed."""
        # Create task
        create_response = requests.post(
            f"{api_url}/tasks",
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Complete task
        response = requests.post(
            f"{api_url}/tasks/{task_id}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["section"] == "Completed"
        assert data["completed_at"] is not None
        
        # Cleanup
        requests.delete(f"{api_url}/tasks/{task_id}", headers=auth_headers)
    
    def test_delete_task(self, api_url, auth_headers, sample_task_data):
        """Test deleting a task."""
        # Create task
        create_response = requests.post(
            f"{api_url}/tasks",
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Delete task
        response = requests.delete(
            f"{api_url}/tasks/{task_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        get_response = requests.get(
            f"{api_url}/tasks/{task_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


class TestKanbanFiltering:
    """Test suite for task filtering and querying."""
    
    @pytest.fixture
    def api_url(self):
        return LOCAL_API_URL
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer your-jwt-token-here"}
    
    def test_filter_by_section(self, api_url, auth_headers):
        """Test filtering tasks by section."""
        response = requests.get(
            f"{api_url}/tasks",
            params={"section": "To Do"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for task in data:
            assert task["section"] == "To Do"
    
    def test_filter_by_priority(self, api_url, auth_headers):
        """Test filtering tasks by priority."""
        response = requests.get(
            f"{api_url}/tasks",
            params={"priority": "high"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for task in data:
            assert task["priority"] == "high"
    
    def test_filter_by_epic(self, api_url, auth_headers):
        """Test filtering tasks by epic."""
        response = requests.get(
            f"{api_url}/tasks",
            params={"epic": "Testing"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for task in data:
            assert task["epic"] == "Testing"
    
    def test_pagination(self, api_url, auth_headers):
        """Test pagination with limit and offset."""
        response = requests.get(
            f"{api_url}/tasks",
            params={"limit": 5, "offset": 0},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5


class TestKanbanStatistics:
    """Test suite for kanban statistics and reporting."""
    
    @pytest.fixture
    def api_url(self):
        return LOCAL_API_URL
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer your-jwt-token-here"}
    
    def test_get_stats(self, api_url, auth_headers):
        """Test retrieving kanban board statistics."""
        response = requests.get(f"{api_url}/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 4  # Four sections
        
        for section_stat in data:
            assert "section" in section_stat
            assert "count" in section_stat
            assert "high_priority" in section_stat
            assert "medium_priority" in section_stat
            assert "low_priority" in section_stat
    
    def test_list_sections(self, api_url, auth_headers):
        """Test listing available sections."""
        response = requests.get(f"{api_url}/sections", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data == ["Backlog", "To Do", "In Progress", "Completed"]


class TestDatabaseOperations:
    """Test suite for direct database operations."""
    
    @pytest.fixture
    def db_session(self):
        """Create a database session for testing."""
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_database_connection(self, db_session):
        """Test database connectivity."""
        result = db_session.execute("SELECT 1").scalar()
        assert result == 1
    
    def test_create_task_in_database(self, db_session):
        """Test creating a task directly in the database."""
        from models.kanban import KanbanTask
        
        task = KanbanTask(
            content="Direct database test task",
            priority="medium",
            section="Backlog",
            epic="Testing"
        )
        
        db_session.add(task)
        db_session.commit()
        
        # Verify task was created
        retrieved_task = db_session.query(KanbanTask).filter_by(
            content="Direct database test task"
        ).first()
        
        assert retrieved_task is not None
        assert retrieved_task.content == "Direct database test task"
        assert retrieved_task.priority == "medium"
        
        # Cleanup
        db_session.delete(retrieved_task)
        db_session.commit()
    
    def test_task_constraints(self, db_session):
        """Test database constraints on tasks."""
        from models.kanban import KanbanTask
        from sqlalchemy.exc import IntegrityError
        
        # Test invalid priority
        with pytest.raises(IntegrityError):
            task = KanbanTask(
                content="Invalid task",
                priority="invalid",  # Should fail constraint
                section="Backlog"
            )
            db_session.add(task)
            db_session.commit()
        
        db_session.rollback()


class TestWebInterfaceIntegration:
    """Test suite for web interface integration."""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8000"
    
    def test_kanban_page_loads(self, base_url):
        """Test that the kanban web page loads successfully."""
        response = requests.get(f"{base_url}/kanban")
        
        # May return 302 redirect to login if not authenticated
        assert response.status_code in [200, 302]
    
    def test_kanban_page_authenticated(self, base_url):
        """Test kanban page access with authentication."""
        # TODO: Implement session-based authentication test
        pass


# ============================================================================
# Integration Test Suite
# ============================================================================

class TestFullWorkflow:
    """End-to-end integration tests for complete workflows."""
    
    @pytest.fixture
    def api_url(self):
        return LOCAL_API_URL
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer your-jwt-token-here"}
    
    def test_task_lifecycle(self, api_url, auth_headers):
        """Test complete task lifecycle from creation to completion."""
        # 1. Create task
        task_data = {
            "content": "Integration test task",
            "priority": "high",
            "section": "Backlog",
            "epic": "Integration Testing"
        }
        
        create_response = requests.post(
            f"{api_url}/tasks",
            json=task_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # 2. Move to To Do
        requests.post(
            f"{api_url}/tasks/{task_id}/move",
            json={"section": "To Do"},
            headers=auth_headers
        )
        
        # 3. Move to In Progress
        requests.post(
            f"{api_url}/tasks/{task_id}/move",
            json={"section": "In Progress"},
            headers=auth_headers
        )
        
        # 4. Update priority
        requests.post(
            f"{api_url}/tasks/{task_id}/priority",
            json={"priority": "medium"},
            headers=auth_headers
        )
        
        # 5. Complete task
        complete_response = requests.post(
            f"{api_url}/tasks/{task_id}/complete",
            headers=auth_headers
        )
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["status"] == "completed"
        assert completed_task["section"] == "Completed"
        
        # 6. Cleanup
        requests.delete(f"{api_url}/tasks/{task_id}", headers=auth_headers)


# ============================================================================
# Test Runner Configuration
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
