# Setup Guide

A fresh clone runs the SIH 26183 MVP with Flask, a PostgreSQL/Supabase production database, and a Vite frontend. The backend remains the single integration point for the frontend, database, and blockchain provider.

## Prerequisites

Install Git, Python 3.11+, Node.js 20+, npm, and a Supabase PostgreSQL project. Copy the environment template without committing the resulting `.env` file:

```bash
cp .env.example .env
```

Set `DATABASE_URL` to the Supabase PostgreSQL connection string and set `REQUIRE_POSTGRES=true` in deployed/demo environments. The backend then fails fast rather than silently switching to SQLite. `CORS_ORIGINS` should include the frontend origin, normally `http://localhost:5173`.

## Install and run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
psql "$DATABASE_URL" -f database/schema.postgres.sql
python backend/app.py
```

The API is available at `http://localhost:5000`. Verify it with:

```bash
curl http://localhost:5000/api/health
```

In another terminal:

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:5000 npm run dev
```

## Demo workflow

No manual SQL edits are required. After Flask starts, load deterministic, explicitly labelled demo data through the API:

```bash
curl -X POST http://localhost:5000/api/demo/seed
curl http://localhost:5000/api/dashboard/summary
curl 'http://localhost:5000/api/cases/top-priority?limit=10'
```

The seed creates 60 repeatable demo complaints, analyzes their bounded two-hop Ethereum mock flows, persists rule-based risk and investigation priority, creates potential VASP alerts, and establishes potentially related cases through observable shared-wallet evidence.

## Local tests

The test suite injects an in-memory SQLite database intentionally. This is test isolation only; it is not the production/demo persistence strategy.

```bash
PYTHONPATH=. pytest -q
```

The local SQLite schema is `database/schema.sqlite.sql`. The production schema is `database/schema.postgres.sql`; both support the same backend contract.

## Security and limitations

Never commit `.env`, database passwords, Supabase service-role keys, blockchain API keys, or tokens. The current provider is deterministic mock data unless a future provider adapter is explicitly configured. Risk and priority are transparent investigative signals; potential VASP association does not establish ownership, criminal identity, recovery, or asset freezing.
