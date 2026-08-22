# Database Schema

## Project
SIH 26183 — Crypto Fraud Attribution Platform

**Database:** PostgreSQL / Supabase

This is the database source of truth for the MVP. Backend models and migrations must match it.

## Rules

- Entity IDs use UUID.
- Wallet addresses and transaction hashes use TEXT.
- Timestamps use TIMESTAMPTZ in UTC.
- Cryptocurrency amounts must preserve precision; API representation is a string.
- Foreign keys use the same datatype as referenced primary keys.
- Frontend never accesses database tables directly.

## Tables

### cases

| Column | Type | Null | Notes |
|---|---|---|---|
| id | UUID | NO | PK |
| case_reference | TEXT | NO | Human-readable case reference |
| fraud_type | TEXT | NO | Fraud category |
| description | TEXT | YES | Case description |
| status | TEXT | NO | Case status |
| created_at | TIMESTAMPTZ | NO | Creation time |
| updated_at | TIMESTAMPTZ | NO | Last update |

### wallets

| Column | Type | Null | Notes |
|---|---|---|---|
| id | UUID | NO | PK |
| address | TEXT | NO | Blockchain address |
| chain | TEXT | NO | Canonical chain identifier |
| wallet_type | TEXT | NO | Wallet classification |
| first_seen_at | TIMESTAMPTZ | YES | First observed transaction |
| last_seen_at | TIMESTAMPTZ | YES | Last observed transaction |
| created_at | TIMESTAMPTZ | NO | Creation time |

Recommended unique constraint: `(address, chain)`.

### transactions

| Column | Type | Null | Notes |
|---|---|---|---|
| id | UUID | NO | PK |
| transaction_hash | TEXT | NO | Blockchain transaction hash |
| chain | TEXT | NO | Blockchain |
| from_wallet_id | UUID | NO | FK wallets.id |
| to_wallet_id | UUID | NO | FK wallets.id |
| asset | TEXT | NO | Asset/token |
| amount | TEXT | NO | Exact amount representation |
| block_number | BIGINT | YES | Block number |
| timestamp | TIMESTAMPTZ | NO | Transaction time |
| status | TEXT | NO | Transaction status |
| hop | INTEGER | YES | Investigation hop |
| created_at | TIMESTAMPTZ | NO | Insert time |

### entities

| Column | Type | Null | Notes |
|---|---|---|---|
| id | UUID | NO | PK |
| name | TEXT | NO | Entity name |
| type | TEXT | NO | VASP/exchange/etc. |
| verification_status | TEXT | NO | Verification state |
| created_at | TIMESTAMPTZ | NO | Creation time |

### wallet_entity_labels

| Column | Type | Null | Notes |
|---|---|---|---|
| id | UUID | NO | PK |
| wallet_id | UUID | NO | FK wallets.id |
| entity_id | UUID | NO | FK entities.id |
| source | TEXT | NO | Attribution source |
| confidence | NUMERIC | YES | 0–1 |
| created_at | TIMESTAMPTZ | NO | Creation time |

### attributions

| Column | Type | Null | Notes |
|---|---|---|---|
| id | UUID | NO | PK |
| case_id | UUID | NO | FK cases.id |
| wallet_id | UUID | NO | FK wallets.id |
| entity_id | UUID | YES | FK entities.id |
| match_type | TEXT | NO | Attribution method |
| confidence | NUMERIC | YES | 0–1 |
| evidence | JSONB | YES | Supporting evidence |
| created_at | TIMESTAMPTZ | NO | Creation time |

### risk_assessments

| Column | Type | Null | Notes |
|---|---|---|---|
| id | UUID | NO | PK |
| case_id | UUID | NO | FK cases.id |
| score | INTEGER | NO | 0–100 |
| level | TEXT | NO | Risk category |
| created_at | TIMESTAMPTZ | NO | Creation time |

### risk_indicators

| Column | Type | Null | Notes |
|---|---|---|---|
| id | UUID | NO | PK |
| risk_assessment_id | UUID | NO | FK risk_assessments.id |
| code | TEXT | NO | Machine-readable indicator |
| description | TEXT | NO | Explanation |
| severity | TEXT | NO | Indicator severity |
| evidence | JSONB | YES | Supporting evidence |

## Relationships

```text
cases
 ├── attributions
 └── risk_assessments
       └── risk_indicators

wallets
 ├── transactions (sender/receiver)
 └── wallet_entity_labels
       └── entities

entities
 └── attributions
```

## Canonical Values

Chain MVP: `ethereum`

Wallet types: `reported_wallet`, `intermediary`, `exchange`, `vasp`, `unknown`

Risk levels: `low`, `medium`, `high`, `critical`

Transaction statuses: `pending`, `confirmed`, `failed`, `unknown`

Entity types: `vasp`, `exchange`, `bridge`, `defi_protocol`, `unknown`

## Required Indexes

Recommended indexes: wallet address, wallet chain, transaction hash, transaction chain, transaction timestamp, transaction sender, transaction receiver, attribution case, risk assessment case.

## Datatype Rules

Never store wallet addresses or transaction hashes as numeric types. Never store cryptocurrency values as FLOAT. Never store UUID foreign keys as INTEGER. Never use plain TEXT for timestamps when a timestamp type is available.

Any schema change must update this document, migrations/schema.sql, backend models, and API_CONTRACT.md if the API is affected.
