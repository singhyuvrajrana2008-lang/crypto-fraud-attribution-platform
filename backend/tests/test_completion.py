import sqlite3

import pytest

from backend.app import create_app


@pytest.fixture()
def client():
    database = sqlite3.connect(":memory:")
    app = create_app({"TESTING": True, "DATABASE": database})
    with app.test_client() as test_client:
        yield test_client
    database.close()


def data(response):
    payload = response.get_json()
    assert payload["success"] is True, payload
    return payload["data"]


def test_complete_mvp_workflow(client):
    seeded = data(client.post("/api/demo/seed"))
    assert seeded["created_cases"] == 60
    assert seeded["analyzed_cases"] == 60

    summary = data(client.get("/api/dashboard/summary"))
    assert summary["total_cases"] == 60
    assert summary["potential_vasp_associations"] == 60

    listing = data(client.get("/api/cases?search=DEMO-001&risk_level=high&limit=10"))
    assert listing["total"] >= 1
    top = data(client.get("/api/cases/top-priority?limit=10"))
    assert len(top) == 10
    assert all(top[i]["priority_score"] >= top[i + 1]["priority_score"] for i in range(len(top) - 1))

    case_id = top[0]["case_id"]
    detail = data(client.get(f"/api/cases/{case_id}"))
    assert detail["priority"]["priority_score"] == detail["priority_score"]
    assert detail["transaction_count"] == 2
    assert detail["hop_count"] == 2

    assert len(data(client.get(f"/api/cases/{case_id}/related"))) >= 1
    assert len(data(client.get(f"/api/cases/{case_id}/transactions"))["items"]) == 2
    assert len(data(client.get(f"/api/cases/{case_id}/graph"))["edges"]) == 2
    assert data(client.get(f"/api/cases/{case_id}/risk"))["indicators"]
    assert data(client.get(f"/api/cases/{case_id}/attribution"))[0]["entity_type"] == "vasp"

    note = data(client.post(f"/api/cases/{case_id}/notes", json={"note": "Review evidence."}))
    updated = data(client.patch(f"/api/notes/{note['id']}", json={"note": "Review evidence and escalate."}))
    assert updated["note"].startswith("Review evidence")
    assert client.patch(f"/api/cases/{case_id}/status", json={"status": "under_review"}).status_code == 200
    report = data(client.get(f"/api/cases/{case_id}/report"))
    assert report["evidence"]["demo_data"] is True
    audit = data(client.get(f"/api/cases/{case_id}/audit"))
    assert {entry["action"] for entry in audit} >= {"CASE_CREATED", "ANALYSIS_COMPLETED", "NOTE_ADDED", "STATUS_CHANGED", "REPORT_GENERATED"}


def test_seed_is_idempotent_and_alerts_are_readable(client):
    data(client.post("/api/demo/seed"))
    second = data(client.post("/api/demo/seed"))
    assert second["created_cases"] == 0
    alerts = data(client.get("/api/alerts"))
    assert alerts
    alert_id = alerts[0]["id"]
    assert data(client.patch(f"/api/alerts/{alert_id}/read", json={"read": True}))["read"] in (True, 1)
    assert data(client.get("/api/alerts?read=1"))


def test_linked_cases_recalculate_priority_and_delete(client):
    wallet = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    first = data(client.post("/api/cases", json={"case_reference": "LINK-001", "fraud_type": "investment_scam", "reported_amount": "1000", "reported_wallet_address": wallet, "blockchain": "ethereum"}))
    first_id = first["id"]
    data(client.post("/api/investigations/analyze", json={"case_id": first_id, "wallet_address": wallet, "chain": "ethereum"}))
    before = data(client.get(f"/api/cases/{first_id}/priority"))["priority_score"]

    second = data(client.post("/api/cases", json={"case_reference": "LINK-002", "fraud_type": "phishing", "reported_amount": "1000", "reported_wallet_address": wallet, "blockchain": "ethereum"}))
    second_id = second["id"]
    data(client.post("/api/investigations/analyze", json={"case_id": second_id, "wallet_address": wallet, "chain": "ethereum"}))
    after = data(client.get(f"/api/cases/{first_id}/priority"))
    assert after["priority_factors"]["linked_cases"] >= 25
    assert after["priority_score"] > before

    deleted = data(client.delete(f"/api/cases/{second_id}"))
    assert deleted["case_id"] == second_id
    assert deleted["deleted"] is True
    assert first_id in deleted["recalculated_case_ids"]
    assert client.get(f"/api/cases/{second_id}").status_code == 404
    assert data(client.get(f"/api/cases/{first_id}/priority"))["priority_factors"]["linked_cases"] == 0
    assert client.get(f"/api/cases/{first_id}/audit").status_code == 200
