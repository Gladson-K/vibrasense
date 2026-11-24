import os, sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "software"))
os.chdir(os.path.join(os.path.dirname(__file__), "..", "software"))
import db
db.conn()  # create schema
from app import app

def test_health():
    c = app.test_client()
    r = c.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["db"] is True

def test_machines_and_alarms():
    c = app.test_client()
    db.upsert_node("test-node")
    r = c.get("/api/machines")
    assert any(m["node_id"] == "test-node" for m in r.get_json())
    db.add_alarm("test-node", "WATCH", "unit-test", "{}")
    r = c.get("/api/alarms")
    assert len(r.get_json()) >= 1
    aid = r.get_json()[0]["id"]
    assert c.post(f"/api/alarms/{aid}/ack").get_json()["ok"] is True

def test_telemetry_roundtrip():
    c = app.test_client()
    ts = time.time()
    db.insert_telemetry("test-node", ts, {"rms_vel": 1.1, "peak": 2.2, "crest": 2.0,
                       "kurt": 3.0, "cur_rms": 4.4, "temp": 41.0, "b1": 0, "b2": 0, "b3": 0})
    r = c.get("/api/telemetry?node=test-node&minutes=5")
    rows = r.get_json()
    assert any(row["rms_vel"] == 1.1 for row in rows)
