You are the SENIOR BACKEND ENGINEER for our SIH 2026 project.

PROJECT:
SIH 26183 — Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics

GITHUB:
https://github.com/singhyuvrajrana2008-lang/crypto-fraud-attribution-platform

============================================================
MISSION
============================================================

Build and complete the Flask backend so the entire frontend can operate from the backend without manual database editing, hardcoded responses, datatype conversions, or frontend workarounds.

The final MVP must support this complete workflow:

COMPLAINTS
    ↓
CASE CREATION / INGESTION
    ↓
WALLET ANALYSIS
    ↓
BLOCKCHAIN TRANSACTION DATA
    ↓
TRANSACTION NORMALIZATION
    ↓
MULTI-HOP FUND-FLOW ANALYSIS
    ↓
GRAPH GENERATION
    ↓
RISK ANALYSIS
    ↓
INVESTIGATION PRIORITY
    ↓
TOP 10 PRIORITY CASES
    ↓
RELATED CASE DETECTION
    ↓
POTENTIAL VASP / EXCHANGE ATTRIBUTION
    ↓
ALERTS
    ↓
INVESTIGATOR NOTES
    ↓
INVESTIGATION REPORT
    ↓
AUDIT TRAIL
    ↓
FRONTEND DASHBOARD

============================================================
NON-NEGOTIABLE TECHNOLOGY
============================================================

Backend framework:
Flask

Language:
Python

Database:
PostgreSQL through Supabase

Frontend communication:
REST API

Data format:
JSON

Environment:
.env

Do NOT migrate the backend to FastAPI, Django, Node, Express, or another framework.

Do NOT rewrite the existing Flask backend merely to use a different architecture.

Improve and complete the existing Flask implementation.

============================================================
FIRST STEP: INSPECT THE REPOSITORY
============================================================

Before modifying anything, inspect the actual GitHub repository.

Read:

docs/API_CONTRACT.md
docs/DATABASE_SCHEMA.md
docs/ARCHITECTURE.md
docs/SETUP.md
docs/INTEGRATION_CHECKLIST.md
README.md
.env.example

Then inspect:

backend/
frontend/
database/

Also inspect:

requirements.txt
existing Flask app
existing routes
existing models
existing services
existing tests
environment handling
frontend API calls
database schema
database seed data

IMPORTANT:

Do not assume the repository is empty.

Do not replace working code without understanding it.

The repository's existing implementation takes priority over assumptions in this prompt.

Priority order:

1. Existing working repository implementation
2. API_CONTRACT.md
3. DATABASE_SCHEMA.md
4. ARCHITECTURE.md
5. This prompt
6. Your implementation preferences

If two requirements conflict:

STOP.

Identify the conflict and resolve it deliberately.

Never silently change an API field, database field, endpoint, datatype, or enum.

============================================================
FLASK APPLICATION ARCHITECTURE
============================================================

Keep Flask as the main application framework.

Use a modular structure similar to:

backend/
│
├── app.py
├── config.py
├── requirements.txt
│
├── routes/
│   ├── auth.py
│   ├── health.py
│   ├── cases.py
│   ├── investigations.py
│   ├── transactions.py
│   ├── graph.py
│   ├── risk.py
│   ├── priority.py
│   ├── attribution.py
│   ├── related_cases.py
│   ├── alerts.py
│   ├── notes.py
│   ├── reports.py
│   └── audit.py
│
├── services/
│   ├── case_service.py
│   ├── blockchain_service.py
│   ├── transaction_service.py
│   ├── graph_service.py
│   ├── risk_service.py
│   ├── priority_service.py
│   ├── attribution_service.py
│   ├── correlation_service.py
│   ├── alert_service.py
│   ├── report_service.py
│   └── audit_service.py
│
├── providers/
│   ├── base.py
│   ├── mock_provider.py
│   └── live_provider.py
│
├── models/
│   ├── case.py
│   ├── wallet.py
│   ├── transaction.py
│   ├── risk.py
│   └── attribution.py
│
├── utils/
│   ├── validators.py
│   ├── responses.py
│   ├── timestamps.py
│   └── errors.py
│
└── tests/

You may keep the repository's existing structure if it already follows the same responsibilities.

Do not create unnecessary abstraction layers.

============================================================
APPLICATION STARTUP
============================================================

The backend must start with:

python backend/app.py

or the existing documented Flask command.

It must:

