"""Initial database schema.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-05-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('owner_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    )
    
    # Create grants table
    op.create_table(
        'grants',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('creator_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('grantee_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('permission', sa.String(50), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['grantee_id'], ['users.id'], ),
    )
    
    # Create indexes
    op.create_index(op.f('ix_grants_document_id'), 'grants', ['document_id'], unique=False)
    op.create_index(op.f('ix_grants_grantee_id'), 'grants', ['grantee_id'], unique=False)
    op.create_index(op.f('ix_grants_creator_id'), 'grants', ['creator_id'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop indexes
    op.drop_index(op.f('ix_grants_creator_id'), table_name='grants')
    op.drop_index(op.f('ix_grants_grantee_id'), table_name='grants')
    op.drop_index(op.f('ix_grants_document_id'), table_name='grants')
    
    # Drop tables
    op.drop_table('grants')
    op.drop_table('documents')
    op.drop_table('users')
