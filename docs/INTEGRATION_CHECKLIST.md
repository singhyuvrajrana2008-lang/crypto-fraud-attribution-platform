# Integration Checklist

## Purpose

This checklist must pass before frontend, backend, and database work is considered integrated.

## Repository

- [ ] `frontend/` exists
- [ ] `backend/` exists
- [ ] `database/` exists
- [ ] `docs/` exists
- [ ] `.env.example` exists
- [ ] `.gitignore` exists
- [ ] README explains the project and run commands

## Backend

- [ ] `backend/requirements.txt` is complete
- [ ] Backend starts from a fresh virtual environment
- [ ] `GET /api/health` works
- [ ] Environment variables load correctly
- [ ] Database connection works
- [ ] Blockchain provider configuration works
- [ ] No secrets are hardcoded

## Frontend

- [ ] `npm install` succeeds from a fresh clone
- [ ] `npm run dev` succeeds
- [ ] API base URL comes from environment configuration
- [ ] No direct database access
- [ ] No provider-specific blockchain logic
- [ ] Loading state works
- [ ] Error state works
- [ ] Empty state works
- [ ] No blocking browser console errors

## API Contract

- [ ] Endpoint paths match `API_CONTRACT.md`
- [ ] HTTP methods match
- [ ] Request field names match
- [ ] Response field names match
- [ ] Datatypes match
- [ ] Enum values match
- [ ] Error envelope matches
- [ ] UUIDs are strings in JSON
- [ ] Timestamps are ISO 8601 UTC
- [ ] Cryptocurrency amounts preserve precision

## Database

- [ ] `database/schema.sql` executes on a clean database
- [ ] `database/seed.sql` works for demo data when used
- [ ] Foreign keys match referenced UUID types
- [ ] Wallet addresses are TEXT
- [ ] Transaction hashes are TEXT
- [ ] Timestamps use TIMESTAMPTZ
- [ ] Cryptocurrency amounts preserve precision
- [ ] Required indexes exist
- [ ] Schema matches `DATABASE_SCHEMA.md`

## End-to-End Test

1. Start the backend.
2. Start the frontend.
3. Open the dashboard.
4. Create or select a case.
5. Enter a supported demo wallet address.
6. Select `ethereum`.
7. Submit analysis.
8. Confirm `POST /api/investigations/analyze` succeeds.
9. Confirm transactions are returned/stored.
10. Confirm graph nodes and edges are returned.
11. Confirm attribution results are returned.
12. Confirm risk score and indicators are returned.
13. Confirm the dashboard displays the results.
14. Confirm browser console has no blocking errors.
15. Confirm backend logs contain no unhandled exceptions.

## Fresh-Clone Test

A team member who did not develop the feature must test the repository from a clean clone using only `docs/SETUP.md`.

Success means:

```text
clone
→ configure .env
→ install dependencies
→ apply schema
→ start backend
→ start frontend
→ analyze demo wallet
→ see dashboard results
```

No manual source-code edits are allowed during this test.

## Merge Gate

Do not merge a feature if it changes an API field, database field, endpoint, enum, environment variable, or dependency without updating the relevant documentation and contract.