1. Load environment variables.
2. Create Flask application.
3. Configure CORS.
4. Register routes.
5. Configure database access.
6. Register error handlers.
7. Start successfully without requiring undocumented manual steps.

============================================================
ENVIRONMENT VARIABLES
============================================================

Use environment variables.

Possible variables:

DATABASE_URL=
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SECRET_KEY=
BLOCKCHAIN_PROVIDER=mock
BLOCKCHAIN_API_URL=
BLOCKCHAIN_API_KEY=
FRONTEND_ORIGIN=

Only require variables that the actual implementation needs.

Never hardcode credentials.

Never commit .env.

Update .env.example when new variables are required.

============================================================
GLOBAL API RESPONSE FORMAT
============================================================

Every API response must follow the contract.

Success:

{
  "success": true,
  "data": {},
  "error": null
}

Error:

{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}

Do not return random structures such as:

{
  "message": "ok"
}

from one endpoint and another format elsewhere.

============================================================
DATATYPE RULES
============================================================

UUID:
string in JSON

Wallet address:
string

Transaction hash:
string

Blockchain:
canonical string/enum

Amount:
string where precision could otherwise be lost

Risk score:
integer/number

Confidence:
number 0–1

Timestamp:
ISO 8601 UTC string

Boolean:
true / false

Nullable:
null

NEVER:

- cast wallet addresses to numbers
- cast transaction hashes to numbers
- use floating-point arithmetic for precise cryptocurrency amounts
- return inconsistent enum capitalization
- randomly replace null with ""

============================================================
CORS
============================================================

Configure CORS for the actual frontend development origin.

Do not disable security globally.

Use environment configuration for allowed origins where practical.

Typical development origin:

http://localhost:5173

Do not hardcode multiple unrelated origins throughout the project.

============================================================
HEALTH ENDPOINT
============================================================

Implement:

GET /api/health

Response:

{
  "success": true,
  "data": {
    "status": "ok"
  },
  "error": null
}

This must work even if an external blockchain provider is unavailable.

============================================================
AUTHENTICATION
============================================================

Support investigator authentication if the current project requires it.

Endpoints:

POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me

Roles:

investigator
admin

For the mid-evaluation, authentication may be simplified if necessary, but protected endpoint structure must remain clean.

Never expose passwords or secrets.

============================================================
CASE / COMPLAINT MANAGEMENT
============================================================

Cases represent incoming cyber-fraud complaints.

Support:

POST /api/cases
GET /api/cases
GET /api/cases/{case_id}
PATCH /api/cases/{case_id}
PATCH /api/cases/{case_id}/status

Case data may include:

case_number
fraud_type
reported_amount
currency
reported_wallet_address
blockchain
description
source
complaint_date
status

Status values:

new
analyzing
under_review
escalated
closed

The backend owns case validation and storage.

============================================================
COMPLAINT INGESTION
============================================================

The project pitch assumes complaints can enter the system.

For the MVP, support controlled demo complaint ingestion.

Create an appropriate demo seed mechanism, such as:

POST /api/demo/seed

or the repository's existing equivalent.

The demo dataset should contain enough cases to demonstrate:

- ranking
- related complaints
- different fraud types
- different amounts
- different risk levels
- repeated wallet activity
- potential VASP associations

Demo data must be clearly labelled as demo/test data.

Never represent fabricated data as real cybercrime intelligence.

============================================================
BLOCKCHAIN PROVIDER ABSTRACTION
============================================================

Do not put blockchain-provider-specific code directly inside Flask routes.

Use:

Flask route
    ↓
Investigation service
    ↓
Blockchain service
    ↓
Provider adapter

Create a provider interface conceptually:

BlockchainProvider
├── MockBlockchainProvider
└── LiveBlockchainProvider

Environment:

BLOCKCHAIN_PROVIDER=mock

must allow the entire MVP to run without external blockchain credentials.

The mock and live providers must return the SAME normalized transaction structure.

The frontend must never know which provider generated the data.

============================================================
LIVE BLOCKCHAIN DATA
============================================================

When a live provider is configured:

1. Validate wallet address.
2. Request relevant transaction data.
3. Normalize response.
4. Handle provider errors.
5. Apply configured analysis limits.
6. Store relevant results.

Never store the entire blockchain.

Only retrieve relevant indexed transaction data.

============================================================
WALLET VALIDATION
============================================================

Validate:

- wallet address present
- wallet address format
- supported blockchain
- required fields
- malformed input

Return appropriate errors.

Example:

