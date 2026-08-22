# Database Schema

The production database is **PostgreSQL through Supabase**. SQLite is retained only for isolated local tests and uses `database/schema.sqlite.sql`; production and demo persistence must use `DATABASE_URL` pointing to PostgreSQL.

All production primary keys are UUIDs. Wallet addresses and transaction hashes are `TEXT`; cryptocurrency amounts use `NUMERIC`; scores use `INTEGER`; timestamps use `TIMESTAMPTZ`; structured fields use `JSONB`.

| Table | Purpose | Key relationships |
|---|---|---|
| `users` | Investigator/admin metadata | Referenced by notes and audit logs |
| `cases` | Complaint, analysis status, and persisted priority summary | Root entity |
| `wallets` | Canonical wallet identities by chain | Referenced by case wallets and transactions |
| `case_wallets` | Case-to-wallet roles | `cases` ↔ `wallets` |
| `transactions` | Normalized blockchain transactions | References source and destination wallets |
| `case_transactions` | Case-to-transaction scope | `cases` ↔ `transactions` |
| `entities` | Potential VASP/exchange labels | Referenced by attributions |
| `wallet_entity_labels` | Label sources and confidence | `wallets` ↔ `entities` |
| `attributions` | Explainable potential associations | References cases, wallets, entities |
| `analysis_results` | Provider-agnostic analysis status | References cases |
| `risk_assessments` | Rule-based risk score and level | References cases |
| `risk_indicators` | Evidence behind risk assessments | References risk assessments |
| `priorities` | Rule-based investigation priority and factors | One row per case |
| `case_relationships` | Potentially related cases and observable evidence | Case-to-case relationship |
| `alerts` | Generated investigator alerts | References cases |
| `investigation_notes` | Investigator notes | References cases and optional users |
| `investigation_reports` | Persistable report payloads | References cases |
| `audit_logs` | Case activity trail | References cases and optional users |

The canonical case statuses are `new`, `analyzing`, `under_review`, `escalated`, and `closed`. Risk levels are `low`, `medium`, `high`, and `critical`. Demo blockchain data is deterministic mock data and is explicitly labelled; a potential VASP association is not a confirmed owner or criminal attribution.

Apply the production schema with:

```bash
psql "$DATABASE_URL" -f database/schema.postgres.sql
```

The normal demo workflow uses `POST /api/demo/seed`; no manual SQL edits are required.
