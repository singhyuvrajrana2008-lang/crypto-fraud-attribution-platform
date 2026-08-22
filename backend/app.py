from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from flask import Flask, g, jsonify, request
from flask_cors import CORS

try:
    from .storage import is_postgres_connection, open_database
except ImportError:  # pragma: no cover
    from storage import is_postgres_connection, open_database

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = BASE_DIR / "database" / "local.sqlite3"
ETH_ADDRESS = re.compile(r"^0x[a-fA-F0-9]{40}$")
UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")
CHAIN = "ethereum"
STATUSES = ("new", "analyzing", "under_review", "escalated", "closed")
RISK_LEVELS = ("low", "medium", "high", "critical")
FRAUD_TYPES = ("investment_scam", "romance_scam", "phishing", "ransomware", "pig_butchering", "other")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def envelope(data: Any = None, error: dict[str, str] | None = None, success: bool = True):
    return jsonify({"success": success, "data": data if success else None, "error": error if not success else None})


def fail(code: str, message: str, status: int):
    return envelope(error={"code": code, "message": message}, success=False), status


def json_text(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"))


def db_path() -> str:
    configured = os.getenv("DATABASE_URL", "")
    if configured.startswith("sqlite:///"):
        return configured.removeprefix("sqlite:///")
    if configured and not configured.startswith(("postgresql://", "postgres://")):
        return configured
    return os.getenv("SQLITE_PATH", str(DEFAULT_DB))


def get_db():
    if "db" not in g:
        database_url = os.getenv("DATABASE_URL", "")
        require_postgres = os.getenv("REQUIRE_POSTGRES", "false").lower() == "true"
        if require_postgres and not database_url.startswith(("postgresql://", "postgres://")):
            raise RuntimeError("REQUIRE_POSTGRES is enabled but DATABASE_URL is not a Postgres URL")
        g.db = open_database(database_url, str(DEFAULT_DB))
    return g.db


def init_db(database=None):
    database = database or get_db()
    schema_name = "schema.postgres.sql" if is_postgres_connection(database) else "schema.sqlite.sql"
    schema = (BASE_DIR / "database" / schema_name).read_text()
    if is_postgres_connection(database):
        for statement in schema.split(";"):
            statement = statement.strip()
            if statement:
                database.execute(statement)
    else:
        database.executescript(schema)
    database.commit()


def row_dict(row):
    if row is None:
        return None
    result = dict(row)
    for key, value in result.items():
        if isinstance(value, uuid.UUID):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        elif isinstance(value, Decimal):
            result[key] = format(value, "f")
    return result


def json_row(row):
    result = row_dict(row)
    if result:
        for key in ("confidence",):
            if result.get(key) is not None:
                result[key] = float(result[key])
        for key in ("priority_factors", "evidence", "details"):
            if key in result and isinstance(result[key], str):
                try:
                    result[key] = json.loads(result[key])
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


def audit(case_id: str | None, action: str, details: dict[str, Any] | None = None):
    get_db().execute(
        "INSERT INTO audit_logs (id,case_id,user_id,action,details,created_at) VALUES (?,?,?,?,?,?)",
        (str(uuid.uuid4()), case_id, None, action, json_text(details or {}), now_iso()),
    )


def amount_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value or "0")).quantize(Decimal("0.00000001"))
    except (InvalidOperation, ValueError):
        raise ValueError("amount must be numeric")


def stable_address(seed: str) -> str:
    return "0x" + hashlib.sha256(seed.encode()).hexdigest()[:40]


def case_base(case):
    data = json_row(case) or {}
    data.setdefault("blockchain", data.get("chain", CHAIN))
    data["reported_wallet_address"] = data.get("reported_wallet_address")
    return data


def analysis_summary(case_id: str):
    db = get_db()
    tx_count = db.execute("SELECT COUNT(*) AS n FROM case_transactions WHERE case_id=?", (case_id,)).fetchone()["n"]
    hop = db.execute("SELECT COALESCE(MAX(t.hop),0) AS n FROM case_transactions ct JOIN transactions t ON t.id=ct.transaction_id WHERE ct.case_id=?", (case_id,)).fetchone()["n"]
    wallet = db.execute("SELECT reported_wallet_address FROM cases WHERE id=?", (case_id,)).fetchone()
    risk = db.execute("SELECT * FROM risk_assessments WHERE case_id=? ORDER BY created_at DESC LIMIT 1", (case_id,)).fetchone()
    priority = db.execute("SELECT * FROM priorities WHERE case_id=? ORDER BY created_at DESC LIMIT 1", (case_id,)).fetchone()
    attribution = db.execute("SELECT e.name,e.type,a.confidence FROM attributions a LEFT JOIN entities e ON e.id=a.entity_id WHERE a.case_id=? LIMIT 1", (case_id,)).fetchone()
    related = db.execute("SELECT COUNT(*) AS n FROM case_relationships WHERE case_id=?", (case_id,)).fetchone()["n"]
    return {"status": "completed" if tx_count else "pending", "transaction_count": tx_count, "hop_count": hop, "wallet_address": wallet["reported_wallet_address"] if wallet else None, "risk": json_row(risk), "priority": json_row(priority), "related_case_count": related, "potential_vasp": json_row(attribution)}


