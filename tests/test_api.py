import uuid

import pytest

pytest.importorskip("flask")

import db
from app import app


def test_health():
    c = app.test_client()
    r = c.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["db"] is True


def test_machines_and_alarms():
    node = "test-" + uuid.uuid4().hex[:8]
    c = app.test_client()
    db.upsert_node(node)
    r = c.get("/api/machines")
    assert any(m["node_id"] == node for m in r.get_json())
    db.add_alarm(node, "WATCH", "unit-test", "{}")
    r = c.get("/api/alarms")
    item = next(a for a in r.get_json() if a["node_id"] == node)
    assert c.post(f"/api/alarms/{item['id']}/ack").get_json()["ok"] is True


def test_telemetry_roundtrip():
    node = "tele-" + uuid.uuid4().hex[:8]
    c = app.test_client()
    db.insert_telemetry(node, 1.0, {"rms_vel": 1.1, "peak": 2.2, "crest": 2.0,
                                   "kurt": 3.0, "cur_rms": 4.4, "temp": 41.0,
                                   "b1": 0.0, "b2": 0.0, "b3": 0.0})
    r = c.get(f"/api/telemetry?node={node}&minutes=10080")
    rows = r.get_json()
    assert any(row["rms_vel"] == 1.1 for row in rows)


def test_invalid_inputs_are_rejected():
    c = app.test_client()
    assert c.get("/api/telemetry?node=../etc").status_code == 400
    assert c.get("/api/alarms?ack=maybe").status_code == 400
    assert c.post("/api/models/retrain", json={"node": "../etc"}).status_code == 400


def test_dashboard_uses_text_content():
    body = app.test_client().get("/").get_data(as_text=True)
    assert "innerHTML" not in body
    assert "textContent" in body
