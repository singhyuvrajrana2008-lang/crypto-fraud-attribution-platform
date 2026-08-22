You are the SENIOR BACKEND + DATABASE + INTEGRATION ENGINEER responsible for FINISHING the existing SIH project.

PROJECT:
SIH 26183 — Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics

GITHUB REPOSITORY:
https://github.com/singhyuvrajrana2008-lang/crypto-fraud-attribution-platform

============================================================
PRIMARY OBJECTIVE
============================================================

DO NOT rebuild the project from scratch.

DO NOT replace the existing Flask backend with another framework.

DO NOT throw away working implementation.

Your job is to INSPECT the current repository, identify the missing functionality, and complete the remaining backend + database work required for the current MVP frontend feature list.

The final website must support this complete investigator workflow:

COMPLAINTS
↓
COMPLAINT INGESTION
↓
AUTOMATED WALLET ANALYSIS
↓
TRANSACTION DATA
↓
FUND-FLOW GRAPH
↓
RISK ANALYSIS
↓
INVESTIGATION PRIORITY
↓
TOP 10 PRIORITY CASES
↓
RELATED CASE DETECTION
↓
VASP / EXCHANGE ASSOCIATION
↓
ALERTS
↓
INVESTIGATOR REVIEW
↓
NOTES / STATUS
↓
REPORT
↓
AUDIT TRAIL

============================================================
CRITICAL RULE: INSPECT BEFORE CHANGING
============================================================

First inspect the actual GitHub repository.

Read:

README.md
docs/API_CONTRACT.md
docs/DATABASE_SCHEMA.md
docs/SETUP.md
docs/ARCHITECTURE.md
docs/INTEGRATION_CHECKLIST.md
.env.example

Then inspect:

backend/
frontend/
database/
backend/requirements.txt

Inspect:

- current Flask app
- current routes
- current services
- current models
- current tests
- current database code
- current schema.sql
- current seed.sql
- current frontend API calls
- current environment handling

Create a gap analysis BEFORE implementing.

Your first internal checklist must be:

IMPLEMENTED
PARTIALLY IMPLEMENTED
MISSING
BROKEN / INCONSISTENT

Do not duplicate functionality that already works.

============================================================
IMPORTANT EXISTING REPOSITORY ISSUE
============================================================

The repository documentation describes PostgreSQL/Supabase as the target database, but the current database/schema implementation may contain SQLite-oriented constructs.

You MUST verify this.

The final implementation must have ONE coherent database strategy.

For the evaluation MVP:

PRIMARY PERSISTENCE:
Supabase PostgreSQL

OPTIONAL LOCAL TEST MODE:
SQLite only if already intentionally supported for tests

Do NOT let production/demo runtime silently switch between incompatible database schemas.

If the current schema conflicts with DATABASE_SCHEMA.md:

1. Resolve the conflict.
2. Update schema.sql/migrations.
3. Update DATABASE_SCHEMA.md.
4. Update backend database code.
5. Update API_CONTRACT.md only if API behavior changes.
6. Test the complete flow.

============================================================
DO NOT CHANGE FLASK
============================================================

Backend framework MUST remain:

Flask

Language:

Python

Database:

PostgreSQL through Supabase

Frontend communication:

REST API + JSON

Do NOT migrate to FastAPI, Django, Node, Express, etc.

============================================================
CURRENT CORE FEATURES TO PRESERVE
============================================================

Preserve and verify existing working functionality for:

- Flask REST API
- health endpoint
- case creation
- wallet analysis
- transaction normalization
- transaction retrieval
- graph data
- risk analysis
- VASP attribution
- report data

Do not rewrite these unnecessarily.

============================================================
MAIN REMAINING MVP FEATURES TO IMPLEMENT
============================================================

Implement and integrate the following missing capabilities.

------------------------------------------------------------
1. CASE / COMPLAINT LISTING
------------------------------------------------------------

Implement:

GET /api/cases

Support:

- pagination
- search
- status filter
- risk filter
- fraud type filter
- blockchain filter
- amount range
- date range
- sorting

Search fields:

- case number
- wallet address
- transaction hash if applicable

Sort options:

- priority
- priority_score
- risk_score
- amount
- created_at

