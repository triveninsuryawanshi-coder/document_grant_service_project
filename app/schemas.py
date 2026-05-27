"""Pydantic schemas for request/response validation."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GrantCreate(BaseModel):
    """Schema for creating a grant."""

    document_id: UUID
    grantee_id: UUID
    permission: str = Field(..., pattern="^(view|edit|admin)$")
    expires_at: datetime


class GrantResponse(BaseModel):
    """Schema for grant response."""

    id: UUID
    document_id: UUID
    creator_id: UUID
    grantee_id: UUID
    permission: str
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
    is_active: bool = False

    model_config = {"from_attributes": True}


class GrantListResponse(BaseModel):
    """Schema for listing grants."""

    grants: list[GrantResponse]
    total: int


class GrantCheckResponse(BaseModel):
    """Schema for grant status check."""

    is_active: bool
    expires_at: datetime
    revoked_at: datetime | None = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
    error_code: str | None = None
