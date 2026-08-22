# API Contract

## Project
SIH 26183 — Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics

**Status:** MVP / Mid-Evaluation
**Backend:** Flask REST API
**Database:** PostgreSQL / Supabase
**API prefix:** `/api`

This document is the single source of truth for frontend ↔ backend communication.

## Global Rules

All JSON responses use:

```json
{"success": true, "data": {}, "error": null}
```

Errors use:

```json
{"success": false, "data": null, "error": {"code": "ERROR_CODE", "message": "Human-readable message"}}
```

| Concept | API representation |
|---|---|
| UUID | string |
| Wallet address | string |
| Transaction hash | string |
| Cryptocurrency amount | string |
| Score | integer |
| Confidence | number 0–1 |
| Timestamp | ISO 8601 UTC string |
| Nullable | `null` |

Never represent cryptocurrency amounts as JavaScript floating-point values when precision matters.

## Canonical Enums

Chain: `ethereum`

Risk level: `low`, `medium`, `high`, `critical`

Transaction status: `pending`, `confirmed`, `failed`, `unknown`

Wallet type: `reported_wallet`, `intermediary`, `exchange`, `vasp`, `unknown`

Entity type: `vasp`, `exchange`, `bridge`, `defi_protocol`, `unknown`

Attribution match type: `known_address`, `entity_label`, `behavioral_match`, `cluster_match`, `unknown`

Indicator severity: `low`, `medium`, `high`, `critical`

# Endpoints

## Health

`GET /api/health`

```json
{"success": true, "data": {"status": "ok"}, "error": null}
```

## Create Case

`POST /api/cases`

Request:

```json
{
  "case_reference": "NCRP-DEMO-001",
  "fraud_type": "investment_scam",
  "description": "Suspected cryptocurrency fraud case"
}
```

Required: `case_reference`, `fraud_type`.

Response `201` returns the case with `id`, `case_reference`, `fraud_type`, `description`, `status`, `created_at`, and `updated_at`.

## Get Case

`GET /api/cases/{case_id}`

Returns the case object.

## Analyze Wallet

`POST /api/investigations/analyze`

Request:

```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "chain": "ethereum"
}
```

Response data:

```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "wallet": {
    "id": "650e8400-e29b-41d4-a716-446655440000",
    "address": "0x1234567890abcdef1234567890abcdef12345678",
    "chain": "ethereum",
    "type": "reported_wallet"
  },
  "analysis": {
    "status": "completed",
    "transaction_count": 42,
    "hop_count": 5,
    "total_transferred_value": "12.450000000000000000"
  },
  "risk": {"score": 87, "level": "high"},
  "attribution": {
    "entity_name": "Example Exchange",
    "entity_type": "vasp",
    "confidence": 0.92
  }
}
```

## Get Transactions

`GET /api/cases/{case_id}/transactions?page=1&limit=50`

Each transaction contains:

```json
{
  "id": "UUID",
  "transaction_hash": "0x...",
  "chain": "ethereum",
  "from_address": "0x...",
  "to_address": "0x...",
  "asset": "ETH",
  "amount": "1.250000000000000000",
  "block_number": 12345678,
  "timestamp": "2026-08-22T14:30:00Z",
  "status": "confirmed",
  "hop": 1
}
```

## Get Transaction Graph

`GET /api/cases/{case_id}/graph`

Response data contains `nodes` and `edges`.

Node:

```json
{"id":"wallet_001","address":"0x...","type":"reported_wallet","label":"Reported Wallet"}
```

Edge:

```json
{"id":"edge_001","source":"wallet_001","target":"wallet_002","transaction_hash":"0x...","amount":"1.250000000000000000","asset":"ETH","timestamp":"2026-08-22T14:30:00Z","hop":1}
```

## Get Attribution

`GET /api/cases/{case_id}/attribution`

Each attribution contains `id`, `wallet_address`, `entity_name`, `entity_type`, `match_type`, `confidence`, `evidence`, and `created_at`.

## Get Risk

`GET /api/cases/{case_id}/risk`

Response data contains `id`, `score` (0–100), `level`, `indicators`, and `created_at`.

An indicator contains `code`, `description`, `severity`, and optional evidence.

## Get Report

`GET /api/cases/{case_id}/report`

Returns the case, wallet, transactions, graph, attribution, and risk information used to display/generate the investigation report.

# Error Codes

`VALIDATION_ERROR`, `MISSING_FIELD`, `INVALID_WALLET_ADDRESS`, `UNSUPPORTED_CHAIN`, `CASE_NOT_FOUND`, `WALLET_NOT_FOUND`, `TRANSACTION_NOT_FOUND`, `ANALYSIS_FAILED`, `BLOCKCHAIN_PROVIDER_ERROR`, `DATABASE_ERROR`, `INTERNAL_ERROR`.

HTTP conventions: `200` success, `201` created, `400` invalid request, `404` missing resource, `409` conflict, `500` internal error, `502` provider failure.

# Integration Rules

- Frontend MUST use exact endpoint paths, field names, datatypes, and enum values.
- Backend MUST normalize external blockchain-provider responses before returning them.
- Frontend MUST NOT access the database directly.
- Backend MUST NOT expose provider-specific response structures.
- Attribution is an analytical association, not automatic proof of criminal ownership.
- Any contract change must update this file before dependent code is merged.
