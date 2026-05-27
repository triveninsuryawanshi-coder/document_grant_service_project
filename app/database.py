"""Database connection and session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Base


class Database:
    """Database connection manager."""

    def __init__(self, database_url: str):
        """Initialize database connection."""
        self.engine = create_async_engine(
            database_url,
            echo=settings.database_echo,
            future=True,
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        """Get async session."""
        async with self.async_session() as session:
            yield session

    async def create_all(self):
        """Create all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        """Drop all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self):
        """Close database connection."""
        await self.engine.dispose()


db = Database(settings.database_url)
