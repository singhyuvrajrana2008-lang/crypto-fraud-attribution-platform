You are the SENIOR BACKEND + DATABASE + INTEGRATION ENGINEER responsible for COMPLETING the existing SIH 26183 project.

PROJECT:
SIH 26183 — Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics

REPOSITORY:
https://github.com/singhyuvrajrana2008-lang/crypto-fraud-attribution-platform

============================================================
MISSION
============================================================

DO NOT rebuild the project from scratch.

DO NOT replace Flask.

DO NOT replace the current frontend architecture.

DO NOT throw away working backend functionality.

Your task is to inspect the CURRENT repository, preserve what already works, fix inconsistencies, and IMPLEMENT ALL REMAINING BACKEND + DATABASE FEATURES required for the complete MVP.

The final system must support:

COMPLAINTS
↓
COMPLAINT INGESTION
↓
WALLET ANALYSIS
↓
TRANSACTION RETRIEVAL
↓
MULTI-HOP FUND FLOW
↓
GRAPH
↓
RISK ANALYSIS
↓
INVESTIGATION PRIORITY
↓
TOP 10 PRIORITY CASES
↓
RELATED CASES
↓
POTENTIAL VASP ASSOCIATION
↓
ALERTS
↓
INVESTIGATOR REVIEW
↓
NOTES
↓
STATUS
↓
REPORT
↓
AUDIT TRAIL
↓
FRONTEND DASHBOARD

============================================================
CURRENT REPOSITORY STATUS
============================================================

The current repository already contains a Flask backend with working/partial functionality for:

- Flask REST API
- health endpoint
- create case
- get case
- wallet analysis
- Ethereum wallet validation
- deterministic demo transaction generation
- transaction retrieval
- graph generation
- risk analysis
- VASP attribution
- report data
- PostgreSQL connection wrapper

PRESERVE THESE FEATURES.

Do not rewrite them unless necessary to fix a bug or integration problem.

============================================================
FIRST TASK: REPOSITORY AUDIT
============================================================

Before editing code, inspect the actual repository.

Read:

README.md
docs/API_CONTRACT.md
docs/DATABASE_SCHEMA.md
docs/ARCHITECTURE.md
docs/SETUP.md
docs/INTEGRATION_CHECKLIST.md
.env.example

Inspect:

backend/
frontend/
database/

Inspect:

backend/app.py
backend/storage.py
backend/requirements.txt
database/schema.sql
database/seed.sql if present
frontend/package.json
all existing frontend API calls
existing tests

Create an internal gap analysis:

IMPLEMENTED
PARTIALLY IMPLEMENTED
MISSING
BROKEN
INCONSISTENT

Then implement only what is required.

============================================================
CRITICAL DATABASE ISSUE
============================================================

The project documentation says PostgreSQL/Supabase is the production/demo database.

The repository may contain SQLite-oriented schema/runtime behavior.

FIX THIS INCONSISTENCY.

FINAL RULE:

Production/demo runtime:
Supabase PostgreSQL

Optional local test mode:
SQLite only if intentionally retained for tests

Do not silently use SQLite when the application is supposed to use Supabase.

The final PostgreSQL schema must be compatible with the actual Flask queries.

Use:

UUID
TEXT for wallet addresses
TEXT for transaction hashes
TIMESTAMPTZ for timestamps
NUMERIC where appropriate
INTEGER for scores

Do NOT use:

SQLite PRAGMA statements in PostgreSQL schema
TEXT timestamps in PostgreSQL schema
FLOAT cryptocurrency amounts
INTEGER UUIDs

Make:

database/schema.sql

a real PostgreSQL/Supabase schema.

If necessary, update:

database/schema.sql
database/seed.sql
docs/DATABASE_SCHEMA.md
docs/SETUP.md
backend database code

============================================================
FLASK REQUIREMENT
============================================================

Backend framework MUST remain:

Flask

Python

REST API

JSON

Supabase/PostgreSQL