def graph_data(case_id: str):
    db = get_db()
    wallets = db.execute("SELECT DISTINCT w.* FROM wallets w JOIN case_wallets cw ON cw.wallet_id=w.id WHERE cw.case_id=?", (case_id,)).fetchall()
    txs = db.execute("SELECT t.*, fw.address AS from_address, tw.address AS to_address, fw.wallet_type AS from_type, tw.wallet_type AS to_type FROM case_transactions ct JOIN transactions t ON t.id=ct.transaction_id JOIN wallets fw ON fw.id=t.from_wallet_id JOIN wallets tw ON tw.id=t.to_wallet_id WHERE ct.case_id=? ORDER BY t.timestamp", (case_id,)).fetchall()
    nodes = {}
    for w in wallets:
        nodes[w["id"]] = {"id": "wallet_" + w["id"], "address": w["address"], "type": w["wallet_type"], "label": "Reported Wallet" if w["wallet_type"] == "reported_wallet" else w["wallet_type"].replace("_", " ").title()}
    edges = []
    for t in txs:
        nodes.setdefault(t["from_wallet_id"], {"id": "wallet_" + t["from_wallet_id"], "address": t["from_address"], "type": t["from_type"], "label": t["from_type"].title()})
        nodes.setdefault(t["to_wallet_id"], {"id": "wallet_" + t["to_wallet_id"], "address": t["to_address"], "type": t["to_type"], "label": t["to_type"].title()})
        edges.append({"id": "edge_" + t["id"], "source": "wallet_" + t["from_wallet_id"], "target": "wallet_" + t["to_wallet_id"], "transaction_hash": t["transaction_hash"], "amount": str(t["amount"]), "asset": t["asset"], "timestamp": t["timestamp"], "hop": t["hop"]})
    return {"nodes": list(nodes.values()), "edges": edges}