{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_WALLET_ADDRESS",
    "message": "The wallet address is invalid for the selected blockchain."
  }
}

============================================================
TRANSACTION NORMALIZATION
============================================================

Every provider response must be converted to the standard model.

Example:

{
  "id": "uuid",
  "transaction_hash": "0x...",
  "blockchain": "ethereum",
  "from_address": "0x...",
  "to_address": "0x...",
  "amount": "1.250000000000000000",
  "asset": "ETH",
  "timestamp": "2026-08-23T00:00:00Z",
  "block_number": 123456,
  "status": "confirmed",
  "hop": 1
}

Do not leak provider-specific fields to the frontend.

============================================================
MULTI-HOP FUND FLOW ANALYSIS
============================================================

Implement wallet-flow traversal.

Starting wallet:

reported wallet

Process:

1. Retrieve relevant transactions.
2. Identify destinations.
3. Follow relevant destinations.
4. Assign hop numbers.
5. Track visited wallets.
6. Avoid cycles.
7. Avoid duplicate transactions.
8. Respect maximum hop depth.
9. Construct graph.
10. Store relevant results.

Support configurable maximum hops.

Possible MVP default:

3–5 hops

Do not allow unlimited graph expansion by default.

Return:

transaction_count
wallet_count
hop_count
first_seen
last_seen
total relevant value where valid
nodes
edges

============================================================
GRAPH SERVICE
============================================================

The frontend must receive graph-ready data.

Nodes:

{
  "id": "wallet_001",
  "wallet_id": "uuid",
  "address": "0x...",
  "type": "reported_wallet",
  "label": "Reported Wallet"
}

Edges:

{
  "id": "edge_001",
  "source": "wallet_001",
  "target": "wallet_002",
  "transaction_id": "uuid",
  "transaction_hash": "0x...",
  "amount": "1.25",
  "asset": "ETH",
  "timestamp": "2026-08-23T00:00:00Z",
  "hop": 1
}

Node IDs and edge IDs must remain stable within an investigation result.

The frontend must not reconstruct the graph from raw transactions.

============================================================
TRANSACTION ENDPOINT
============================================================

Implement:

GET /api/cases/{case_id}/transactions

Support pagination.

Allow:

page
limit
sort

Return:

transactions
pagination

============================================================
TRANSACTION TIMELINE
============================================================

The backend should provide all fields necessary for chronological display:

transaction hash
from address
to address
amount
asset
timestamp
hop
status

Frontend should be able to sort or use backend ordering.

============================================================
RISK ENGINE
============================================================

Implement an explainable rule-based MVP risk engine.

Possible indicators:

MULTI_HOP
RAPID_MOVEMENT
FUND_SPLITTING
FUND_CONSOLIDATION
REPEATED_ACTIVITY
VASP_INTERACTION
MULTIPLE_RELATED_CASES
HIGH_FINANCIAL_IMPACT

Each indicator must contain:

code
description
severity
weight
evidence where appropriate

Risk output:

{
  "score": 87,
  "level": "high",
  "indicators": [...]
}

Risk levels:

low
medium
high

Do not claim that a risk score proves criminal activity.

Risk means:

investigative attention / prioritization

not:

legal guilt

============================================================
PRIORITY ENGINE
============================================================

Priority and risk are DIFFERENT.

Risk asks:

"How suspicious does the observed activity look?"

Priority asks:

"Which case should an investigator examine first?"

Priority should combine documented signals such as:

- financial impact
- number of linked complaints
- repeated wallet activity
- suspicious fund movement
- potential VASP interaction
- other approved indicators

Return:

priority_score
priority_rank
priority_factors

Example:

{
  "priority_rank": 1,
  "priority_score": 91,
  "priority_factors": {
    "financial_impact": 75,
    "linked_cases": 95,
    "repeated_activity": 90,
    "fund_movement": 85
  }
}

Do not allow the frontend to calculate these scores.

Backend is the source of truth.

============================================================
TOP 10 PRIORITY CASES
============================================================

Implement:

GET /api/cases/top-priority?limit=10

Default limit:

10

Return:

rank
case_id
case_number
reported_amount
currency
fraud_type
reported_wallet_address
blockchain
priority_score
risk_score
risk_level
related_case_count
status
created_at

The dashboard must be able to render the top 10 directly from this endpoint.

============================================================
CASE SEARCH / FILTERING
============================================================

GET /api/cases

Support filters:

search
status
risk_level
fraud_type
blockchain
min_amount
max_amount
date_from
date_to

