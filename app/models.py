"""Database models."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, UUID as SQLUUID, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Document(Base):
    """Document model."""

    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Grant(Base):
    """Grant model."""

    __tablename__ = "grants"

    id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), primary_key=True)
    document_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), nullable=False)
    creator_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), nullable=False)
    grantee_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), nullable=False)
    permission: Mapped[str] = mapped_column(String(50), nullable=False)  # view, edit, admin
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
