# API Examples

This document contains example API calls using curl. Make sure the server is running at `http://localhost:8000`.

## User IDs (from seed data)

```
Alice: 550e8400-e29b-41d4-a716-446655440001
Bob:   550e8400-e29b-41d4-a716-446655440002
Carol: 550e8400-e29b-41d4-a716-446655440003
```

## Document IDs (from seed data)

```
Q1 Report:         550e8400-e29b-41d4-a716-446655440011
Product Roadmap:   550e8400-e29b-41d4-a716-446655440012
Budget 2026:       550e8400-e29b-41d4-a716-446655440013
```

## Health Check

```bash
curl http://localhost:8000/health
```

## Create a Grant

Create a grant with view permission for 7 days:

```bash
curl -X POST http://localhost:8000/grants \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "550e8400-e29b-41d4-a716-446655440011",
    "grantee_id": "550e8400-e29b-41d4-a716-446655440002",
    "permission": "view",
    "expires_at": "2026-06-27T00:00:00Z"
  }'
```

## List All Grants

```bash
curl http://localhost:8000/grants
```

With pagination:

```bash
curl "http://localhost:8000/grants?skip=0&limit=10"
```

## Get a Specific Grant

```bash
curl http://localhost:8000/grants/{grant_id}
```

Example:

```bash
curl http://localhost:8000/grants/550e8400-e29b-41d4-a716-446655440021
```

## Check Grant Status

```bash
curl http://localhost:8000/grants/{grant_id}/check
```

Example:

```bash
curl http://localhost:8000/grants/550e8400-e29b-41d4-a716-446655440021/check
```

Response:

```json
{
  "is_active": true,
  "expires_at": "2026-06-27T00:00:00+00:00",
  "revoked_at": null
}
```

## Revoke a Grant

Only the creator can revoke. Pass the creator_id as a query parameter:

```bash
curl -X DELETE "http://localhost:8000/grants/550e8400-e29b-41d4-a716-446655440021?creator_id=550e8400-e29b-41d4-a716-446655440001"
```

## Error Responses

### Invalid Expiry (too soon)

```bash
curl -X POST http://localhost:8000/grants \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "550e8400-e29b-41d4-a716-446655440011",
    "grantee_id": "550e8400-e29b-41d4-a716-446655440002",
    "permission": "view",
    "expires_at": "2026-05-27T00:00:30Z"
  }'
```

Response (400):

```json
{
  "detail": "Expiry must be at least 1 minute in the future"
}
```

### Duplicate Active Grant

```bash
# First call succeeds
curl -X POST http://localhost:8000/grants \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "550e8400-e29b-41d4-a716-446655440011",
    "grantee_id": "550e8400-e29b-41d4-a716-446655440002",
    "permission": "view",
    "expires_at": "2026-06-27T00:00:00Z"
  }'

# Second call fails (duplicate)
curl -X POST http://localhost:8000/grants \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "550e8400-e29b-41d4-a716-446655440011",
    "grantee_id": "550e8400-e29b-41d4-a716-446655440002",
    "permission": "edit",
    "expires_at": "2026-06-27T00:00:00Z"
  }'
```

Response (409):

```json
{
  "detail": "An active grant already exists for this document and grantee"
}
```

### Unauthorized Revocation

```bash
curl -X DELETE "http://localhost:8000/grants/{grant_id}?creator_id=550e8400-e29b-41d4-a716-446655440002"
```

Response (400):

```json
{
  "detail": "Only the creator can revoke this grant"
}
```

### Not Found

```bash
curl http://localhost:8000/grants/00000000-0000-0000-0000-000000000000
```

Response (404):

```json
{
  "detail": "Grant not found"
}
```
