"""FastAPI application and routes."""
from datetime import datetime, timezone
from uuid import UUID

import structlog
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db
from app.logging_config import configure_logging
from app.models import Grant
from app.schemas import GrantCreate, GrantResponse, GrantListResponse, GrantCheckResponse
from app.services import GrantService

# Configure logging
configure_logging()

logger = structlog.get_logger()

app = FastAPI(
    title="Document Grant Service",
    description="REST API for managing document access grants",
    version="1.0.0",
)


async def get_session() -> AsyncSession:
    """Dependency for getting database session."""
    async for session in db.get_session():
        yield session


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    logger.info("Starting up Document Grant Service")


@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown."""
    logger.info("Shutting down Document Grant Service")
    await db.close()


@app.post("/grants", response_model=GrantResponse, status_code=status.HTTP_201_CREATED)
async def create_grant(grant_data: GrantCreate, session: AsyncSession = Depends(get_session)):
    """Create a new grant.
    
    Business rules:
    - Expiry must be at least 1 minute in the future
    - Only one active grant per grantee/document pair
    """
    try:
        # Validate expiry
        GrantService.validate_expiry(grant_data.expires_at)
        
        # Check if document exists
        document_exists = await GrantService.verify_document_exists(
            session, grant_data.document_id
        )
        if not document_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        
        # Check for duplicate active grant
        has_duplicate = await GrantService.check_duplicate_active_grant(
            session, grant_data.document_id, grant_data.grantee_id
        )
        if has_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active grant already exists for this document and grantee",
            )
        
        # Create new grant
        grant = Grant(
            document_id=grant_data.document_id,
            creator_id=grant_data.grantee_id,  # For this service, creator == grantee
            grantee_id=grant_data.grantee_id,
            permission=grant_data.permission,
            expires_at=grant_data.expires_at,
        )
        
        session.add(grant)
        await session.commit()
        await session.refresh(grant)
        
        logger.info("grant_created", grant_id=str(grant.id))
        
        return GrantResponse(
            **grant.__dict__,
            is_active=GrantService.is_grant_active(grant),
        )
    
    except ValueError as e:
        logger.warning("grant_creation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.get("/grants", response_model=GrantListResponse)
async def list_grants(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    """List all grants with pagination."""
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pagination parameters",
        )
    
    grants, total = await GrantService.list_grants(session, skip, limit)
    
    grant_responses = [
        GrantResponse(**g.__dict__, is_active=GrantService.is_grant_active(g))
        for g in grants
    ]
    
    logger.info("grants_listed", count=len(grants), total=total)
    
    return GrantListResponse(grants=grant_responses, total=total)


@app.get("/grants/{grant_id}", response_model=GrantResponse)
async def get_grant(grant_id: UUID, session: AsyncSession = Depends(get_session)):
    """Retrieve a single grant by ID."""
    grant = await GrantService.get_grant(session, grant_id)
    
    if grant is None:
        logger.warning("grant_not_found", grant_id=str(grant_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grant not found",
        )
    
    return GrantResponse(
        **grant.__dict__,
        is_active=GrantService.is_grant_active(grant),
    )


@app.delete("/grants/{grant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_grant(
    grant_id: UUID,
    creator_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Revoke a grant.
    
    Business rules:
    - Only the creator can revoke a grant
    - Cannot revoke already-revoked or expired grants
    """
    try:
        grant = await GrantService.validate_creator(session, grant_id, creator_id)
        await GrantService.check_revocation_validity(grant)
        
        grant.revoked_at = datetime.now(timezone.utc)
        session.add(grant)
        await session.commit()
        
        logger.info("grant_revoked", grant_id=str(grant_id), by_user=str(creator_id))
        
        return None
    
    except ValueError as e:
        logger.warning("grant_revocation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.get("/grants/{grant_id}/check", response_model=GrantCheckResponse)
async def check_grant(grant_id: UUID, session: AsyncSession = Depends(get_session)):
    """Check the status of a grant."""
    grant = await GrantService.get_grant(session, grant_id)
    
    if grant is None:
        logger.warning("grant_not_found", grant_id=str(grant_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grant not found",
        )
    
    is_active = GrantService.is_grant_active(grant)
    
    logger.info("grant_checked", grant_id=str(grant_id), is_active=is_active)
    
    return GrantCheckResponse(
        is_active=is_active,
        expires_at=grant.expires_at,
        revoked_at=grant.revoked_at,
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
