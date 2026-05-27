# Solution Design Decisions

## Key Design Decisions

1. **Creator = Grantee for Simplicity**: The implementation treats the grant creator as the grantee. This can be extended to support different users in production.

2. **Async-First Architecture**: Full async/await support with asyncpg for optimal concurrency handling in high-throughput scenarios.

3. **Soft Deletes for Grants**: Revoked and expired grants are never deleted—`revoked_at` timestamp tracks revocation state while maintaining audit trail.

4. **UTC Timestamps**: All expiration and revocation times use UTC with timezone awareness to avoid cross-timezone bugs.

5. **Deterministic Test UUIDs**: Seeding uses fixed UUIDs for reproducible test data and easy reference in documentation.

## Tradeoffs

- **No Authentication/Authorization Layer**: Revocation requires passing `creator_id` as query param (stateless design). Production should use JWT/OAuth.
- **Simple Pagination**: No cursor-based pagination—offset/limit used for simplicity; scale with keyset pagination if needed.
- **In-Memory Grant Active Check**: Status checked in code rather than database view for flexibility but requires timezone handling.

## Known Gaps

- No concurrency conflict handling for simultaneous duplicate grant creation (race condition).
- Integration tests use a separate test database; production CI/CD should use shared test fixtures.
- Missing graceful shutdown handling for in-flight requests.
