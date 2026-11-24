import json
import os
import subprocess
import sys
import time
from functools import wraps

from flask import Flask, Response, jsonify, render_template_string, request

import alerts
import audit
import auth
import db
import fleet
import i18n
import models
import paths
import snmp
from validation import valid_node_id

ROOT = paths.project_root()
if str(ROOT / "ml") not in sys.path:
    sys.path.insert(0, str(ROOT / "ml"))

from high_freq import bearing_frequencies

app = Flask(__name__)
scorer = models.Scorer()
alert_router = alerts.AlertRouter([alerts.MemoryTransport()])

INDEX = """
<!doctype html><title>{{ title }}</title>
<h1>{{ title }}</h1>
<label>Language
<select id="lang">
{% for language in languages %}<option value="{{ language }}">{{ language }}</option>{% endfor %}
</select>
</label>
<div id="machines">connecting...</div>
<h2>Alarms</h2><ul id="alarms"></ul>
<script>
const lang = new URLSearchParams(location.search).get("lang") || "en";
document.getElementById("lang").value = lang;
document.getElementById("lang").addEventListener("change", e => {
  location.search = "?lang=" + e.target.value;
});
function renderMachines(machines) {
  const root = document.getElementById("machines");
  root.replaceChildren();
  machines.forEach(m => {
    const line = document.createElement("div");
    const name = document.createElement("b");
    name.textContent = m.node_id;
    line.append(name, document.createTextNode(" " + m.status + " last seen: " + new Date(m.last_seen*1000).toLocaleTimeString()));
    root.appendChild(line);
  });
}
function renderAlarms(alarms) {
  const root = document.getElementById("alarms");
  root.replaceChildren();
  alarms.forEach(a => {
    const item = document.createElement("li");
    item.textContent = a.node_id + " [" + a.state + "] " + a.reason + " - " + new Date(a.ts*1000).toLocaleString();
    root.appendChild(item);
  });
}
const es = new EventSource("/stream");
es.onmessage = e => {
  const d = JSON.parse(e.data);
  renderMachines(d.machines);
  renderAlarms(d.alarms);
};
</script>
"""


def current_role():
    if os.environ.get("VIBRASENSE_AUTH_ENABLED", "0") != "1":
        return "admin"
    return auth.role_from_headers(request.headers, default=os.environ.get("VIBRASENSE_ROLE", "viewer"))