Return frontend-ready data.

Do not make the frontend download all records and calculate filters locally.

------------------------------------------------------------
2. COMPLAINT INGESTION
------------------------------------------------------------

The MVP needs an incoming complaint workflow.

Implement a controlled demo ingestion mechanism.

Example:

POST /api/demo/seed

or an equivalent repository-consistent endpoint.

The demo data should include enough cases to demonstrate:

- different fraud types
- different amounts
- multiple risk levels
- different priority scores
- multiple linked complaints
- repeated wallet activity
- multi-hop transactions
- at least one potential VASP association

The demo dataset must be deterministic.

Do NOT present fabricated demo data as real law-enforcement intelligence.

The frontend must be able to load demo complaints without manual SQL editing.

------------------------------------------------------------
3. INVESTIGATION PRIORITY ENGINE
------------------------------------------------------------

This is a REQUIRED missing feature.

IMPORTANT:

RISK and PRIORITY are different.

Risk:
"How suspicious does the observed activity look?"

Priority:
"Which case should the investigator look at first?"

Create a backend priority engine.

Priority should use documented factors such as:

- financial impact
- number of linked complaints
- repeated wallet activity
- suspicious fund movement
- potential VASP interaction
- other clearly documented signals

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

The frontend must NOT calculate priority.

Backend/database is the source of truth.

Do NOT call this "fraud probability".

Use:

investigation priority

------------------------------------------------------------
4. TOP 10 PRIORITY CASES
------------------------------------------------------------

Implement:

GET /api/cases/top-priority?limit=10

Default limit = 10

Return:

- rank
- case_id
- case_number
- reported amount
- currency
- fraud type
- reported wallet
- blockchain
- priority score
- risk score
- risk level
- related case count
- status
- created_at

The endpoint must calculate/query the actual top cases.

Do NOT hardcode the top 10.

------------------------------------------------------------
5. CROSS-CASE CORRELATION
------------------------------------------------------------

Implement a case-correlation service.

Identify potentially related complaints through observable evidence such as:

- shared wallet
- shared downstream wallet
- shared destination
- common VASP association
- common transaction pattern

Implement:

GET /api/cases/{case_id}/related

Return:

- related_case_id
- relationship_type
- confidence
- evidence
- shared wallet/destination where appropriate

Possible relationship types:

shared_wallet
shared_downstream_wallet
shared_destination
common_vasp
common_transaction_pattern

CRITICAL:

Do not conclude:

"same criminal"

based only on shared blockchain relationships.

Use:

potentially related cases

------------------------------------------------------------
6. UPDATE RISK ENGINE
------------------------------------------------------------

Preserve the existing risk engine if it already works.

Add missing indicators required by the new workflow where appropriate:

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

Each indicator should have:

code
description
severity
weight/evidence where appropriate

Risk levels:

low
medium
high
critical

Do not claim that risk equals criminality.

------------------------------------------------------------
7. DASHBOARD SUMMARY API
------------------------------------------------------------

The frontend needs summary cards.

Implement an efficient dashboard endpoint such as:

GET /api/dashboard/summary

Return:

- total_cases
- new_cases
- analyzing_cases
- high_priority_cases
- medium_priority_cases
- low_priority_cases
- high_risk_cases
- total_amount_involved
- potential_vasp_associations
- related_case_count
- recent_alert_count

Also provide:

GET /api/dashboard/recent-alerts

if appropriate.

Do not force the frontend to make many unnecessary API calls for simple dashboard statistics.

------------------------------------------------------------
8. ALERTS
------------------------------------------------------------

Implement alert generation and storage.

Alert types:

HIGH_RISK_CASE
MULTIPLE_RELATED_CASES
RAPID_FUND_MOVEMENT
VASP_MATCH
HIGH_FINANCIAL_IMPACT

Implement:

GET /api/alerts

PATCH /api/alerts/{alert_id}/read

Fields:

id
case_id
type
title
message
severity
read
created_at

Alerts should be generated based on actual analysis results.

------------------------------------------------------------
9. CASE STATUS MANAGEMENT
------------------------------------------------------------

Support:

new
analyzing
under_review
escalated
closed