Do NOT migrate to FastAPI, Django, Node, Express, etc.

============================================================
P0 — FEATURES THAT MUST BE IMPLEMENTED
============================================================

------------------------------------------------------------
1. CASE LISTING
------------------------------------------------------------

Implement:

GET /api/cases

Support:

search
status
risk_level
fraud_type
blockchain
min_amount
max_amount
date_from
date_to
priority

Sorting:

priority
priority_score
risk_score
amount
created_at

Pagination:

page
limit

The frontend must be able to populate the complaint/case table directly.

------------------------------------------------------------
2. COMPLAINT INGESTION
------------------------------------------------------------

Add a deterministic demo complaint ingestion mechanism.

Implement:

POST /api/demo/seed

The seed must create enough realistic DEMO cases for the dashboard.

Target approximately:

50–100 demo cases

The data must include:

- different fraud types
- different amounts
- different risk levels
- different priority scores
- multiple related complaints
- repeated wallet activity
- multi-hop transaction flows
- at least one potential VASP association
- high/medium/low priority cases

The seed must be deterministic.

Avoid random data that changes every run.

Do not represent demo data as actual cybercrime intelligence.

Make seeding idempotent or safely repeatable.

------------------------------------------------------------
3. DASHBOARD SUMMARY
------------------------------------------------------------

Implement:

GET /api/dashboard/summary

Return:

total_cases
new_cases
analyzing_cases
high_priority_cases
medium_priority_cases
low_priority_cases
high_risk_cases
total_amount_involved
potential_vasp_associations
related_case_count
recent_alert_count

The dashboard should not need 10 separate API calls for basic statistics.

------------------------------------------------------------
4. PRIORITY ENGINE
------------------------------------------------------------

THIS IS A REQUIRED CORE FEATURE.

Risk and priority are different.

RISK:
How suspicious is the observed wallet activity?

PRIORITY:
Which case should the investigator investigate first?

Build a transparent rule-based priority engine.

Priority factors should include documented signals such as:

- financial impact
- number of linked complaints
- repeated wallet activity
- suspicious fund movement
- potential VASP association
- other observable investigation signals

Calculate:

priority_score
priority_rank
priority_factors

Example:

{
  "priority_score": 91,
  "priority_rank": 1,
  "priority_factors": {
    "financial_impact": 75,
    "linked_cases": 95,
    "repeated_activity": 90,
    "fund_movement": 85,
    "vasp_interaction": 80
  }
}

Do NOT call the score "fraud probability".

Do NOT allow the frontend to calculate it.

Backend/database is the source of truth.

Persist the priority result.

------------------------------------------------------------
5. TOP 10 PRIORITY CASES
------------------------------------------------------------

Implement:

GET /api/cases/top-priority?limit=10

Default:

10

Return:

rank
case_id
case_reference
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

The Top 10 must come from actual backend/database calculations.

Do not hardcode values.

------------------------------------------------------------
6. CASE DETAIL
------------------------------------------------------------

Expand case retrieval where needed so the frontend can display:

case reference
fraud type
amount
currency
wallet
blockchain
status
priority
risk
analysis status
transaction count
hop count
related case count
potential VASP
created_at
updated_at

Use:

GET /api/cases/{case_id}

------------------------------------------------------------
7. CROSS-CASE CORRELATION
------------------------------------------------------------

Implement:

GET /api/cases/{case_id}/related

Detect potentially related cases through:

shared_wallet
shared_downstream_wallet
shared_destination
common_vasp
common_transaction_pattern

Return:

related_case_id
relationship_type
confidence
evidence
shared_wallet
shared_destination where applicable

CRITICAL:

Never claim:

"same scammer"

or:

"same criminal"

based solely on wallet relationships.

Use:

potentially related cases

Persist relationships.

------------------------------------------------------------
8. RISK ENGINE
------------------------------------------------------------

Preserve existing risk engine but expand it where necessary.

Indicators:

