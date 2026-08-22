import sqlite3
from pathlib import Path

import pytest

from backend.app import create_app


@pytest.fixture()
def client(tmp_path):
    database = sqlite3.connect(":memory:")
    app = create_app({"TESTING": True, "DATABASE": database})
    with app.test_client() as test_client:
        yield test_client
    database.close()


def assert_envelope(payload, success=True):
    assert payload["success"] is success
    assert (payload["data"] is not None) == success
    assert (payload["error"] is None) == success


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert_envelope(response.get_json())
    assert response.get_json()["data"] == {"status": "ok"}


def test_case_creation_and_validation(client):
    missing = client.post("/api/cases", json={})
    assert missing.status_code == 400
    assert missing.get_json()["error"]["code"] == "MISSING_FIELD"

    response = client.post("/api/cases", json={"case_reference": "TEST-001", "fraud_type": "investment_scam", "description": "Demo"})
    assert response.status_code == 201
    payload = response.get_json()
    assert_envelope(payload)
    assert payload["data"]["case_reference"] == "TEST-001"
    assert isinstance(payload["data"]["id"], str)


def test_analysis_and_read_models(client):
    case = client.post("/api/cases", json={"case_reference": "TEST-002", "fraud_type": "investment_scam"}).get_json()["data"]
    bad_wallet = client.post("/api/investigations/analyze", json={"case_id": case["id"], "wallet_address": "bad", "chain": "ethereum"})
    assert bad_wallet.status_code == 400
    assert bad_wallet.get_json()["error"]["code"] == "INVALID_WALLET_ADDRESS"

    address = "0x" + "3" * 40
    response = client.post("/api/investigations/analyze", json={"case_id": case["id"], "wallet_address": address, "chain": "ethereum"})
    assert response.status_code == 200
    result = response.get_json()["data"]
    assert result["wallet"]["address"] == address
    assert result["analysis"]["transaction_count"] == 2
    assert result["risk"]["level"] == "high"
    assert result["attribution"]["entity_type"] == "vasp"

    transactions = client.get(f"/api/cases/{case['id']}/transactions").get_json()["data"]
    assert len(transactions["items"]) == 2
    assert isinstance(transactions["items"][0]["amount"], str)
    assert transactions["items"][0]["from_address"] == address

    graph = client.get(f"/api/cases/{case['id']}/graph").get_json()["data"]
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2
    assert all(edge["id"].startswith("edge_") for edge in graph["edges"])

    attribution = client.get(f"/api/cases/{case['id']}/attribution").get_json()["data"]
    assert attribution[0]["match_type"] == "known_address"
    assert 0 <= attribution[0]["confidence"] <= 1

    risk = client.get(f"/api/cases/{case['id']}/risk").get_json()["data"]
    assert risk["score"] == 87
    assert risk["indicators"][0]["code"] == "MULTI_HOP"

    report = client.get(f"/api/cases/{case['id']}/report").get_json()["data"]
    assert report["case"]["id"] == case["id"]
    assert "graph" in report


def test_missing_case_is_consistent(client):
    response = client.get("/api/cases/550e8400-e29b-41d4-a716-446655440000")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "CASE_NOT_FOUND"
