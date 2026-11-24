import i18n
from alerts import AlertRouter, MemoryTransport
from auth import allowed, role_from_headers
from audit import append, read_all
from fleet import hierarchy, parse_csv, qr_payload
from snmp import health_trap


class Headers:
    def __init__(self, values):
        self.values = values

    def get(self, key, default=None):
        return self.values.get(key, default)


def test_i18n_catalogs():
    assert set(i18n.available_languages()) == {"en", "es", "hi", "pt"}
    assert i18n.translate("en", "dashboard_title") == "VibraSense Dashboard"
    assert i18n.translate("es", "dashboard_title") != "VibraSense Dashboard"
    assert i18n.translate("missing", "dashboard_title") == "VibraSense Dashboard"


def test_rbac_matrix():
    assert allowed("viewer", "read")
    assert not allowed("viewer", "ack")
    assert allowed("technician", "ack")
    assert allowed("admin", "manage_users")
    assert role_from_headers(Headers({"X-Role": "technician"}), "viewer") == "technician"
    assert role_from_headers(Headers({"X-Role": "unknown"}), "viewer") == "viewer"


def test_audit_append_and_read(tmp_path, monkeypatch):
    target = tmp_path / "audit.jsonl"
    monkeypatch.setenv("VIBRASENSE_AUDIT_LOG", str(target))
    append("tester", "ack", "42")
    records = read_all(target)
    assert records[0]["actor"] == "tester"
    assert records[0]["target"] == "42"


def test_fleet_csv_import():
    text = "node_id,name,site,machine_class\nnode-a,Press 1,Plant A,Press\nnode-b,Fan 2,Plant A,Fan\n"
    rows = parse_csv(text)
    assert len(rows) == 2
    assert hierarchy(rows)["Plant A"]["Press"] == ["node-a"]
    assert qr_payload("node-a") == "vs://node/node-a"


def test_fleet_csv_rejects_bad_data():
    text = "node_id,name,site,machine_class\n../bad,Press 1,Plant A,Press\n"
    try:
        parse_csv(text)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid node id was accepted")


def test_local_alert_transport():
    transport = MemoryTransport()
    router = AlertRouter([transport])
    assert router.publish("node-a", "WATCH", "high vibration", language="en")
    assert "node-a" in transport.messages[0]["subject"]


def test_snmp_trap_representation():
    trap = health_trap("node-a", "ALARM")
    assert trap["oid"].endswith(".1.0")
    assert trap["severity_code"] == 2