MULTI_HOP
RAPID_MOVEMENT
FUND_SPLITTING
FUND_CONSOLIDATION
REPEATED_ACTIVITY
VASP_INTERACTION
MULTIPLE_RELATED_CASES
HIGH_FINANCIAL_IMPACT

Return:

score
level
indicators

Each indicator should provide:

code
description
severity
evidence

Risk levels:

low
medium
high
critical

Risk is an investigative signal, not proof of criminality.

------------------------------------------------------------
9. ALERTS
------------------------------------------------------------

Implement:

GET /api/alerts

PATCH /api/alerts/{alert_id}/read

Generate alerts for:

HIGH_RISK_CASE
MULTIPLE_RELATED_CASES
RAPID_FUND_MOVEMENT
VASP_MATCH
HIGH_FINANCIAL_IMPACT

Store:

id
case_id
type
title
message
severity
read
created_at

------------------------------------------------------------
10. CASE STATUS
------------------------------------------------------------

Implement:

PATCH /api/cases/{case_id}/status

Canonical statuses:

new
analyzing
under_review
escalated
closed

Record:

old status
new status
changed_at
changed_by if available

Create an audit event.

------------------------------------------------------------
11. INVESTIGATOR NOTES
------------------------------------------------------------

Implement:

GET /api/cases/{case_id}/notes
POST /api/cases/{case_id}/notes
PATCH /api/notes/{note_id}
DELETE /api/notes/{note_id}

Persist:

case_id
user_id
note
created_at
updated_at

------------------------------------------------------------
12. AUDIT TRAIL
------------------------------------------------------------

Implement:

GET /api/cases/{case_id}/audit

Log:

CASE_CREATED
CASE_VIEWED
ANALYSIS_STARTED
ANALYSIS_COMPLETED
ANALYSIS_FAILED
STATUS_CHANGED
NOTE_ADDED
REPORT_GENERATED
VASP_ASSOCIATION_FOUND

Persist:

id
user_id
case_id
action
details
created_at

------------------------------------------------------------
13. REPORT
------------------------------------------------------------

Preserve:

GET /api/cases/{case_id}/report

It must return live data including:

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
timestamps

If PDF generation is easy and stable, implement:

POST /api/cases/{case_id}/report/pdf

Otherwise leave PDF as P1 and do not let it block the MVP.

------------------------------------------------------------
14. SEARCH / FILTERING
------------------------------------------------------------

Make the case listing usable by frontend.

Support:

Search:
case reference
wallet address
transaction hash where applicable

Filters:
priority
risk
fraud type
blockchain
date
amount
status
VASP association

Sorting:
priority
risk
amount
date

Use database-side filtering.

------------------------------------------------------------
15. AUTHENTICATION
------------------------------------------------------------

Inspect existing authentication.

If it exists:
preserve and integrate it.

If it doesn't:
implement the minimum necessary investigator authentication structure.

Roles:

investigator
admin

Do not overbuild authentication for the mid-evaluation.

Never expose passwords or Supabase service-role keys.

============================================================
BLOCKCHAIN ANALYSIS
============================================================

PRESERVE existing wallet-analysis functionality.

The MVP currently uses Ethereum.

Keep:

chain = ethereum

The backend should support a provider abstraction:

Mock Provider
Live Provider

Both must produce the same normalized transaction structure.

The MVP must work without a live blockchain API by using deterministic demo transactions.

The frontend must not know whether the provider is mock or live.

============================================================
MULTI-HOP FUND FLOW
============================================================

Starting from the reported wallet:

1. retrieve transactions
2. normalize them
3. identify destination wallets
4. follow relevant destinations
5. assign hop numbers
6. track visited wallets
7. prevent cycles
8. prevent duplicates
9. enforce maximum hop depth
10. create graph

Use a bounded MVP depth such as 3–5 hops.

Do not create unlimited traversal.

============================================================
GRAPH
============================================================

Preserve existing graph endpoint:

GET /api/cases/{case_id}/graph

