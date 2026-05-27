"""Unit tests for grant service."""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.services import GrantService
from app.models import Grant


def test_is_grant_active_with_valid_grant():
    """Test that a valid grant is considered active."""
    now = datetime.now(timezone.utc)
    grant = Grant(
        id=UUID("550e8400-e29b-41d4-a716-446655440001"),
        document_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
        creator_id=UUID("550e8400-e29b-41d4-a716-446655440003"),
        grantee_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
        permission="view",
        expires_at=now + timedelta(days=1),
        revoked_at=None,
    )
    assert GrantService.is_grant_active(grant) is True


def test_is_grant_active_with_expired_grant():
    """Test that an expired grant is not active."""
    now = datetime.now(timezone.utc)
    grant = Grant(
        id=UUID("550e8400-e29b-41d4-a716-446655440001"),
        document_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
        creator_id=UUID("550e8400-e29b-41d4-a716-446655440003"),
        grantee_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
        permission="view",
        expires_at=now - timedelta(days=1),
        revoked_at=None,
    )
    assert GrantService.is_grant_active(grant) is False


def test_is_grant_active_with_revoked_grant():
    """Test that a revoked grant is not active."""
    now = datetime.now(timezone.utc)
    grant = Grant(
        id=UUID("550e8400-e29b-41d4-a716-446655440001"),
        document_id=UUID("550e8400-e29b-41d4-a716-446655440002"),
        creator_id=UUID("550e8400-e29b-41d4-a716-446655440003"),
        grantee_id=UUID("550e8400-e29b-41d4-a716-446655440004"),
        permission="view",
        expires_at=now + timedelta(days=1),
        revoked_at=now - timedelta(hours=1),
    )
    assert GrantService.is_grant_active(grant) is False


def test_validate_expiry_with_valid_expiry():
    """Test that a valid expiry passes validation."""
    now = datetime.now(timezone.utc)
    future_expiry = now + timedelta(minutes=2)
    # Should not raise
    GrantService.validate_expiry(future_expiry)


def test_validate_expiry_with_invalid_expiry():
    """Test that an expiry less than 1 minute in the future fails."""
    now = datetime.now(timezone.utc)
    invalid_expiry = now + timedelta(seconds=30)
    with pytest.raises(ValueError, match="Expiry must be at least 1 minute in the future"):
        GrantService.validate_expiry(invalid_expiry)


def test_validate_expiry_with_past_time():
    """Test that a past expiry fails."""
    now = datetime.now(timezone.utc)
    past_expiry = now - timedelta(days=1)
    with pytest.raises(ValueError, match="Expiry must be at least 1 minute in the future"):
        GrantService.validate_expiry(past_expiry)


def test_validate_expiry_with_exactly_now():
    """Test that expiry at exactly now fails."""
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="Expiry must be at least 1 minute in the future"):
        GrantService.validate_expiry(now)
