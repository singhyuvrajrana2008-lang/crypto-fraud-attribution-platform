# Pre-Implementation Gap Analysis

The audit compared the existing Flask repository with the SIH 26183 completion specification.

| Area | Before implementation | Resolution |
|---|---|---|
| Flask health, case creation, single-case retrieval | Implemented | Preserved and extended |
| Wallet analysis, normalized transactions, graph, risk, attribution, report | Partially implemented | Preserved and connected to persisted workflow |
| Production schema | Broken/inconsistent: `schema.sql` used SQLite constructs while documentation named PostgreSQL | Replaced with PostgreSQL schema and isolated SQLite test schema |
| Case listing and database-side filtering | Missing | Added pagination, search, filters, sorting, and totals |
| Deterministic complaint ingestion | Missing | Added idempotent 60-case demo seed |
| Investigation priority and Top 10 | Missing | Added transparent persisted rule-based priority engine and ranking endpoint |
| Cross-case correlation | Missing | Added potentially-related case relationships based on shared observable wallet-flow evidence |
| Dashboard summary and alerts | Missing | Added summary, recent alerts, generated alerts, and read state |
| Status management | Missing | Added canonical status transitions and audit events |
| Investigator notes | Missing | Added create, list, update, and delete endpoints |
| Audit trail | Missing | Added persistent case audit events |
| Tests | Only baseline tests | Added end-to-end completion tests and clean-clone pytest configuration |
| Frontend/API documentation | Incomplete | Updated API contract, database schema, and setup guide |

The implementation deliberately does not claim criminal identity, confirmed ownership, guaranteed recovery, or live blockchain intelligence. Demo analysis uses deterministic mock transactions and clearly labelled investigative signals.
