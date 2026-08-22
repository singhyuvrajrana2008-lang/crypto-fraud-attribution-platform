PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cases (
  id TEXT PRIMARY KEY,
  case_reference TEXT NOT NULL UNIQUE,
  fraud_type TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wallets (
  id TEXT PRIMARY KEY,
  address TEXT NOT NULL,
  chain TEXT NOT NULL CHECK (chain = 'ethereum'),
  wallet_type TEXT NOT NULL CHECK (wallet_type IN ('reported_wallet','intermediary','exchange','vasp','unknown')),
  first_seen_at TEXT,
  last_seen_at TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(address, chain)
);

CREATE TABLE IF NOT EXISTS transactions (
  id TEXT PRIMARY KEY,
  transaction_hash TEXT NOT NULL,
  chain TEXT NOT NULL CHECK (chain = 'ethereum'),
  from_wallet_id TEXT NOT NULL REFERENCES wallets(id),
  to_wallet_id TEXT NOT NULL REFERENCES wallets(id),
  asset TEXT NOT NULL,
  amount TEXT NOT NULL,
  block_number INTEGER,
  timestamp TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending','confirmed','failed','unknown')),
  hop INTEGER,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  UNIQUE(transaction_hash, chain)
);

CREATE TABLE IF NOT EXISTS entities (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('vasp','exchange','bridge','defi_protocol','unknown')),
  verification_status TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wallet_entity_labels (
  id TEXT PRIMARY KEY,
  wallet_id TEXT NOT NULL REFERENCES wallets(id),
  entity_id TEXT NOT NULL REFERENCES entities(id),
  source TEXT NOT NULL,
  confidence REAL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attributions (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES cases(id),
  wallet_id TEXT NOT NULL REFERENCES wallets(id),
  entity_id TEXT REFERENCES entities(id),
  match_type TEXT NOT NULL CHECK (match_type IN ('known_address','entity_label','behavioral_match','cluster_match','unknown')),
  confidence REAL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
  evidence TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS risk_assessments (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES cases(id),
  score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
  level TEXT NOT NULL CHECK (level IN ('low','medium','high','critical')),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS risk_indicators (
  id TEXT PRIMARY KEY,
  risk_assessment_id TEXT NOT NULL REFERENCES risk_assessments(id),
  code TEXT NOT NULL,
  description TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('low','medium','high','critical')),
  evidence TEXT
);

CREATE INDEX IF NOT EXISTS idx_wallets_address_chain ON wallets(address, chain);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_from ON transactions(from_wallet_id);
CREATE INDEX IF NOT EXISTS idx_transactions_to ON transactions(to_wallet_id);
CREATE INDEX IF NOT EXISTS idx_attributions_case ON attributions(case_id);
CREATE INDEX IF NOT EXISTS idx_risk_case ON risk_assessments(case_id);
