"""Database seed data."""
import asyncio
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db
from app.models import User, Document, Grant
from datetime import datetime, timedelta, timezone


# Deterministic UUIDs for seeding
USERS = {
    "alice": UUID("550e8400-e29b-41d4-a716-446655440001"),
    "bob": UUID("550e8400-e29b-41d4-a716-446655440002"),
    "carol": UUID("550e8400-e29b-41d4-a716-446655440003"),
}

DOCUMENTS = {
    "q1_report": UUID("550e8400-e29b-41d4-a716-446655440011"),
    "product_roadmap": UUID("550e8400-e29b-41d4-a716-446655440012"),
    "budget_2026": UUID("550e8400-e29b-41d4-a716-446655440013"),
}


async def seed_database():
    """Seed database with deterministic data."""
    async with db.async_session() as session:
        # Create users
        alice = User(id=USERS["alice"], username="alice")
        bob = User(id=USERS["bob"], username="bob")
        carol = User(id=USERS["carol"], username="carol")
        
        session.add_all([alice, bob, carol])
        await session.flush()
        
        # Create documents
        q1_report = Document(
            id=DOCUMENTS["q1_report"],
            title="Q1 Report",
            owner_id=USERS["alice"],
        )
        product_roadmap = Document(
            id=DOCUMENTS["product_roadmap"],
            title="Product Roadmap",
            owner_id=USERS["alice"],
        )
        budget_2026 = Document(
            id=DOCUMENTS["budget_2026"],
            title="Budget 2026",
            owner_id=USERS["bob"],
        )
        
        session.add_all([q1_report, product_roadmap, budget_2026])
        await session.flush()
        
        # Create grants
        now = datetime.now(timezone.utc)
        
        # Alice grants view access to Bob for Q1 Report (expires in 7 days)
        grant1 = Grant(
            id=UUID("550e8400-e29b-41d4-a716-446655440021"),
            document_id=DOCUMENTS["q1_report"],
            creator_id=USERS["alice"],
            grantee_id=USERS["bob"],
            permission="view",
            expires_at=now + timedelta(days=7),
        )
        
        # Alice grants edit access to Carol for Product Roadmap (expires in 30 days)
        grant2 = Grant(
            id=UUID("550e8400-e29b-41d4-a716-446655440022"),
            document_id=DOCUMENTS["product_roadmap"],
            creator_id=USERS["alice"],
            grantee_id=USERS["carol"],
            permission="edit",
            expires_at=now + timedelta(days=30),
        )
        
        # Bob grants admin access to Alice for Budget 2026 (expires in 14 days)
        grant3 = Grant(
            id=UUID("550e8400-e29b-41d4-a716-446655440023"),
            document_id=DOCUMENTS["budget_2026"],
            creator_id=USERS["bob"],
            grantee_id=USERS["alice"],
            permission="admin",
            expires_at=now + timedelta(days=14),
        )
        
        session.add_all([grant1, grant2, grant3])
        await session.commit()
        
        print("✓ Database seeded successfully!")
        print(f"  - 3 users created: alice, bob, carol")
        print(f"  - 3 documents created: Q1 Report, Product Roadmap, Budget 2026")
        print(f"  - 3 grants created with various permissions")


async def main():
    """Main entry point."""
    try:
        # Create all tables first (via Alembic in production)
        await db.create_all()
        print("✓ Database tables created")
        
        # Seed data
        await seed_database()
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
