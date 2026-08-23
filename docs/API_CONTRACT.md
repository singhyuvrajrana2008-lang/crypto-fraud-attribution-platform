# API Contract

The backend is a Flask REST API under `/api`. Every response uses the envelope `{"success": true, "data": {}, "error": null}`. Errors use `{"success": false, "data": null, "error": {"code": "ERROR_CODE", "message": "..."}}`.

| Concept | Representation |
|---|---|
| UUID | JSON string |
| Amount | Decimal-preserving JSON string |
| Score | Integer from 0 to 100 |
| Confidence | Number from 0 to 1 |
| Timestamp | ISO 8601 UTC string |

Canonical chain is `ethereum`. Case statuses are `new`, `analyzing`, `under_review`, `escalated`, and `closed`. Risk levels are `low`, `medium`, `high`, and `critical`.

## Core endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Dependency-independent health check |
| `POST` | `/api/cases` | Create a complaint; requires `case_reference` and `fraud_type`; accepts amount, currency, wallet, blockchain, description |
| `GET` | `/api/cases/{case_id}` | Frontend-ready case detail including analysis, risk, priority, related count, and VASP summary |
| `DELETE` | `/api/cases/{case_id}` | Delete a complaint and its dependent case evidence; returns recalculated linked case IDs |
| `PATCH` | `/api/cases/{case_id}` | Update `description`, `fraud_type`, or `currency` |
| `PATCH` | `/api/cases/{case_id}/status` | Change status with `{ "status": "under_review" }`; writes an audit event |
| `POST` | `/api/investigations/analyze` | Analyze `{case_id, wallet_address, chain}` using the normalized deterministic mock provider |
| `GET` | `/api/cases/{case_id}/transactions?page=1&limit=50` | Paginated normalized transactions |
| `GET` | `/api/cases/{case_id}/graph` | Graph `{nodes, edges}` ready for rendering |
| `GET` | `/api/cases/{case_id}/risk` | Risk score, level, indicators, and evidence |
| `GET` | `/api/cases/{case_id}/priority` | Persisted investigation priority score and factors |
| `GET` | `/api/cases/{case_id}/attribution` | Explainable potential VASP associations |
| `GET /api/cases/{case_id}/related` | Potentially related cases and observable shared-wallet evidence in either relationship direction |
| `GET` | `/api/cases/{case_id}/report` | Live case, wallet, timeline, graph, risk, priority, related, attribution, and evidence payload |
| `GET` | `/api/cases/{case_id}/audit` | Case audit trail |

## Case listing and ranking

`GET /api/cases` supports database-side `page`, `limit`, `search`, `status`, `risk_level` (or `risk`), `fraud_type`, `blockchain`, `min_amount`, `max_amount`, `date_from`, `date_to`, `vasp`, `sort`, and `order`. Sort values are `priority`, `priority_score`, `risk_score`, `amount`, and `created_at`. It returns `{page, limit, total, items}`. Search covers case reference, reported wallet address, and transaction hash.

`GET /api/cases/top-priority?limit=10` returns actual backend-ranked items. The UI exposes this response in the Operations / Top 10 priority queue. Its `Open case` action currently displays a coming-soon notice because a dedicated case-detail dashboard is not yet wired; the Live Demo remains the supported case-opening workflow. Each item includes `rank`, `case_id`, `id`, `case_reference`, `reported_amount`, `currency`, `fraud_type`, `reported_wallet_address`, `blockchain`, `priority_score`, `risk_score`, `risk_level`, `related_case_count`, `status`, and `created_at`.

## Dashboard, alerts, notes, and demo ingestion

| Method | Path | Request/response |
|---|---|---|
| `GET` | `/api/dashboard/summary` | Summary counts, total amount, VASP count, relationship count, and recent alert count |
| `GET` | `/api/dashboard/recent-alerts` | Latest ten alerts |
| `POST` | `/api/demo/seed` | Idempotently creates and analyzes 60 deterministic demo cases |
| `GET` | `/api/alerts` | Alerts; optional `read=0` or `read=1` filter |
| `PATCH` | `/api/alerts/{alert_id}/read` | Optional `{ "read": true }`; marks an alert read/unread |
| `GET` | `/api/cases/{case_id}/notes` | List investigator notes |
| `POST` | `/api/cases/{case_id}/notes` | Requires non-empty `{ "note": "..." }` |
| `PATCH` | `/api/notes/{note_id}` | Replace a note with non-empty `note` |
| `DELETE` | `/api/notes/{note_id}` | Delete a note |

When analysis discovers a relationship, both cases receive reciprocal relationship rows and their persisted risk/priority records are recalculated using the updated linked-case count. Deleting a complaint removes its dependent records and recalculates surviving linked cases. The UI requires confirmation before deletion.

Alerts use `HIGH_RISK_CASE`, `MULTIPLE_RELATED_CASES`, `VASP_MATCH`, and `HIGH_FINANCIAL_IMPACT` where evidence supports generation. Demo data is not real cybercrime intelligence. Risk, priority, related-case detection, and attribution are investigative signals, not proof of criminal identity, ownership, or wrongdoing.

## Normalized transaction and graph shapes

Transactions contain `id`, `transaction_hash`, `chain`, `from_address`, `to_address`, `asset`, `amount`, `block_number`, `timestamp`, `status`, and `hop`. Graph nodes contain `id`, `address`, `type`, and `label`; graph edges contain `id`, `source`, `target`, `transaction_hash`, `amount`, `asset`, `timestamp`, and `hop`.

## Error codes

Common codes are `VALIDATION_ERROR`, `MISSING_FIELD`, `INVALID_WALLET_ADDRESS`, `UNSUPPORTED_CHAIN`, `INVALID_STATUS`, `CASE_NOT_FOUND`, `ALERT_NOT_FOUND`, `NOTE_NOT_FOUND`, `CONFLICT`, and `INTERNAL_ERROR`. HTTP status conventions are `200`, `201`, `400`, `404`, `409`, and `500`.