Support sorting:

priority
priority_score
risk_score
amount
created_at

Support pagination.

Filtering should happen server-side wherever practical.

============================================================
CROSS-CASE CORRELATION
============================================================

Detect potentially related complaints using observable relationships:

shared_wallet
shared_downstream_wallet
shared_destination
common_vasp
common_transaction_pattern

Endpoint:

GET /api/cases/{case_id}/related

Return:

related_case_id
relationship_type
confidence
evidence
shared wallet/destination when applicable

Do not automatically claim:

"same criminal"

because two cases share an address.

Use:

"potentially related cases"

============================================================
VASP / ENTITY ATTRIBUTION
============================================================

Implement evidence-based matching.

Endpoint:

GET /api/cases/{case_id}/attribution

Return:

entity_name
entity_type
confidence
match_type
evidence
source
wallet_address

Possible entity types:

vasp
exchange
bridge
defi_protocol
unknown

Possible match types:

known_address
entity_label
behavioral_match
cluster_match
unknown

Use:

Potential VASP Association

not:

Confirmed owner

unless authoritative evidence exists.

============================================================
RISK + PRIORITY + ATTRIBUTION COMBINED CASE VIEW
============================================================

The case detail API should provide enough information for the frontend to display:

- case summary
- risk
- priority
- transaction count
- hop count
- related case count
- potential VASP
- analysis status

Do not make the frontend call 15 endpoints just to display one case if a clean aggregated case endpoint is appropriate.

============================================================
ALERTS
============================================================

Generate alerts for:

HIGH_RISK_CASE
MULTIPLE_RELATED_CASES
RAPID_FUND_MOVEMENT
VASP_MATCH
HIGH_FINANCIAL_IMPACT

Support:

GET /api/alerts

PATCH /api/alerts/{alert_id}/read

Alert fields:

id
case_id
type
title
message
severity
read
created_at

============================================================
CASE STATUS
============================================================

Implement:

PATCH /api/cases/{case_id}/status

Store:

old status
new status
changed_by
changed_at

Also create an audit record.

============================================================
INVESTIGATOR NOTES
============================================================

Implement:

GET /api/cases/{case_id}/notes
POST /api/cases/{case_id}/notes
PATCH /api/notes/{note_id}
DELETE /api/notes/{note_id}

Store:

case_id
user_id
note
created_at
updated_at

============================================================
INVESTIGATION REPORT
============================================================

Implement:

GET /api/cases/{case_id}/report

The report data should aggregate:

case
wallet
transactions
timeline
graph
risk
priority
related cases
VASP associations
evidence
analysis timestamps

PDF generation can be implemented as a P1 feature if the main workflow is already stable.

If PDF is implemented:

POST /api/cases/{case_id}/report/pdf

Do not allow report generation to break the core investigation workflow.

============================================================
AUDIT LOG
============================================================

Track:

CASE_CREATED
CASE_VIEWED
ANALYSIS_STARTED
ANALYSIS_COMPLETED
ANALYSIS_FAILED
STATUS_CHANGED
NOTE_ADDED
REPORT_GENERATED
VASP_ASSOCIATION_FOUND

Endpoint:

GET /api/cases/{case_id}/audit

Fields:

id
user_id
case_id
action
details
created_at

============================================================
DATABASE INTEGRATION
============================================================

Use Supabase/PostgreSQL.

Do not create a conflicting local database abstraction if the project already has Supabase integration.

Support the agreed tables:

users
cases
wallets
case_wallets
transactions
case_transactions
analysis_results
risk_assessments
risk_indicators
case_relationships
vasp_associations
alerts
investigation_notes
investigation_reports
audit_logs

Every backend model/operation must use the documented schema.

Canonical naming must remain consistent:

case_id
wallet_id
transaction_id
entity_id
priority_score
risk_score
risk_level
created_at
updated_at

Do not silently rename fields.

============================================================
DATABASE TRANSACTIONS / CONSISTENCY
============================================================

Where an investigation writes multiple related records:

case
wallets
transactions
analysis
risk
relationships
attribution

use transactional or otherwise safe database operations where supported.

Do not leave half-written investigations whenever possible.

============================================================
FRONTEND CONTRACT
============================================================

The frontend must NOT:

- query Supabase directly
- call blockchain providers directly
- calculate risk
- calculate priority
- determine VASP attribution
- reconstruct graph logic
- perform case correlation

Backend returns the answers.

Frontend displays them.

