"""Integration tests for grant API endpoints."""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_grant_success(test_data):
    """Test successful grant creation."""
    data = test_data
    users = data["users"]
    documents = data["documents"]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(days=7)).isoformat()
        
        response = await client.post(
            "/grants",
            json={
                "document_id": str(documents[0].id),
                "grantee_id": str(users[1].id),
                "permission": "view",
                "expires_at": expires_at,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["permission"] == "view"
        assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_grant_invalid_expiry(test_data):
    """Test grant creation with invalid expiry."""
    data = test_data
    users = data["users"]
    documents = data["documents"]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(seconds=30)).isoformat()
        
        response = await client.post(
            "/grants",
            json={
                "document_id": str(documents[0].id),
                "grantee_id": str(users[1].id),
                "permission": "view",
                "expires_at": expires_at,
            },
        )
        
        assert response.status_code == 400
        assert "Expiry must be at least 1 minute in the future" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_grant_nonexistent_document(test_data):
    """Test grant creation for nonexistent document."""
    data = test_data
    users = data["users"]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(days=7)).isoformat()
        
        response = await client.post(
            "/grants",
            json={
                "document_id": str(uuid4()),
                "grantee_id": str(users[1].id),
                "permission": "view",
                "expires_at": expires_at,
            },
        )
        
        assert response.status_code == 404
        assert "Document not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_grants(test_data):
    """Test listing grants."""
    data = test_data
    users = data["users"]
    documents = data["documents"]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a grant first
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(days=7)).isoformat()
        
        await client.post(
            "/grants",
            json={
                "document_id": str(documents[0].id),
                "grantee_id": str(users[1].id),
                "permission": "view",
                "expires_at": expires_at,
            },
        )
        
        # List grants
        response = await client.get("/grants")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["grants"]) == 1


@pytest.mark.asyncio
async def test_get_grant(test_data):
    """Test retrieving a single grant."""
    data = test_data
    users = data["users"]
    documents = data["documents"]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a grant first
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(days=7)).isoformat()
        
        create_response = await client.post(
            "/grants",
            json={
                "document_id": str(documents[0].id),
                "grantee_id": str(users[1].id),
                "permission": "view",
                "expires_at": expires_at,
            },
        )
        
        grant_id = create_response.json()["id"]
        
        # Get the grant
        response = await client.get(f"/grants/{grant_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == grant_id
        assert data["permission"] == "view"


@pytest.mark.asyncio
async def test_get_grant_not_found(test_data):
    """Test retrieving a nonexistent grant."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/grants/{uuid4()}")
        
        assert response.status_code == 404
        assert "Grant not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_check_grant_active(test_data):
    """Test checking an active grant."""
    data = test_data
    users = data["users"]
    documents = data["documents"]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a grant
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(days=7)).isoformat()
        
        create_response = await client.post(
            "/grants",
            json={
                "document_id": str(documents[0].id),
                "grantee_id": str(users[1].id),
                "permission": "view",
                "expires_at": expires_at,
            },
        )
        
        grant_id = create_response.json()["id"]
        
        # Check the grant
        response = await client.get(f"/grants/{grant_id}/check")
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True


@pytest.mark.asyncio
async def test_health_check(test_data):
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
