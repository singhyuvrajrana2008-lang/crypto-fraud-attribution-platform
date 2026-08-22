from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from flask import Flask, g, jsonify, request
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = BASE_DIR / "database" / "local.sqlite3"
ETH_ADDRESS = re.compile(r"^0x[a-fA-F0-9]{40}$")
UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")
CHAIN = "ethereum"
RISK_LEVELS = ("low", "medium", "high", "critical")
TX_STATUSES = ("pending", "confirmed", "failed", "unknown")
WALLET_TYPES = ("reported_wallet", "intermediary", "exchange", "vasp", "unknown")
ENTITY_TYPES = ("vasp", "exchange", "bridge", "defi_protocol", "unknown")
MATCH_TYPES = ("known_address", "entity_label", "behavioral_match", "cluster_match", "unknown")
SEVERITIES = ("low", "medium", "high", "critical")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def envelope(data: Any = None, error: dict[str, str] | None = None, success: bool = True):
    return jsonify({"success": success, "data": data if success else None, "error": error if not success else None})


def fail(code: str, message: str, status: int):
    return envelope(error={"code": code, "message": message}, success=False), status


def db_path() -> str:
    configured = os.getenv("DATABASE_URL", "")
    if configured.startswith("sqlite:///"):
        return configured.removeprefix("sqlite:///")
    if configured and not configured.startswith(("postgresql://", "postgres://")):
        return configured
    return os.getenv("SQLITE_PATH", str(DEFAULT_DB))


def get_db():
    if "db" not in g:
        path = db_path()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def init_db(database=None):
    database = database or get_db()
    schema = (BASE_DIR / "database" / "schema.sql").read_text()
    database.executescript(schema)
    database.commit()


def row_dict(row):
    return dict(row) if row is not None else None


def json_row(row):
    result = row_dict(row)
    if result:
        for key in ("confidence",):
            if result.get(key) is not None:
                result[key] = float(result[key])
        if "evidence" in result and isinstance(result["evidence"], str):
            try:
                result["evidence"] = json.loads(result["evidence"])
            except json.JSONDecodeError:
                pass
    return result


def require_json():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return None, fail("VALIDATION_ERROR", "Request body must be a JSON object", 400)
    return body, None


def validate_uuid(value: Any) -> bool:
    return isinstance(value, str) and bool(UUID_RE.fullmatch(value))


def validate_address(value: Any) -> bool:
    return isinstance(value, str) and bool(ETH_ADDRESS.fullmatch(value))


def get_case(case_id: str):
    if not validate_uuid(case_id):
        return None
    return get_db().execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()