============================================================
SECURITY
============================================================

Use:

- environment variables
- input validation
- role checks where applicable
- controlled database access
- no secrets in code
- no stack traces in API responses
- safe error messages
- secure CORS

Do not expose Supabase service-role credentials to the frontend.

============================================================
DEPENDENCIES
============================================================

Use only necessary Python packages.

Likely dependencies may include:

Flask
Flask-CORS
python-dotenv
requests
Supabase/PostgreSQL client
pytest

Use NetworkX only if the actual implementation benefits from it.

Do not add machine-learning frameworks unless a real ML feature requires them.

Do not add packages merely to make the technology stack look impressive.

Every dependency must be added to:

backend/requirements.txt

============================================================
TESTING
============================================================

Create automated tests for:

GET /api/health

authentication

case creation

case retrieval

case filtering

invalid wallet

unsupported blockchain

missing required fields

wallet analysis

transactions

graph

risk

priority

top 10

related cases

attribution

alerts

notes

reports

audit

database operations

At minimum verify the complete workflow:

demo complaints
→ analysis
→ transaction data
→ graph
→ risk
→ priority
→ related cases
→ VASP
→ frontend-ready response

============================================================
END-TO-END ACCEPTANCE TEST
============================================================

A clean test should be:

1. Start Flask.
2. Start frontend.
3. Load demo complaints.
4. Display complaint list.
5. Run analysis.
6. Store results.
7. Calculate risk.
8. Calculate priority.
9. Return top 10.
10. Open priority #1.
11. Show transaction timeline.
12. Show fund-flow graph.
13. Show related cases.
14. Show potential VASP.
15. Show alerts.
16. Show notes.
17. Generate/read report.
18. Show audit trail.

No manual SQL editing should be necessary during this flow.

============================================================
DEMO DATA REQUIREMENT
============================================================

Create deterministic demo data sufficient to produce a convincing dashboard.

Include cases with:

- different fraud types
- different financial amounts
- different numbers of related complaints
- multiple-hop flows
- at least one potential VASP association
- different risk levels
- different priority scores
- at least one cluster of related cases

The demo should produce a meaningful Top 10 list.

Do not use random data that changes every run.

============================================================
DEFINITION OF DONE
============================================================

Backend is NOT complete merely because Flask starts.

Backend is complete only when:

[ ] Flask runs successfully
[ ] Supabase/PostgreSQL connection works
[ ] API contract is satisfied
[ ] frontend can consume the APIs
[ ] complaints can be loaded
[ ] complaint data is stored
[ ] wallet analysis works
[ ] transactions are normalized
[ ] multi-hop analysis works
[ ] graph data is returned
[ ] transaction timeline works
[ ] risk score works
[ ] priority score works
[ ] priority ranking works
[ ] top 10 works
[ ] cross-case correlation works
[ ] VASP association works
[ ] alerts work
[ ] status changes work
[ ] notes work
[ ] report data works
[ ] audit log works
[ ] search/filter works
[ ] errors are consistent
[ ] no secrets are committed
[ ] setup works from a clean clone
[ ] no frontend/database workarounds are required

============================================================
FINAL INTEGRATION AUDIT
============================================================

Before declaring success, verify this exact chain:

Frontend input
↓
Flask route
↓
validation
↓
service
↓
blockchain provider/mock provider
↓
normalization
↓
graph/risk/priority/correlation analysis
↓
Supabase/PostgreSQL
↓
structured API response
↓
frontend rendering

For every important field compare:

DATABASE
↓
BACKEND
↓
API_CONTRACT
↓
FRONTEND

The field names and datatypes must match.

Examples:

case_id
wallet_address
transaction_hash
priority_score
risk_score
risk_level
related_case_count
confidence
created_at

Do not leave integration problems for the team lead to discover.

============================================================
FINAL REPORT
============================================================

When finished, report:

1. Files created/modified
2. Flask routes implemented
3. Services implemented
4. Database tables used
5. Database changes
6. Dependencies added
7. Environment variables required
8. Tests executed
9. End-to-end result
10. Features fully implemented
11. Features using deterministic mock data
12. Features still planned
13. Known limitations
14. Exact commands required to run backend
15. Exact API endpoints the frontend should consume

DO NOT claim a feature is live if it is mocked.

DO NOT claim blockchain attribution proves real-world identity.

DO NOT claim AI/ML if the MVP uses rule-based scoring.

The goal is a stable, integrated Flask backend that makes the frontend fully functional.