# Crypto Fraud Attribution Platform

SIH Problem ID: **26183**

Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics.

## MVP

The MVP is designed around this flow:

```text
Victim-reported wallet
        ↓
Wallet validation
        ↓
Blockchain transaction retrieval
        ↓
Transaction normalization
        ↓
Transaction graph
        ↓
Known VASP/entity attribution
        ↓
Risk analysis
        ↓
Investigator dashboard
```

## Repository Structure

```text
frontend/       Frontend application
backend/        Flask REST API
database/       SQL schema and demo seed data
docs/           Integration contracts and setup documentation
.env.example    Environment variable template
```

## Integration Source of Truth

- `docs/API_CONTRACT.md` — frontend/backend API contract
- `docs/DATABASE_SCHEMA.md` — database contract
- `docs/SETUP.md` — fresh-clone setup
- `docs/ARCHITECTURE.md` — system architecture
- `docs/INTEGRATION_CHECKLIST.md` — final integration gate

## Quick Start

Follow `docs/SETUP.md` rather than inventing local setup steps.

Backend:

```bash
python -m venv .venv
pip install -r backend/requirements.txt
python backend/app.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The exact environment and database setup is documented in `docs/SETUP.md`.

## Team Rule

Do not change API paths, JSON fields, datatypes, enum values, database columns, or environment variable names independently. Update the relevant contract first, then update dependent code.

## Important Scope Note

Attribution and risk scores are investigative analytics. A potential VASP association or risk score must not be represented as automatic proof of criminal ownership.