def upsert_risk(db, case_id: str, reported_amount: Any, txs: list[dict[str, Any]], related_count: int, has_vasp: bool):
    amount = amount_decimal(reported_amount)
    max_hop = max((int(t.get("hop") or 0) for t in txs), default=0)
    indicators = []
    if max_hop >= 2:
        indicators.append(("MULTI_HOP", "Funds moved through multiple intermediary wallets", "high", {"hop_count": max_hop}))
    if len(txs) >= 2:
        indicators.append(("REPEATED_ACTIVITY", "Multiple observed transactions involve the reported wallet flow", "medium", {"transaction_count": len(txs)}))
    if has_vasp:
        indicators.append(("VASP_INTERACTION", "A downstream wallet has a potential demo VASP association", "medium", {"association": "potential"}))
    if related_count >= 2:
        indicators.append(("MULTIPLE_RELATED_CASES", "Multiple complaints share observable wallet-flow evidence", "high", {"related_case_count": related_count}))
    if amount >= 10000:
        indicators.append(("HIGH_FINANCIAL_IMPACT", "Reported amount exceeds the high-impact threshold", "high", {"reported_amount": str(amount)}))
    score = min(100, 22 + max_hop * 20 + min(len(txs) * 5, 15) + (15 if has_vasp else 0) + min(related_count * 5, 20) + (20 if amount >= 10000 else 0))
    level = "critical" if score >= 95 else "high" if score >= 60 else "medium" if score >= 35 else "low"
    old = db.execute("SELECT id FROM risk_assessments WHERE case_id=? ORDER BY created_at DESC LIMIT 1", (case_id,)).fetchone()
    if old:
        rid = old["id"]
        db.execute("UPDATE risk_assessments SET score=?,level=?,created_at=? WHERE id=?", (score, level, now_iso(), rid))
        db.execute("DELETE FROM risk_indicators WHERE risk_assessment_id=?", (rid,))
    else:
        rid = str(uuid.uuid4())
        db.execute("INSERT INTO risk_assessments (id,case_id,score,level,created_at) VALUES (?,?,?,?,?)", (rid, case_id, score, level, now_iso()))
    for code, description, severity, evidence in indicators:
        db.execute("INSERT INTO risk_indicators (id,risk_assessment_id,code,description,severity,evidence) VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), rid, code, description, severity, json_text(evidence)))
    return db.execute("SELECT * FROM risk_assessments WHERE id=?", (rid,)).fetchone()


def calculate_priority(db, case_id: str):
    row = db.execute("SELECT c.reported_amount, r.score AS risk_score FROM cases c LEFT JOIN risk_assessments r ON r.case_id=c.id WHERE c.id=? ORDER BY r.created_at DESC LIMIT 1", (case_id,)).fetchone()
    amount = amount_decimal(row["reported_amount"] if row else 0)
    related = db.execute("SELECT COUNT(*) AS n FROM case_relationships WHERE case_id=?", (case_id,)).fetchone()["n"]
    tx_count = db.execute("SELECT COUNT(*) AS n FROM case_transactions WHERE case_id=?", (case_id,)).fetchone()["n"]
    max_hop = db.execute("SELECT COALESCE(MAX(t.hop),0) AS n FROM case_transactions ct JOIN transactions t ON t.id=ct.transaction_id WHERE ct.case_id=?", (case_id,)).fetchone()["n"]
    vasp = db.execute("SELECT COUNT(*) AS n FROM attributions a JOIN entities e ON e.id=a.entity_id WHERE a.case_id=? AND e.type IN ('vasp','exchange')", (case_id,)).fetchone()["n"] > 0
    factors = {"financial_impact": min(100, int(amount / Decimal("100"))), "linked_cases": min(100, related * 25), "repeated_activity": min(100, tx_count * 30), "fund_movement": min(100, max_hop * 30), "vasp_interaction": 80 if vasp else 0}
    score = round(factors["financial_impact"] * .25 + factors["linked_cases"] * .2 + factors["repeated_activity"] * .15 + factors["fund_movement"] * .2 + factors["vasp_interaction"] * .2)
    score = min(100, max(0, score))
    existing = db.execute("SELECT id FROM priorities WHERE case_id=?", (case_id,)).fetchone()
    values = (score, json_text(factors), now_iso())
    if existing:
        db.execute("UPDATE priorities SET priority_score=?,priority_factors=?,created_at=? WHERE id=?", (*values, existing["id"]))
    else:
        db.execute("INSERT INTO priorities (id,case_id,priority_score,priority_factors,created_at) VALUES (?,?,?,?,?)", (str(uuid.uuid4()), case_id, *values))
    db.execute("UPDATE cases SET priority_score=?,priority_factors=? WHERE id=?", (score, json_text(factors), case_id))
    return score, factors


def create_alert(db, case_id, alert_type, title, message, severity):
    exists = db.execute("SELECT id FROM alerts WHERE case_id=? AND type=?", (case_id, alert_type)).fetchone()
    if not exists:
        db.execute("INSERT INTO alerts (id,case_id,type,title,message,severity,read,created_at) VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), case_id, alert_type, title, message, severity, False, now_iso()))


def correlate(db, case_id: str):
    base = db.execute("SELECT reported_wallet_address FROM cases WHERE id=?", (case_id,)).fetchone()
    if not base:
        return []
    rows = db.execute("SELECT id,reported_wallet_address FROM cases WHERE id<>?", (case_id,)).fetchall()
    results = []
    for other in rows:
        shared = None
        if base["reported_wallet_address"] and base["reported_wallet_address"] == other["reported_wallet_address"]:
            shared = ("shared_wallet", 0.98, base["reported_wallet_address"])
        else:
            common = db.execute("SELECT w.address FROM case_wallets a JOIN case_wallets b ON a.wallet_id=b.wallet_id JOIN wallets w ON w.id=a.wallet_id WHERE a.case_id=? AND b.case_id=? AND w.address<>? LIMIT 1", (case_id, other["id"], base["reported_wallet_address"] or "")).fetchone()
            if common:
                shared = ("shared_downstream_wallet", 0.84, common["address"])
        if shared:
            exists = db.execute("SELECT id FROM case_relationships WHERE case_id=? AND related_case_id=?", (case_id, other["id"])).fetchone()
            if not exists:
                db.execute("INSERT INTO case_relationships (id,case_id,related_case_id,relationship_type,confidence,evidence,shared_wallet,created_at) VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), case_id, other["id"], shared[0], shared[1], json_text({"observable": "shared wallet-flow evidence", "note": "potentially related cases; not proof of common identity"}), shared[2], now_iso()))
            results.append({"related_case_id": other["id"], "relationship_type": shared[0], "confidence": shared[1], "evidence": {"observable": "shared wallet-flow evidence", "note": "potentially related cases; not proof of common identity"}, "shared_wallet": shared[2]})
    return results


def analyze_case(case_id: str, address: str, chain: str):
    db = get_db(); timestamp = now_iso()
    wallet = db.execute("SELECT * FROM wallets WHERE address=? AND chain=?", (address, chain)).fetchone()
    if wallet is None:
        wid = str(uuid.uuid4())
        db.execute("INSERT INTO wallets (id,address,chain,wallet_type,created_at) VALUES (?,?,?,?,?)", (wid, address, chain, "reported_wallet", timestamp))
        wallet = db.execute("SELECT * FROM wallets WHERE id=?", (wid,)).fetchone()
    else:
        wid = wallet["id"]
    db.execute("INSERT OR IGNORE INTO case_wallets (id,case_id,wallet_id,role,created_at) VALUES (?,?,?,?,?)", (str(uuid.uuid4()), case_id, wid, "reported", timestamp))
    existing = db.execute("SELECT t.*,fw.address AS from_address,tw.address AS to_address FROM case_transactions ct JOIN transactions t ON t.id=ct.transaction_id JOIN wallets fw ON fw.id=t.from_wallet_id JOIN wallets tw ON tw.id=t.to_wallet_id WHERE ct.case_id=? ORDER BY t.hop", (case_id,)).fetchall()
    if not existing:
        intermediary_address = stable_address(address + ":intermediary")
        vasp_address = stable_address(address + ":vasp")
        ids = []
        for addr, wtype in ((intermediary_address, "intermediary"), (vasp_address, "vasp")):
            found = db.execute("SELECT id FROM wallets WHERE address=? AND chain=?", (addr, chain)).fetchone()
            if found: ids.append(found["id"])
            else:
                new_id = str(uuid.uuid4()); ids.append(new_id)
                db.execute("INSERT INTO wallets (id,address,chain,wallet_type,created_at) VALUES (?,?,?,?,?)", (new_id, addr, chain, wtype, timestamp))
            db.execute("INSERT OR IGNORE INTO case_wallets (id,case_id,wallet_id,role,created_at) VALUES (?,?,?,?,?)", (str(uuid.uuid4()), case_id, ids[-1], "downstream", timestamp))
        tx_specs = [(stable_address(address + ":tx1"), wid, ids[0], "7.450000000000000000", 1), (stable_address(address + ":tx2"), ids[0], ids[1], "5.000000000000000000", 2)]
        for tx_hash, from_id, to_id, amount, hop in tx_specs:
            tx_id = str(uuid.uuid4())
            db.execute("INSERT OR IGNORE INTO transactions (id,transaction_hash,chain,from_wallet_id,to_wallet_id,asset,amount,block_number,timestamp,status,hop,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (tx_id, tx_hash, chain, from_id, to_id, "ETH", amount, 20000000 + hop, timestamp, "confirmed", hop, timestamp))
            found_tx = db.execute("SELECT id FROM transactions WHERE transaction_hash=? AND chain=?", (tx_hash, chain)).fetchone()
            db.execute("INSERT OR IGNORE INTO case_transactions (id,case_id,transaction_id,created_at) VALUES (?,?,?,?)", (str(uuid.uuid4()), case_id, found_tx["id"], timestamp))
    db.execute("UPDATE cases SET reported_wallet_address=?,blockchain=?,analysis_status=?,status=?,updated_at=? WHERE id=?", (address, chain, "completed", "analyzing", timestamp, case_id))
    attr = db.execute("SELECT id FROM entities WHERE name=?", ("Demo Exchange",)).fetchone()
    if not attr:
        eid = str(uuid.uuid4()); db.execute("INSERT INTO entities (id,name,type,verification_status,created_at) VALUES (?,?,?,?,?)", (eid, "Demo Exchange", "vasp", "demo", timestamp))
    else: eid = attr["id"]
    exists_attr = db.execute("SELECT id FROM attributions WHERE case_id=?", (case_id,)).fetchone()
    if not exists_attr:
        db.execute("INSERT INTO attributions (id,case_id,wallet_id,entity_id,match_type,confidence,evidence,created_at) VALUES (?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), case_id, wid, eid, "known_address", .92, json_text(["Deterministic demo VASP association"]), timestamp))
        audit(case_id, "VASP_ASSOCIATION_FOUND", {"entity": "Demo Exchange", "demo": True})
    txs = [json_row(x) for x in db.execute("SELECT t.* FROM case_transactions ct JOIN transactions t ON t.id=ct.transaction_id WHERE ct.case_id=?", (case_id,)).fetchall()]
    related = correlate(db, case_id)
    has_vasp = True
    db.execute("INSERT INTO analysis_results (id,case_id,status,transaction_count,hop_count,provider,created_at) VALUES (?,?,?,?,?,?,?)", (str(uuid.uuid4()), case_id, "completed", len(txs), max((int(t["hop"] or 0) for t in txs), default=0), "mock", timestamp))
    risk = upsert_risk(db, case_id, get_case(case_id)["reported_amount"], txs, len(related), has_vasp)
    score, factors = calculate_priority(db, case_id)
    risk_score = int(risk["score"])
    create_alert(db, case_id, "VASP_MATCH", "Potential VASP association", "A downstream wallet has a deterministic demo VASP association.", "medium")
    if risk_score >= 60: create_alert(db, case_id, "HIGH_RISK_CASE", "High-risk investigative signal", "The rule-based risk score is high; review observable evidence.", "high")
    if len(related) >= 2: create_alert(db, case_id, "MULTIPLE_RELATED_CASES", "Multiple potentially related cases", "Observable wallet-flow evidence links multiple complaints.", "high")
    if Decimal(str(get_case(case_id)["reported_amount"] or 0)) >= 10000: create_alert(db, case_id, "HIGH_FINANCIAL_IMPACT", "High financial impact", "Reported amount exceeds the configured threshold.", "high")
    audit(case_id, "ANALYSIS_COMPLETED", {"transaction_count": len(txs), "priority_score": score})
    db.commit()
    return {"case_id": case_id, "wallet": {"id": wid, "address": address, "chain": chain, "type": "reported_wallet"}, "analysis": {"status": "completed", "transaction_count": len(txs), "hop_count": max((int(t["hop"] or 0) for t in txs), default=0), "total_transferred_value": "12.450000000000000000"}, "risk": {"score": risk_score, "level": risk["level"]}, "priority": {"priority_score": score, "priority_factors": factors}, "attribution": {"entity_name": "Demo Exchange", "entity_type": "vasp", "confidence": .92}}


def create_app(test_config: dict[str, Any] | None = None):
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=os.getenv("SECRET_KEY", "development-only"))
    if test_config: app.config.update(test_config)
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    CORS(app, origins=[x.strip() for x in origins.split(",") if x.strip()])

    @app.before_request
    def before():
        if app.config.get("TESTING") and app.config.get("DATABASE") is not None:
            g.db = app.config["DATABASE"]; g.db.row_factory = sqlite3.Row; g.db.execute("PRAGMA foreign_keys = ON")
        else: get_db()

    @app.teardown_appcontext
    def teardown(_error=None):
        db = g.pop("db", None)
        if db is not None and not (app.config.get("TESTING") and app.config.get("DATABASE") is not None): db.close()

    @app.errorhandler(Exception)
    def handle_error(error):
        app.logger.exception("Unhandled API error: %s", error)
        return fail("INTERNAL_ERROR", "An internal server error occurred", 500)

    @app.get("/api/health")
    def health():
        get_db().execute("SELECT 1").fetchone(); return envelope({"status": "ok"})

    @app.post("/api/cases")
    def create_case_route():
        body, error = require_json()
        if error: return error
        if not isinstance(body.get("case_reference"), str) or not body["case_reference"].strip(): return fail("MISSING_FIELD", "case_reference is required", 400)
        if not isinstance(body.get("fraud_type"), str) or not body["fraud_type"].strip(): return fail("MISSING_FIELD", "fraud_type is required", 400)
        try: amount = str(amount_decimal(body.get("reported_amount", "0")))
        except ValueError as exc: return fail("VALIDATION_ERROR", str(exc), 400)
        cid, ts = str(uuid.uuid4()), now_iso(); db = get_db()
        try:
            db.execute("INSERT INTO cases (id,case_reference,fraud_type,reported_amount,currency,reported_wallet_address,blockchain,description,status,analysis_status,priority_score,priority_factors,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (cid, body["case_reference"].strip(), body["fraud_type"].strip(), amount, body.get("currency", "ETH"), body.get("reported_wallet_address"), body.get("blockchain", CHAIN), body.get("description"), body.get("status", "new"), "pending", 0, json_text({}), ts, ts))
            audit(cid, "CASE_CREATED", {"demo": bool(body.get("demo"))}); db.commit()
        except Exception as exc:
            if "unique" in str(exc).lower(): return fail("CONFLICT", "case_reference already exists", 409)
            raise
        return envelope(case_base(get_case(cid))), 201

    @app.get("/api/cases")
    def list_cases():
        args = request.args; page = max(1, int(args.get("page", 1))); limit = min(100, max(1, int(args.get("limit", 25))))
        sort = args.get("sort", args.get("priority", "created_at")); direction = "ASC" if args.get("order") == "asc" else "DESC"
        sort_map = {"priority": "c.priority_score", "priority_score": "c.priority_score", "risk_score": "COALESCE(r.score,0)", "amount": "c.reported_amount", "created_at": "c.created_at"}
        order = sort_map.get(sort, "c.created_at")
        where, params = ["1=1"], []
        search = args.get("search")
        if search: where.append("(c.case_reference LIKE ? OR c.reported_wallet_address LIKE ? OR EXISTS (SELECT 1 FROM case_transactions ct JOIN transactions t ON t.id=ct.transaction_id WHERE ct.case_id=c.id AND t.transaction_hash LIKE ?))"); params += [f"%{search}%"] * 3
        for key, column in (("status", "c.status"), ("fraud_type", "c.fraud_type"), ("blockchain", "c.blockchain")):
            if args.get(key): where.append(f"{column}=?"); params.append(args[key])
        if args.get("risk_level") or args.get("risk"): where.append("COALESCE(r.level,'low')=?"); params.append(args.get("risk_level", args.get("risk")))
        if args.get("min_amount"): where.append("c.reported_amount>=?"); params.append(args["min_amount"])
        if args.get("max_amount"): where.append("c.reported_amount<=?"); params.append(args["max_amount"])
        if args.get("date_from"): where.append("c.created_at>=?"); params.append(args["date_from"])
        if args.get("date_to"): where.append("c.created_at<=?"); params.append(args["date_to"])
        if args.get("vasp") == "true": where.append("EXISTS (SELECT 1 FROM attributions a JOIN entities e ON e.id=a.entity_id WHERE a.case_id=c.id AND e.type IN ('vasp','exchange'))")
        db = get_db(); total = db.execute(f"SELECT COUNT(*) AS n FROM cases c LEFT JOIN risk_assessments r ON r.case_id=c.id WHERE {' AND '.join(where)}", tuple(params)).fetchone()["n"]
        rows = db.execute(f"SELECT c.*,COALESCE(r.score,0) AS risk_score,COALESCE(r.level,'low') AS risk_level,(SELECT COUNT(*) FROM case_relationships cr WHERE cr.case_id=c.id) AS related_case_count FROM cases c LEFT JOIN risk_assessments r ON r.case_id=c.id WHERE {' AND '.join(where)} ORDER BY {order} {direction} LIMIT ? OFFSET ?", tuple(params + [limit, (page-1)*limit])).fetchall()
        return envelope({"page": page, "limit": limit, "total": total, "items": [case_base(r) for r in rows]})

    @app.get("/api/cases/top-priority")
    def top_priority():
        limit = min(100, max(1, int(request.args.get("limit", 10)))); db = get_db()
        rows = db.execute("SELECT c.*,COALESCE(r.score,0) AS risk_score,COALESCE(r.level,'low') AS risk_level,(SELECT COUNT(*) FROM case_relationships cr WHERE cr.case_id=c.id) AS related_case_count FROM cases c LEFT JOIN risk_assessments r ON r.case_id=c.id ORDER BY c.priority_score DESC,c.created_at ASC LIMIT ?", (limit,)).fetchall()
        items = []
        for rank, row in enumerate(rows, 1):
            data = case_base(row); data["rank"] = rank; data["case_id"] = data["id"]; data["priority_score"] = int(data.get("priority_score") or 0); items.append(data)
        return envelope(items)

    @app.get("/api/cases/<case_id>")
    def detail(case_id):
        case = get_case(case_id)
        if not case: return fail("CASE_NOT_FOUND", "Case not found", 404)
        audit(case_id, "CASE_VIEWED"); get_db().commit(); data = case_base(case); data.update(analysis_summary(case_id)); return envelope(data)

    @app.patch("/api/cases/<case_id>")
    def patch_case(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        body, error = require_json()
        if error: return error
        allowed = {k: body[k] for k in ("description", "fraud_type", "currency") if k in body};
        if not allowed: return fail("VALIDATION_ERROR", "No editable fields supplied", 400)
        db = get_db(); db.execute(f"UPDATE cases SET {','.join(k+'=?' for k in allowed)},updated_at=? WHERE id=?", tuple(allowed.values()) + (now_iso(), case_id)); db.commit(); return envelope(case_base(get_case(case_id)))

    @app.patch("/api/cases/<case_id>/status")
    def update_status(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        body, error = require_json()
        if error: return error
        status = body.get("status")
        if status not in STATUSES: return fail("INVALID_STATUS", f"status must be one of: {', '.join(STATUSES)}", 400)
        db = get_db(); old = get_case(case_id)["status"]; db.execute("UPDATE cases SET status=?,updated_at=? WHERE id=?", (status, now_iso(), case_id)); audit(case_id, "STATUS_CHANGED", {"old_status": old, "new_status": status}); db.commit(); return envelope(case_base(get_case(case_id)))

    @app.post("/api/investigations/analyze")
    def analyze_route():
        body, error = require_json()
        if error: return error
        cid, address, chain = body.get("case_id"), body.get("wallet_address"), body.get("chain")
        if not get_case(cid): return fail("CASE_NOT_FOUND", "case_id does not identify an existing case", 404)
        if not validate_address(address): return fail("INVALID_WALLET_ADDRESS", "wallet_address must be a valid Ethereum address", 400)
        if chain != CHAIN: return fail("UNSUPPORTED_CHAIN", "Only the ethereum chain is supported in the MVP", 400)
        audit(cid, "ANALYSIS_STARTED"); get_db().commit(); return envelope(analyze_case(cid, address, chain))

    @app.get("/api/cases/<case_id>/transactions")
    def transactions(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        try: page, limit = max(1, int(request.args.get("page", 1))), min(100, max(1, int(request.args.get("limit", 50))))
        except ValueError: return fail("VALIDATION_ERROR", "page and limit must be integers", 400)
        db = get_db(); total = db.execute("SELECT COUNT(*) AS n FROM case_transactions WHERE case_id=?", (case_id,)).fetchone()["n"]
        rows = db.execute("SELECT t.*,fw.address AS from_address,tw.address AS to_address FROM case_transactions ct JOIN transactions t ON t.id=ct.transaction_id JOIN wallets fw ON fw.id=t.from_wallet_id JOIN wallets tw ON tw.id=t.to_wallet_id WHERE ct.case_id=? ORDER BY t.hop,t.timestamp LIMIT ? OFFSET ?", (case_id, limit, (page-1)*limit)).fetchall()
        return envelope({"page": page, "limit": limit, "total": total, "items": [json_row(r) for r in rows]})

    @app.get("/api/cases/<case_id>/graph")
    def graph(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        return envelope(graph_data(case_id))

    @app.get("/api/cases/<case_id>/attribution")
    def attribution(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        rows = get_db().execute("SELECT a.*,w.address AS wallet_address,e.name AS entity_name,e.type AS entity_type FROM attributions a JOIN wallets w ON w.id=a.wallet_id LEFT JOIN entities e ON e.id=a.entity_id WHERE a.case_id=?", (case_id,)).fetchall(); return envelope([json_row(r) for r in rows])

    @app.get("/api/cases/<case_id>/risk")
    def risk(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        db = get_db(); row = db.execute("SELECT * FROM risk_assessments WHERE case_id=? ORDER BY created_at DESC LIMIT 1", (case_id,)).fetchone()
        if not row: return envelope(None)
        result = json_row(row); result["indicators"] = [json_row(x) for x in db.execute("SELECT code,description,severity,evidence FROM risk_indicators WHERE risk_assessment_id=?", (row["id"],)).fetchall()]; return envelope(result)

    @app.get("/api/cases/<case_id>/priority")
    def priority(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        row = get_db().execute("SELECT * FROM priorities WHERE case_id=?", (case_id,)).fetchone(); return envelope(json_row(row) if row else None)

    @app.get("/api/cases/<case_id>/related")
    def related(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        rows = get_db().execute("SELECT * FROM case_relationships WHERE case_id=? ORDER BY confidence DESC", (case_id,)).fetchall(); return envelope([json_row(x) for x in rows])

    @app.get("/api/dashboard/summary")
    def summary():
        db = get_db(); total = db.execute("SELECT COUNT(*) AS n FROM cases").fetchone()["n"]; amounts = db.execute("SELECT COALESCE(SUM(reported_amount),0) AS total FROM cases").fetchone()["total"]
        return envelope({"total_cases": total, "new_cases": db.execute("SELECT COUNT(*) AS n FROM cases WHERE status='new'").fetchone()["n"], "analyzing_cases": db.execute("SELECT COUNT(*) AS n FROM cases WHERE status='analyzing'").fetchone()["n"], "high_priority_cases": db.execute("SELECT COUNT(*) AS n FROM cases WHERE priority_score>=70").fetchone()["n"], "medium_priority_cases": db.execute("SELECT COUNT(*) AS n FROM cases WHERE priority_score BETWEEN 35 AND 69").fetchone()["n"], "low_priority_cases": db.execute("SELECT COUNT(*) AS n FROM cases WHERE priority_score<35").fetchone()["n"], "high_risk_cases": db.execute("SELECT COUNT(*) AS n FROM risk_assessments WHERE level IN ('high','critical')").fetchone()["n"], "total_amount_involved": str(amounts), "potential_vasp_associations": db.execute("SELECT COUNT(*) AS n FROM attributions a JOIN entities e ON e.id=a.entity_id WHERE e.type IN ('vasp','exchange')").fetchone()["n"], "related_case_count": db.execute("SELECT COUNT(*) AS n FROM case_relationships").fetchone()["n"], "recent_alert_count": db.execute("SELECT COUNT(*) AS n FROM alerts WHERE created_at>=?", ((datetime.now(timezone.utc) - timedelta(days=7)).isoformat().replace("+00:00", "Z"),)).fetchone()["n"]})

    @app.get("/api/dashboard/recent-alerts")
    def recent_alerts():
        rows = get_db().execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 10").fetchall(); return envelope([json_row(x) for x in rows])

    @app.get("/api/alerts")
    def alerts():
        db = get_db(); read_filter = request.args.get("read")
        if read_filter in ("0", "1"):
            rows = db.execute("SELECT * FROM alerts WHERE read=? ORDER BY created_at DESC", (int(read_filter),)).fetchall()
        else:
            rows = db.execute("SELECT * FROM alerts ORDER BY created_at DESC").fetchall()
        return envelope([json_row(x) for x in rows])

    @app.patch("/api/alerts/<alert_id>/read")
    def mark_alert(alert_id):
        body, error = require_json()
        if error: return error
        db = get_db(); row = db.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
        if not row: return fail("ALERT_NOT_FOUND", "Alert not found", 404)
        db.execute("UPDATE alerts SET read=? WHERE id=?", (bool(body.get("read", True)), alert_id)); db.commit(); return envelope(json_row(db.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()))

    @app.get("/api/cases/<case_id>/notes")
    def notes(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        return envelope([json_row(x) for x in get_db().execute("SELECT * FROM investigation_notes WHERE case_id=? ORDER BY created_at DESC", (case_id,)).fetchall()])

    @app.post("/api/cases/<case_id>/notes")
    def add_note(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        body, error = require_json()
        if error: return error
        if not isinstance(body.get("note"), str) or not body["note"].strip(): return fail("MISSING_FIELD", "note is required", 400)
        nid, ts = str(uuid.uuid4()), now_iso(); db = get_db(); db.execute("INSERT INTO investigation_notes (id,case_id,user_id,note,created_at,updated_at) VALUES (?,?,?,?,?,?)", (nid, case_id, body.get("user_id"), body["note"].strip(), ts, ts)); audit(case_id, "NOTE_ADDED", {"note_id": nid}); db.commit(); return envelope(json_row(db.execute("SELECT * FROM investigation_notes WHERE id=?", (nid,)).fetchone())), 201

    @app.patch("/api/notes/<note_id>")
    def edit_note(note_id):
        body, error = require_json()
        if error: return error
        if not isinstance(body.get("note"), str) or not body["note"].strip(): return fail("MISSING_FIELD", "note is required", 400)
        db = get_db(); row = db.execute("SELECT * FROM investigation_notes WHERE id=?", (note_id,)).fetchone()
        if not row: return fail("NOTE_NOT_FOUND", "Note not found", 404)
        db.execute("UPDATE investigation_notes SET note=?,updated_at=? WHERE id=?", (body["note"].strip(), now_iso(), note_id)); db.commit(); return envelope(json_row(db.execute("SELECT * FROM investigation_notes WHERE id=?", (note_id,)).fetchone()))

    @app.delete("/api/notes/<note_id>")
    def delete_note(note_id):
        db = get_db(); row = db.execute("SELECT * FROM investigation_notes WHERE id=?", (note_id,)).fetchone()
        if not row: return fail("NOTE_NOT_FOUND", "Note not found", 404)
        db.execute("DELETE FROM investigation_notes WHERE id=?", (note_id,)); db.commit(); return envelope({"deleted": True, "id": note_id})

    @app.get("/api/cases/<case_id>/audit")
    def audit_trail(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        return envelope([json_row(x) for x in get_db().execute("SELECT * FROM audit_logs WHERE case_id=? ORDER BY created_at DESC", (case_id,)).fetchall()])

    @app.get("/api/cases/<case_id>/report")
    def report(case_id):
        if not get_case(case_id): return fail("CASE_NOT_FOUND", "Case not found", 404)
        db = get_db(); audit(case_id, "REPORT_GENERATED"); db.commit(); summary_data = analysis_summary(case_id)
        report_payload = {"case": case_base(get_case(case_id)), "wallet": summary_data["wallet_address"], "transactions": [json_row(x) for x in db.execute("SELECT t.*,fw.address AS from_address,tw.address AS to_address FROM case_transactions ct JOIN transactions t ON t.id=ct.transaction_id JOIN wallets fw ON fw.id=t.from_wallet_id JOIN wallets tw ON tw.id=t.to_wallet_id WHERE ct.case_id=? ORDER BY t.hop,t.timestamp", (case_id,)).fetchall()], "timeline": [], "graph": graph_data(case_id), "risk": summary_data["risk"], "priority": summary_data["priority"], "related_cases": [json_row(x) for x in db.execute("SELECT * FROM case_relationships WHERE case_id=?", (case_id,)).fetchall()], "attribution": [json_row(x) for x in db.execute("SELECT a.*,w.address AS wallet_address,e.name AS entity_name,e.type AS entity_type FROM attributions a JOIN wallets w ON w.id=a.wallet_id LEFT JOIN entities e ON e.id=a.entity_id WHERE a.case_id=?", (case_id,)).fetchall()], "evidence": {"demo_data": True, "disclaimer": "Observable blockchain evidence is investigative context and does not establish criminal identity or ownership."}}
        db.execute("INSERT INTO investigation_reports (id,case_id,content,created_at) VALUES (?,?,?,?)", (str(uuid.uuid4()), case_id, json_text(report_payload), now_iso())); db.commit()
        return envelope(report_payload)

    @app.post("/api/demo/seed")
    def seed_demo():
        db = get_db(); created = 0; analyzed = 0; base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        fraud = ["investment_scam", "phishing", "romance_scam", "ransomware", "pig_butchering"]
        for i in range(60):
            ref = f"DEMO-{i+1:03d}"; existing = db.execute("SELECT id FROM cases WHERE case_reference=?", (ref,)).fetchone()
            if existing: cid = existing["id"]
            else:
                cid = str(uuid.uuid5(uuid.NAMESPACE_URL, "crypto-fraud-demo:" + ref)); ts = (base_time + timedelta(days=i)).isoformat().replace("+00:00", "Z"); address = stable_address("demo-wallet:" + str(i // 4))
                db.execute("INSERT INTO cases (id,case_reference,fraud_type,reported_amount,currency,reported_wallet_address,blockchain,description,status,analysis_status,priority_score,priority_factors,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (cid, ref, fraud[i % len(fraud)], str(500 + (i * 137) % 30000), "ETH", address, CHAIN, "Deterministic DEMO/TEST complaint; not real intelligence.", "new", "pending", 0, json_text({}), ts, ts)); audit(cid, "CASE_CREATED", {"demo": True}); created += 1
            result = analyze_case(cid, stable_address("demo-wallet:" + str(i // 4)), CHAIN); analyzed += 1
        db.commit(); return envelope({"created_cases": created, "analyzed_cases": analyzed, "demo": True, "message": "Deterministic demo data only; not real cybercrime intelligence."})

    with app.app_context():
        if app.config.get("TESTING") and app.config.get("DATABASE") is not None:
            init_db(app.config["DATABASE"])
        else:
            init_db()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
