"""Grant service for business logic."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Grant, Document


class GrantService:
    """Service for managing grants."""

    @staticmethod
    def is_grant_active(grant: Grant) -> bool:
        """Check if a grant is currently active."""
        if grant.revoked_at is not None:
            return False
        expires_at = grant.expires_at
        if expires_at.tzinfo is not None:
            expires_at = expires_at.astimezone(timezone.utc).replace(tzinfo=None)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return expires_at > now

    @staticmethod
    def validate_expiry(expires_at: datetime) -> None:
        """Validate that expiry is at least 1 minute in the future."""
        now = datetime.now(timezone.utc)
        min_expiry = now + timedelta(minutes=1)
        
        # Normalize both to UTC if they have timezone info
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at <= min_expiry:
            raise ValueError("Expiry must be at least 1 minute in the future")

    @staticmethod
    async def check_duplicate_active_grant(
        session: AsyncSession, document_id: UUID, grantee_id: UUID
    ) -> bool:
        """Check if there's already an active grant for this grantee/document pair."""
        query = select(Grant).where(
            and_(
                Grant.document_id == document_id,
                Grant.grantee_id == grantee_id,
                Grant.revoked_at.is_(None),
            )
        )
        result = await session.execute(query)
        existing_grant = result.scalars().first()
        
        if existing_grant is None:
            return False
        
        # Check if the existing grant is still active (not expired)
        return GrantService.is_grant_active(existing_grant)

    @staticmethod
    async def get_grant(session: AsyncSession, grant_id: UUID) -> Grant | None:
        """Get a grant by ID."""
        query = select(Grant).where(Grant.id == grant_id)
        result = await session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def validate_creator(
        session: AsyncSession, grant_id: UUID, creator_id: UUID
    ) -> Grant:
        """Validate that the user is the creator of the grant."""
        grant = await GrantService.get_grant(session, grant_id)
        if grant is None:
            raise ValueError("Grant not found")
        if grant.creator_id != creator_id:
            raise ValueError("Only the creator can revoke this grant")
        return grant

    @staticmethod
    async def check_revocation_validity(grant: Grant) -> None:
        """Check if a grant can be revoked."""
        if grant.revoked_at is not None:
            raise ValueError("Cannot revoke an already-revoked grant")
        if not GrantService.is_grant_active(grant):
            raise ValueError("Cannot revoke an expired grant")

    @staticmethod
    async def list_grants(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[list[Grant], int]:
        """List all grants with pagination."""
        # Get total count
        count_query = select(Grant)
        count_result = await session.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Get paginated results
        query = select(Grant).offset(skip).limit(limit)
        result = await session.execute(query)
        grants = result.scalars().all()
        
        return grants, total

    @staticmethod
    async def verify_document_exists(
        session: AsyncSession, document_id: UUID
    ) -> bool:
        """Verify that a document exists."""
        query = select(Document).where(Document.id == document_id)
        result = await session.execute(query)
        return result.scalars().first() is not None