def require(action):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            role = current_role()
            if not auth.allowed(role, action):
                audit.append(role, action, request.path, "denied")
                return jsonify({"error": "forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapped
    return decorator


@app.route("/")
def index():
    language = request.args.get("lang", "en")
    return render_template_string(
        INDEX,
        title=i18n.translate(language, "dashboard_title"),
        languages=i18n.available_languages(),
    )


@app.route("/api/i18n/<language>")
def api_i18n(language):
    return jsonify(i18n.load(language))


@app.route("/api/machines")
@require("read")
def api_machines():
    return jsonify(db.machines())


@app.route("/api/telemetry")
@require("read")
def api_telemetry():
    node = request.args.get("node")
    if not valid_node_id(node):
        return jsonify({"error": "invalid node"}), 400
    try:
        minutes = int(request.args.get("minutes", 60))
    except ValueError:
        return jsonify({"error": "invalid minutes"}), 400
    if not 1 <= minutes <= 10080:
        return jsonify({"error": "minutes out of range"}), 400
    return jsonify(db.recent(node, minutes))


@app.route("/api/alarms")
@require("read")
def api_alarms():
    ack = request.args.get("ack")
    if ack is not None:
        if ack not in ("0", "1"):
            return jsonify({"error": "invalid ack"}), 400
        ack = int(ack)
    return jsonify(db.list_alarms(ack))


@app.route("/api/alarms/<int:aid>/ack", methods=["POST"])
@require("ack")
def api_ack(aid):
    db.conn().execute("UPDATE alarms SET ack=1 WHERE id=?", (aid,))
    db.conn().commit()
    audit.append(current_role(), "ack", str(aid))
    return jsonify({"ok": True})


@app.route("/api/models/retrain", methods=["POST"])
@require("retrain")
def api_retrain():
    payload = request.get_json(silent=True) or {}
    node = payload.get("node", "ALL")
    if node == "ALL":
        nodes = [m["node_id"] for m in db.machines()]
    elif valid_node_id(node):
        nodes = [node]
    else:
        return jsonify({"error": "invalid node"}), 400
    script = ROOT / "ml" / "train_baseline.py"
    logs = []
    ok = True
    for item in nodes:
        result = subprocess.run(
            [sys.executable, str(script), "--node", item],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        ok = ok and result.returncode == 0
        logs.append((result.stdout + result.stderr)[-2000:])
    audit.append(current_role(), "retrain", node, "ok" if ok else "failed")
    return jsonify({"ok": ok, "log": "\n".join(logs)}), 200 if ok else 500


@app.route("/api/health")
@require("read")
def api_health():
    return jsonify({
        "db": True,
        "time": time.time(),
        "nodes": len(db.machines()),
        "models_loaded": sorted(scorer.aes.keys()),
        "languages": i18n.available_languages(),
    })


@app.route("/api/bearing-frequencies")
@require("read")
def api_bearing_frequencies():
    try:
        rpm = float(request.args["rpm"])
        ball_dia = float(request.args["ball_dia_mm"])
        pitch_dia = float(request.args["pitch_dia_mm"])
        balls = int(request.args["balls"])
        angle = float(request.args.get("contact_angle_deg", 0))
    except (KeyError, ValueError):
        return jsonify({"error": "invalid bearing parameters"}), 400
    try:
        return jsonify(bearing_frequencies(rpm, ball_dia, pitch_dia, balls, angle))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/fleet/import", methods=["POST"])
@require("onboard")
def api_fleet_import():
    payload = request.get_json(silent=True) or {}
    text = payload.get("csv") or request.get_data(as_text=True)
    try:
        rows = fleet.parse_csv(text)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    for row in rows:
        db.upsert_node(row["node_id"])
    audit.append(current_role(), "fleet_import", "%d nodes" % len(rows))
    return jsonify({
        "imported": len(rows),
        "hierarchy": fleet.hierarchy(rows),
        "qr": {row["node_id"]: fleet.qr_payload(row["node_id"]) for row in rows},
    })


@app.route("/api/alerts/test", methods=["POST"])
@require("manage_users")
def api_alert_test():
    payload = request.get_json(silent=True) or {}
    node = payload.get("node")
    state = payload.get("state", "WATCH")
    reason = payload.get("reason", "manual test")
    language = payload.get("language", "en")
    if not valid_node_id(node) or state not in snmp.SEVERITY_CODE:
        return jsonify({"error": "invalid alert parameters"}), 400
    ok = alert_router.publish(node, state, reason, language=language)
    audit.append(current_role(), "alert_test", node, "ok" if ok else "failed")
    return jsonify({"ok": ok, "messages": len(alert_router.transports[0].messages)})


@app.route("/api/snmp/trap")
@require("read")
def api_snmp_trap():
    node = request.args.get("node")
    state = request.args.get("state", "OK")
    if not valid_node_id(node) or state not in snmp.SEVERITY_CODE:
        return jsonify({"error": "invalid trap parameters"}), 400
    return jsonify(snmp.health_trap(node, state))


@app.route("/stream")
@require("read")
def stream():
    def gen():
        while True:
            try:
                yield "data: " + json.dumps({"machines": db.machines(), "alarms": db.list_alarms()}) + "\n\n"
            except Exception:
                pass
            time.sleep(2)
    return Response(gen(), mimetype="text/event-stream")


if __name__ == "__main__":
    import ingest
    scorer.load_autoencoders()
    broker = os.environ.get("MQTT_BROKER", "127.0.0.1")
    ing = ingest.Ingestor(broker=broker, on_telemetry=scorer.on_telemetry)
    ing.start()
    app.run(host=os.environ.get("VIBRASENSE_HOST", "127.0.0.1"), port=5000, threaded=True)
