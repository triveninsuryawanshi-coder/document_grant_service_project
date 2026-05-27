"""Pytest configuration."""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_session
from app.models import Base, User, Document, Grant


# Use in-memory SQLite for faster tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session():
    """Create test database and return async session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def override_get_session():
        async with async_session_factory() as session:
            yield session
    
    app.dependency_overrides[get_session] = override_get_session
    
    yield async_session_factory
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_data(async_session):
    """Create test data."""
    async with async_session() as session:
        # Create users
        user1 = User(id=uuid4(), username="user1")
        user2 = User(id=uuid4(), username="user2")
        user3 = User(id=uuid4(), username="user3")
        
        session.add_all([user1, user2, user3])
        await session.flush()
        
        # Create documents
        doc1 = Document(
            id=uuid4(),
            title="Document 1",
            owner_id=user1.id,
        )
        doc2 = Document(
            id=uuid4(),
            title="Document 2",
            owner_id=user2.id,
        )
        
        session.add_all([doc1, doc2])
        await session.commit()
        
        return {
            "users": [user1, user2, user3],
            "documents": [doc1, doc2],
        }