Implement:

PATCH /api/cases/{case_id}/status

Record:

- old status
- new status
- user if available
- timestamp

Also write an audit event.

------------------------------------------------------------
10. INVESTIGATOR NOTES
------------------------------------------------------------

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

------------------------------------------------------------
11. AUDIT TRAIL
------------------------------------------------------------

Implement audit logging for:

CASE_CREATED
CASE_VIEWED
ANALYSIS_STARTED
ANALYSIS_COMPLETED
ANALYSIS_FAILED
STATUS_CHANGED
NOTE_ADDED
REPORT_GENERATED
VASP_ASSOCIATION_FOUND

Implement:

GET /api/cases/{case_id}/audit

Fields:

id
user_id
case_id
action
details
created_at

------------------------------------------------------------
12. REPORT API
------------------------------------------------------------

Preserve existing report endpoint.

Ensure:

GET /api/cases/{case_id}/report

returns live data from the database.

Report should include:

- case summary
- wallet
- transactions
- timeline
- graph
- risk
- priority
- related cases
- VASP associations
- evidence
- timestamps

If PDF generation is already implemented, verify it.

If not implemented:

Implement PDF only AFTER the rest of the workflow is stable.

Do not let PDF generation block the main MVP.

------------------------------------------------------------
13. SEARCH / FILTERING
------------------------------------------------------------

Ensure the frontend can filter by:

- priority
- risk
- fraud type
- blockchain
- date
- amount
- VASP association
- status

Use backend/database filtering.

Support server-side pagination.

------------------------------------------------------------
14. AUTHENTICATION
------------------------------------------------------------

Inspect whether authentication already exists.

If existing auth is functional:

Preserve and integrate it.

If missing and required by the frontend:

Implement a minimal secure investigator auth layer consistent with the existing project architecture.

Roles:

investigator
admin

Do not overbuild auth for the hackathon.

Never expose passwords or Supabase service-role credentials.

------------------------------------------------------------
15. SUPABASE / POSTGRES INTEGRATION
------------------------------------------------------------

The backend must use the configured Supabase PostgreSQL database for demo/production runtime.

Verify actual connection.

The database schema must support:

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

If current schema is incomplete:

Update it.

If a new table is needed:

Add it.

Update:

database/schema.sql
database/seed.sql
docs/DATABASE_SCHEMA.md

Do not leave the repository documentation describing a different schema from the actual database.

------------------------------------------------------------
16. DATABASE CONSISTENCY
------------------------------------------------------------

Use:

UUID for application IDs

TEXT for wallet addresses

TEXT for transaction hashes

TIMESTAMPTZ for timestamps in PostgreSQL

Exact cryptocurrency amount representation

NUMERIC for confidence

INTEGER for risk score

Foreign keys must match the referenced ID type.

Do NOT create a second incompatible schema.

------------------------------------------------------------
17. BLOCKCHAIN PROVIDER
------------------------------------------------------------

Preserve existing provider abstraction if present.

The MVP must be runnable with deterministic demo data even if a live blockchain API is unavailable.

Use:

Mock provider
Live provider

with the same normalized transaction schema.

For MVP:

ethereum

The frontend must not know whether the data is mock or live.

Do not claim a mock result is live blockchain intelligence.

------------------------------------------------------------
18. FRONTEND CONTRACT COMPATIBILITY
------------------------------------------------------------

The frontend must be able to implement these screens/features entirely through the Flask API:

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
CASE STATUS
AUDIT TRAIL

Do NOT require the frontend to:

- query Supabase
- call blockchain APIs
- calculate risk
- calculate priority
- build graph relationships
- detect related cases

The backend returns the data.

The frontend displays it.

============================================================
API CONTRACT UPDATE
============================================================

The current API_CONTRACT.md does not yet describe all of the newer MVP features.

After implementing the missing endpoints, UPDATE:

docs/API_CONTRACT.md

Document every implemented endpoint with:

- method
- path
- purpose
- request
- query parameters
- response
- error response
- datatypes
- enums

Do not leave undocumented endpoints in the final project.

============================================================
DATABASE CONTRACT UPDATE
============================================================

Update:

docs/DATABASE_SCHEMA.md

