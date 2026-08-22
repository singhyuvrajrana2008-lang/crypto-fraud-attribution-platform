# Setup Guide

## Goal

A fresh clone should be able to run the MVP with predictable commands and no developer-specific fixes.

## Prerequisites

- Git
- Python 3.12+
- Node.js 20+
- npm
- Supabase/PostgreSQL project

Verify:

```bash
git --version
python --version
node --version
npm --version
```

## Clone

```bash
git clone https://github.com/singhyuvrajrana2008-lang/crypto-fraud-attribution-platform.git
cd crypto-fraud-attribution-platform
```

## Environment

Copy `.env.example` to `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Never commit `.env`.

## Backend

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Run:

```bash
python backend/app.py
```

Expected development API:

`http://localhost:5000`

Health endpoint:

`GET /api/health`

Expected data:

```json
{"status":"ok"}
```

## Database

The Flask backend uses Supabase Postgres whenever `DATABASE_URL` is a `postgresql://` or `postgres://` URL. Copy `.env.example` to `.env`, set the Supabase database password in `DATABASE_URL`, and keep `REQUIRE_POSTGRES=true` in deployed environments so the backend fails fast instead of silently using local SQLite.

The current Supabase project URL is `https://gmlmjsqphbobzmmqcjlt.supabase.co`. Apply `database/schema.sql` in the Supabase SQL Editor only when provisioning a fresh database. Run `database/seed.sql` only when demo data is required. The schema must match `docs/DATABASE_SCHEMA.md`.

For local tests, omit `REQUIRE_POSTGRES` or set it to `false`; the test suite continues to use an in-memory SQLite connection.

## Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

If the frontend uses Vite, configure:

```text
VITE_API_BASE_URL=http://localhost:5000
```

The actual frontend must use the environment variable rather than scattering hardcoded API URLs through source files.

## Full Run

Terminal 1:

```powershell
cd crypto-fraud-attribution-platform
.\.venv\Scripts\Activate.ps1
python backend/app.py
```

Terminal 2:

```powershell
cd crypto-fraud-attribution-platform\frontend
npm run dev
```

## Clean Installation Test

A teammate who has not previously run the project must be able to:

1. Clone the repository.
2. Create `.env` from `.env.example`.
3. Install backend dependencies.
4. Install frontend dependencies.
5. Apply the database schema.
6. Start backend.
7. Start frontend.
8. Submit a demo wallet.
9. See analysis results.

If manual source-code changes are required, the setup is not complete.

## Configuration Rules

Secrets must be environment variables. Do not commit API keys, passwords, service-role keys, access tokens, or `.env`.

Backend dependencies belong in `backend/requirements.txt`. Frontend dependencies belong in `frontend/package.json`.

## Troubleshooting

### API connection failure

Check that Flask is running on the URL configured in `VITE_API_BASE_URL`.

### CORS failure

Check the configured frontend development origin and Flask CORS configuration. Do not disable security globally as a workaround.

### Database failure

Check `DATABASE_URL`, Supabase project status, credentials, and network connectivity.

### Dependency failure

Install from the committed dependency manifests. If a new dependency is required, add it to the appropriate manifest and commit the change.