def create_app(test_config: dict[str, Any] | None = None):
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=os.getenv("SECRET_KEY", "development-only"))
    if test_config:
        app.config.update(test_config)
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    CORS(app, origins=[item.strip() for item in origins.split(",") if item.strip()])

    @app.before_request
    def open_database():
        if app.config.get("TESTING") and app.config.get("DATABASE") is not None:
            g.db = app.config["DATABASE"]
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        else:
            get_db()

    @app.teardown_appcontext
    def close_database(_error=None):
        db = g.pop("db", None)
        if db is not None and not (app.config.get("TESTING") and app.config.get("DATABASE") is not None):
            db.close()

    @app.get("/api/health")
    def health():
        return envelope({"status": "ok"})

    @app.post("/api/cases")
    def create_case():
        body, error = require_json()
        if error:
            return error
        for field in ("case_reference", "fraud_type"):
            if not isinstance(body.get(field), str) or not body[field].strip():
                return fail("MISSING_FIELD", f"{field} is required", 400)
        case_id, timestamp = str(uuid.uuid4()), now_iso()
        try:
            get_db().execute(
                "INSERT INTO cases (id, case_reference, fraud_type, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (case_id, body["case_reference"].strip(), body["fraud_type"].strip(), body.get("description"), "open", timestamp, timestamp),
            )
            get_db().commit()
        except sqlite3.IntegrityError:
            return fail("CONFLICT", "case_reference already exists", 409)
        return envelope(json_row(get_case(case_id))), 201

    @app.get("/api/cases/<case_id>")
    def case_detail(case_id):
        case = get_case(case_id)
        return envelope(json_row(case)) if case else fail("CASE_NOT_FOUND", "Case not found", 404)

    @app.post("/api/investigations/analyze")
    def analyze():
        body, error = require_json()
        if error:
            return error
        case_id, address, chain = body.get("case_id"), body.get("wallet_address"), body.get("chain")
        if not validate_uuid(case_id) or not get_case(case_id):
            return fail("CASE_NOT_FOUND", "case_id does not identify an existing case", 404)
        if not validate_address(address):
            return fail("INVALID_WALLET_ADDRESS", "wallet_address must be a valid Ethereum address", 400)
        if chain != CHAIN:
            return fail("UNSUPPORTED_CHAIN", "Only the ethereum chain is supported in the MVP", 400)
        db = get_db()
        wallet = db.execute("SELECT * FROM wallets WHERE address = ? AND chain = ?", (address, chain)).fetchone()
        timestamp = now_iso()
        if wallet is None:
            wallet_id = str(uuid.uuid4())
            db.execute("INSERT INTO wallets (id,address,chain,wallet_type,created_at) VALUES (?,?,?,?,?)", (wallet_id, address, chain, "reported_wallet", timestamp))
            wallet = db.execute("SELECT * FROM wallets WHERE id = ?", (wallet_id,)).fetchone()
        else:
            wallet_id = wallet["id"]
        tx = _demo_transactions(db, wallet_id, address, chain, timestamp)
        risk = _upsert_risk(db, case_id, len(tx))
        attribution = _upsert_attribution(db, case_id, wallet_id)
        db.execute("UPDATE cases SET status = ?, updated_at = ? WHERE id = ?", ("analyzed", timestamp, case_id))
        db.commit()
        return envelope({"case_id": case_id, "wallet": {"id": wallet_id, "address": address, "chain": chain, "type": "reported_wallet"}, "analysis": {"status": "completed", "transaction_count": len(tx), "hop_count": max([item["hop"] or 0 for item in tx], default=0), "total_transferred_value": "12.450000000000000000"}, "risk": {"score": risk["score"], "level": risk["level"]}, "attribution": {"entity_name": attribution["entity_name"], "entity_type": attribution["entity_type"], "confidence": attribution["confidence"]}})

    @app.get("/api/cases/<case_id>/transactions")
    def transactions(case_id):
        if not get_case(case_id):
            return fail("CASE_NOT_FOUND", "Case not found", 404)
        try:
            page, limit = max(1, int(request.args.get("page", 1))), min(100, max(1, int(request.args.get("limit", 50))))
        except ValueError:
            return fail("VALIDATION_ERROR", "page and limit must be integers", 400)
        db = get_db(); offset = (page - 1) * limit
        rows = db.execute("WITH RECURSIVE connected(wallet_id, depth) AS (SELECT wallet_id, 0 FROM attributions WHERE case_id=? UNION SELECT t.to_wallet_id, connected.depth + 1 FROM transactions t JOIN connected ON t.from_wallet_id=connected.wallet_id WHERE connected.depth < 5) SELECT DISTINCT t.*, fw.address AS from_address, tw.address AS to_address FROM transactions t JOIN wallets fw ON fw.id=t.from_wallet_id JOIN wallets tw ON tw.id=t.to_wallet_id JOIN connected c ON c.wallet_id=t.from_wallet_id ORDER BY t.timestamp LIMIT ? OFFSET ?", (case_id, limit, offset)).fetchall()
        return envelope({"page": page, "limit": limit, "items": [json_row(r) for r in rows]})

    @app.get("/api/cases/<case_id>/graph")
    def graph(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        return envelope(_graph(case_id))

    @app.get("/api/cases/<case_id>/attribution")
    def attribution(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        rows = get_db().execute("SELECT a.*, w.address AS wallet_address, e.name AS entity_name, e.type AS entity_type FROM attributions a JOIN wallets w ON w.id=a.wallet_id LEFT JOIN entities e ON e.id=a.entity_id WHERE a.case_id=?", (case_id,)).fetchall()
        return envelope([json_row(r) for r in rows])

    @app.get("/api/cases/<case_id>/risk")
    def risk(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        row = get_db().execute("SELECT * FROM risk_assessments WHERE case_id=? ORDER BY created_at DESC LIMIT 1", (case_id,)).fetchone()
        if not row: return envelope(None)
        indicators = get_db().execute("SELECT code, description, severity, evidence FROM risk_indicators WHERE risk_assessment_id=?", (row["id"],)).fetchall()
        result = json_row(row); result["indicators"] = [json_row(i) for i in indicators]
        return envelope(result)

    @app.get("/api/cases/<case_id>/report")
    def report(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        db = get_db()
        transaction_rows = db.execute("WITH RECURSIVE connected(wallet_id, depth) AS (SELECT wallet_id, 0 FROM attributions WHERE case_id=? UNION SELECT t.to_wallet_id, connected.depth + 1 FROM transactions t JOIN connected ON t.from_wallet_id=connected.wallet_id WHERE connected.depth < 5) SELECT DISTINCT t.*, fw.address AS from_address, tw.address AS to_address FROM transactions t JOIN wallets fw ON fw.id=t.from_wallet_id JOIN wallets tw ON tw.id=t.to_wallet_id JOIN connected c ON c.wallet_id=t.from_wallet_id ORDER BY t.timestamp", (case_id,)).fetchall()
        attribution_rows = db.execute("SELECT a.*, w.address AS wallet_address, e.name AS entity_name, e.type AS entity_type FROM attributions a JOIN wallets w ON w.id=a.wallet_id LEFT JOIN entities e ON e.id=a.entity_id WHERE a.case_id=?", (case_id,)).fetchall()
        risk_row = db.execute("SELECT * FROM risk_assessments WHERE case_id=? ORDER BY created_at DESC LIMIT 1", (case_id,)).fetchone()
        risk_data = None
        if risk_row:
            risk_data = json_row(risk_row)
            risk_data["indicators"] = [json_row(item) for item in db.execute("SELECT code, description, severity, evidence FROM risk_indicators WHERE risk_assessment_id=?", (risk_row["id"],)).fetchall()]
        return envelope({"case": json_row(get_case(case_id)), "transactions": [json_row(row) for row in transaction_rows], "graph": _graph(case_id), "attribution": [json_row(row) for row in attribution_rows], "risk": risk_data})

    with app.app_context():
        if app.config.get("TESTING") and app.config.get("DATABASE") is not None:
            init_db(app.config["DATABASE"])
        else:
            init_db()
    return app


def _demo_transactions(db, wallet_id, address, chain, timestamp):
    existing = db.execute("SELECT t.*, fw.address AS from_address, tw.address AS to_address FROM transactions t JOIN wallets fw ON fw.id=t.from_wallet_id JOIN wallets tw ON tw.id=t.to_wallet_id WHERE t.from_wallet_id=? OR t.to_wallet_id=?", (wallet_id, wallet_id)).fetchall()
    if existing: return [json_row(x) for x in existing]
    intermediary_id, target_id = str(uuid.uuid4()), str(uuid.uuid4())
    db.execute("INSERT INTO wallets (id,address,chain,wallet_type,created_at) VALUES (?,?,?,?,?)", (intermediary_id, "0x" + "1" * 40, chain, "intermediary", timestamp))
    db.execute("INSERT INTO wallets (id,address,chain,wallet_type,created_at) VALUES (?,?,?,?,?)", (target_id, "0x" + "2" * 40, chain, "vasp", timestamp))
    rows = [(str(uuid.uuid4()), "0x" + "a" * 64, chain, wallet_id, intermediary_id, "ETH", "7.450000000000000000", 20000001, timestamp, "confirmed", 1), (str(uuid.uuid4()), "0x" + "b" * 64, chain, intermediary_id, target_id, "ETH", "5.000000000000000000", 20000002, timestamp, "confirmed", 2)]
    db.executemany("INSERT INTO transactions (id,transaction_hash,chain,from_wallet_id,to_wallet_id,asset,amount,block_number,timestamp,status,hop) VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
    return [json_row(x) for x in db.execute("SELECT t.*, fw.address AS from_address, tw.address AS to_address FROM transactions t JOIN wallets fw ON fw.id=t.from_wallet_id JOIN wallets tw ON tw.id=t.to_wallet_id WHERE t.id IN (?, ?)", (rows[0][0], rows[1][0])).fetchall()]


def _upsert_attribution(db, case_id, wallet_id):
    entity = db.execute("SELECT * FROM entities WHERE name=?", ("Demo Exchange",)).fetchone()
    if entity is None:
        entity_id = str(uuid.uuid4()); db.execute("INSERT INTO entities (id,name,type,verification_status,created_at) VALUES (?,?,?,?,?)", (entity_id, "Demo Exchange", "vasp", "known_address", now_iso()))
    else: entity_id = entity["id"]
    row = db.execute("SELECT a.*, e.name AS entity_name, e.type AS entity_type FROM attributions a JOIN entities e ON e.id=a.entity_id WHERE case_id=?", (case_id,)).fetchone()
    if row is None:
        db.execute("INSERT INTO attributions (id,case_id,wallet_id,entity_id,match_type,confidence,evidence,created_at) VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), case_id, wallet_id, entity_id, "known_address", 0.92, '["Known VASP wallet address match"]', now_iso()))
        row = db.execute("SELECT a.*, e.name AS entity_name, e.type AS entity_type FROM attributions a JOIN entities e ON e.id=a.entity_id WHERE case_id=?", (case_id,)).fetchone()
    return json_row(row)


def _upsert_risk(db, case_id, tx_count):
    score, level = (87, "high") if tx_count >= 2 else (20, "low")
    row = db.execute("SELECT * FROM risk_assessments WHERE case_id=? ORDER BY created_at DESC LIMIT 1", (case_id,)).fetchone()
    if row is None:
        rid = str(uuid.uuid4()); db.execute("INSERT INTO risk_assessments (id,case_id,score,level,created_at) VALUES (?,?,?,?,?)", (rid, case_id, score, level, now_iso()))
        db.execute("INSERT INTO risk_indicators (id,risk_assessment_id,code,description,severity,evidence) VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), rid, "MULTI_HOP", "Funds moved through multiple intermediary wallets", "medium", '{"hop_count": 2}'))
        row = db.execute("SELECT * FROM risk_assessments WHERE id=?", (rid,)).fetchone()
    return row


def _graph(case_id):
    db = get_db(); wallet_rows = db.execute("SELECT DISTINCT w.* FROM wallets w JOIN attributions a ON a.wallet_id=w.id WHERE a.case_id=?", (case_id,)).fetchall()
    tx_rows = db.execute("WITH RECURSIVE connected(wallet_id, depth) AS (SELECT wallet_id, 0 FROM attributions WHERE case_id=? UNION SELECT t.to_wallet_id, connected.depth + 1 FROM transactions t JOIN connected ON t.from_wallet_id=connected.wallet_id WHERE connected.depth < 5) SELECT DISTINCT t.*, fw.address AS from_address, tw.address AS to_address FROM transactions t JOIN wallets fw ON fw.id=t.from_wallet_id JOIN wallets tw ON tw.id=t.to_wallet_id JOIN connected c ON c.wallet_id=t.from_wallet_id", (case_id,)).fetchall()
    nodes = {r["id"]: {"id": "wallet_" + r["id"], "address": r["address"], "type": r["wallet_type"], "label": "Reported Wallet" if r["wallet_type"] == "reported_wallet" else r["wallet_type"].replace("_", " ").title()} for r in wallet_rows}
    for t in tx_rows:
        for key, address, wtype in ((t["from_wallet_id"], t["from_address"], "intermediary"), (t["to_wallet_id"], t["to_address"], "intermediary")):
            nodes.setdefault(key, {"id": "wallet_" + key, "address": address, "type": wtype, "label": wtype.title()})
    edges = [{"id": "edge_" + t["id"], "source": "wallet_" + t["from_wallet_id"], "target": "wallet_" + t["to_wallet_id"], "transaction_hash": t["transaction_hash"], "amount": t["amount"], "asset": t["asset"], "timestamp": t["timestamp"], "hop": t["hop"]} for t in tx_rows]
    return {"nodes": list(nodes.values()), "edges": edges}


app = create_app()

if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