so it exactly matches:

database/schema.sql
actual Supabase tables
backend queries

No documentation/schema mismatch is allowed.

============================================================
SETUP UPDATE
============================================================

Update:

docs/SETUP.md

so a clean clone can:

1. create .env
2. install backend
3. install frontend
4. provision/apply schema
5. seed demo data
6. start Flask
7. start frontend
8. open the dashboard
9. load complaints
10. perform analysis

No manual source-code edits should be necessary.

============================================================
TESTING
============================================================

Run the existing tests first.

Then add/fix tests for:

- health
- database connection
- case creation
- case listing
- search/filter
- demo seed
- wallet validation
- analysis
- transactions
- graph
- risk
- priority
- top 10
- related cases
- VASP attribution
- dashboard summary
- alerts
- status updates
- notes
- report
- audit

============================================================
CRITICAL END-TO-END TEST
============================================================

Perform this from a clean state:

1. Start Flask.
2. Verify database connection.
3. Seed demo complaints.
4. Request dashboard summary.
5. Request cases.
6. Request top 10.
7. Open Priority #1.
8. Analyze its wallet.
9. Retrieve transactions.
10. Retrieve graph.
11. Retrieve risk.
12. Retrieve priority.
13. Retrieve related cases.
14. Retrieve VASP attribution.
15. Retrieve alerts.
16. Add a note.
17. Change status.
18. Generate/read report.
19. Retrieve audit trail.
20. Confirm frontend-ready response structures.

There must be NO manual SQL editing during this flow.

============================================================
INTEGRATION AUDIT
============================================================

For every important field verify:

DATABASE
↓
BACKEND
↓
API
↓
FRONTEND

Especially:

case_id
case_number
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

No mismatched names such as:

priority
vs
priority_score

caseId
vs
case_id

createdDate
vs
created_at

unless explicitly defined by the contract.

============================================================
SECURITY
============================================================

Use environment variables.

Never commit:

.env
database passwords
Supabase service-role keys
blockchain API secrets
access tokens

Never return secret values through APIs.

Never expose stack traces.

============================================================
NO OVERCLAIMING
============================================================

The system must NOT claim:

- guaranteed criminal identification
- guaranteed exchange ownership
- automatic legal proof
- automatic asset freezing
- guaranteed recovery
- complete mixer deanonymization
- complete cross-chain attribution
- production-grade ML if none exists

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

Do not report "complete" merely because Flask starts.

The work is complete only when:

[ ] Existing Flask functionality still works
[ ] Supabase/PostgreSQL connection works
[ ] Database schema matches documentation
[ ] API contract matches implementation
[ ] Complaint ingestion works
[ ] Case listing works
[ ] Search/filter works
[ ] Dashboard summary works
[ ] Priority engine works
[ ] Top 10 works
[ ] Wallet tracking works
[ ] Transaction timeline works
[ ] Graph works
[ ] Risk works
[ ] Related-case detection works
[ ] VASP attribution works
[ ] Alerts work
[ ] Notes work
[ ] Status management works
[ ] Report endpoint works
[ ] Audit trail works
[ ] Demo seed works
[ ] Frontend can use all implemented endpoints
[ ] No frontend direct database access is required
[ ] No manual SQL changes are required for the demo
[ ] Tests pass
[ ] Clean setup works

============================================================
FINAL DELIVERABLE
============================================================

Before finishing:

1. Implement missing functionality.
2. Fix broken/inconsistent functionality.
3. Update API_CONTRACT.md.
4. Update DATABASE_SCHEMA.md.
5. Update SETUP.md.
6. Update schema.sql/seed.sql.
7. Update requirements if necessary.
8. Run backend tests.
9. Run the complete end-to-end workflow.
10. Verify frontend integration.
11. Commit all changes to a dedicated branch.
12. Open a pull request into main.

FINAL REPORT MUST CONTAIN:

- existing functionality preserved
- missing features implemented
- files changed
- API endpoints added/changed
- database changes
- Supabase connection status
- tests run
- end-to-end result
- mocked vs live functionality
- known limitations
- exact commands to run
- any remaining blockers

DO NOT claim success unless you actually test the end-to-end flow.