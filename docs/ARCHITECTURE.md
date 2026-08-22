# Architecture

## High-Level Flow

```text
Investigator
    ↓
Frontend Dashboard
    ↓ REST/JSON
Flask API
    ↓
Backend Services
    ├── Blockchain Adapter
    ├── Transaction Normalizer
    ├── Graph Service
    ├── Attribution Service
    └── Risk Service
    ↓
PostgreSQL / Supabase
```

## Frontend

Responsibilities:

- Case intake
- Wallet input
- API communication
- Investigation dashboard
- Transaction table/timeline
- Transaction graph
- Attribution display
- Risk display

Frontend must not directly query database tables or contain blockchain-provider logic.

## Backend

Responsibilities:

- API routes
- Validation
- Database access
- Blockchain provider integration
- Provider response normalization
- Transaction graph construction
- VASP/entity matching
- Risk analysis
- Report data assembly

Recommended layers:

```text
backend/
├── app.py
├── routes/
├── services/
├── models/
└── utils/
```

## Blockchain Data Flow

```text
Wallet Address
    ↓
Validation
    ↓
Blockchain Provider
    ↓
Raw Provider Response
    ↓
Normalization
    ↓
Normalized Transactions
    ↓
Database / Graph Engine
```

The frontend must never depend on provider-specific response formats.

## Transaction Graph

Nodes represent wallets/entities. Edges represent transactions.

```text
Reported Wallet
      ↓
Intermediary A
      ↓
Intermediary B
      ↓
Potential VASP
```

The graph response is defined by `API_CONTRACT.md`.

## Attribution

Attribution is evidence-based. The system can return known-address matches, labels, cluster/behavioral matches, confidence, and evidence. A potential association must not be presented as proof of criminal ownership.

## Risk Analysis

For the MVP, rule-based scoring is sufficient. Example indicators include multi-hop movement, rapid movement, splitting/consolidation, and interaction with known entities.

Advanced ML, multi-chain tracing, bridges, DeFi, and large-scale indexing are future extensions unless explicitly implemented.

## Database

PostgreSQL/Supabase stores cases, wallets, transactions, entities, wallet/entity labels, attribution results, and risk assessments.

The database source of truth is `DATABASE_SCHEMA.md` plus the committed SQL/migrations.

## Integration Rule

```text
API_CONTRACT.md
       ↓
Frontend + Backend
       ↓
DATABASE_SCHEMA.md
       ↓
Database
```

Any change to endpoint paths, JSON fields, datatypes, enums, or database relationships must update the relevant contract before dependent work is merged.