Graph must contain:

nodes
edges

Node:

id
address
type
label

Edge:

id
source
target
transaction_hash
amount
asset
timestamp
hop

The frontend should render the graph directly.

Do not require the frontend to reconstruct the graph.

============================================================
TRANSACTIONS
============================================================

Preserve:

GET /api/cases/{case_id}/transactions

Support:

page
limit

Return frontend-ready normalized transactions:

id
transaction_hash
chain
from_address
to_address
asset
amount
block_number
timestamp
status
hop

Never return provider-specific raw transaction structures.

============================================================
VASP ATTRIBUTION
============================================================

Preserve existing attribution behavior but make it database-backed and explainable.

Return:

id
wallet_address
entity_name
entity_type
match_type
confidence
evidence
created_at

Use:

Potential VASP Association

Never automatically claim:

confirmed owner

unless authoritative evidence actually exists.

Demo VASP matches must be clearly demo/test data.

============================================================
DATABASE SCHEMA
============================================================

Final schema should support:

users
cases
wallets
case_wallets
transactions
case_transactions
entities
wallet_entity_labels
attributions
analysis_results
risk_assessments
risk_indicators
case_relationships
alerts
investigation_notes
investigation_reports
audit_logs

Every table must have appropriate:

UUID primary keys
foreign keys
NOT NULL constraints
unique constraints
indexes
timestamps

Do not duplicate tables.

Do not create incompatible alternative field names.

============================================================
CRITICAL FIELD CONSISTENCY
============================================================

Use the same canonical fields across:

DATABASE
→ BACKEND
→ API
→ FRONTEND

Examples:

case_id
case_reference
wallet_id
wallet_address
transaction_id
transaction_hash
priority_score
priority_rank
risk_score
risk_level
related_case_count
confidence
created_at
updated_at

Do not produce:

caseId
priority
score
createdDate

unless the existing API contract explicitly defines those names.

============================================================
API RESPONSE FORMAT
============================================================

All APIs must return:

SUCCESS:

{
  "success": true,
  "data": {},
  "error": null
}

ERROR:

{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}

============================================================
API CONTRACT UPDATE
============================================================

The current API contract does not yet describe all the new MVP features.

After implementation, UPDATE:

docs/API_CONTRACT.md

Document every implemented endpoint:

METHOD
PATH
PURPOSE
REQUEST
QUERY PARAMETERS
RESPONSE
ERRORS
DATATYPES
ENUMS
EXAMPLES

At minimum, document:

GET /api/dashboard/summary
GET /api/cases
GET /api/cases/top-priority
GET /api/cases/{case_id}/related
GET /api/alerts
PATCH /api/alerts/{alert_id}/read
PATCH /api/cases/{case_id}/status
GET /api/cases/{case_id}/notes
POST /api/cases/{case_id}/notes
PATCH /api/notes/{note_id}
DELETE /api/notes/{note_id}
GET /api/cases/{case_id}/audit
POST /api/demo/seed

Only document endpoints that actually exist.

============================================================
DATABASE DOCUMENTATION UPDATE
============================================================

Update:

docs/DATABASE_SCHEMA.md

so it exactly matches the actual PostgreSQL schema.

Update:

database/schema.sql
database/seed.sql

as required.

No documentation/schema mismatch is allowed.

============================================================
SETUP
============================================================

Update:

docs/SETUP.md

A clean clone should support:

1. clone repo
2. create .env
3. install backend
4. install frontend
5. configure Supabase
6. apply PostgreSQL schema
7. seed demo data
8. start Flask
9. start frontend
10. load dashboard
11. load demo complaints
12. analyze case
13. see Top 10

No manual source-code editing.

No manual SQL editing during normal demo flow.

============================================================
SECURITY
============================================================

Use environment variables.

Never commit:

.env
database passwords
Supabase service-role key
blockchain API keys
tokens

Never expose secrets in:

frontend
logs
API responses
README

Never expose stack traces.

============================================================
TESTING
============================================================

Preserve all existing tests.

Add tests for:

health
database connection
case creation
case listing
search/filter
demo seed
wallet analysis
transactions
graph
risk
priority
top 10
related cases
VASP attribution
dashboard summary
alerts
status
notes
report
audit

============================================================
MANDATORY END-TO-END TEST
============================================================

Test from a clean state:

1. Start Flask.
2. Connect to Supabase PostgreSQL.
3. Seed demo complaints.
4. Fetch dashboard summary.
5. Fetch case list.
6. Fetch Top 10.
7. Open #1.
8. Analyze wallet.
9. Fetch transactions.
10. Fetch graph.
11. Fetch risk.
12. Fetch priority.
13. Fetch related cases.
14. Fetch VASP association.
15. Fetch alerts.
16. Add note.
17. Change case status.
18. Generate/read report.
19. Read audit trail.

The entire flow must work WITHOUT manually editing the database.

============================================================
FRONTEND COMPATIBILITY
============================================================

The frontend must be able to implement:

LOGIN
DASHBOARD
COMPLAINT INGESTION
COMPLAINT LIST
TOP 10 PRIORITY
CASE INVESTIGATION
TRANSACTION TIMELINE
FUND-FLOW GRAPH
RISK ANALYSIS
RELATED CASES
VASP ATTRIBUTION
ALERTS
NOTES
REPORT
STATUS MANAGEMENT
AUDIT TRAIL

The frontend must NOT:

- query Supabase directly
- call blockchain providers directly
- calculate risk
- calculate priority
- detect related cases
- reconstruct the transaction graph

Backend returns the data.

Frontend displays it.

============================================================
NO OVERCLAIMING
============================================================

Do not claim:

- criminal identity automatically identified
- guaranteed exchange ownership
- guaranteed fund recovery
- automatic asset freezing
- complete mixer tracing
- complete cross-chain attribution
- trained ML model unless actually implemented

Use:

potential VASP association
investigation priority
risk indicator
observable fund flow
confidence
evidence

============================================================
DEFINITION OF DONE
============================================================

Do not say "complete" because Flask starts.

The project is complete for the MVP only when:

[ ] Flask backend runs
[ ] Supabase PostgreSQL connection works
[ ] PostgreSQL schema is valid
[ ] Database documentation matches schema
[ ] API contract matches implementation
[ ] Demo seed works
[ ] Case ingestion works
[ ] Case listing works
[ ] Search/filter works
[ ] Dashboard summary works
[ ] Priority engine works
[ ] Top 10 works
[ ] Wallet analysis works
[ ] Transaction timeline works
[ ] Graph works
[ ] Risk works
[ ] Related cases works
[ ] VASP association works
[ ] Alerts work
[ ] Status management works
[ ] Notes work
[ ] Report works
[ ] Audit trail works
[ ] Frontend can consume all required APIs
[ ] No manual DB edits are required
[ ] Existing tests pass
[ ] New tests pass
[ ] Clean-clone setup works

============================================================
FINAL GITHUB WORKFLOW
============================================================

Do NOT push directly to main.

Create a dedicated branch:

feature/complete-mvp-backend

Implement the changes there.

Commit logically.

Run tests.

Then open a Pull Request into:

main

The PR description must contain:

- what was already working
- what you added
- database changes
- API changes
- tests
- end-to-end result
- mocked vs live blockchain features
- known limitations

============================================================
FINAL REPORT
============================================================

At the end, report:

1. Gap analysis before implementation
2. Files modified
3. Files created
4. Flask endpoints implemented
5. Database tables created/updated
6. Supabase connection status
7. Demo seed status
8. Priority engine status
9. Top 10 status
10. Cross-case correlation status
11. Risk status
12. VASP status
13. Test results
14. End-to-end test result
15. Exact setup commands
16. Remaining blockers, if any

DO NOT claim completion unless the end-to-end workflow has actually been tested.