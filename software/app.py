import json
import os
import subprocess
import sys
import time

from flask import Flask, Response, jsonify, render_template_string, request

import db
import models
import paths
from validation import valid_node_id

ROOT = paths.project_root()
if str(ROOT / "ml") not in sys.path:
    sys.path.insert(0, str(ROOT / "ml"))

from high_freq import bearing_frequencies

app = Flask(__name__)
scorer = models.Scorer()

INDEX = """
<!doctype html><title>VibraSense</title>
<h1>VibraSense Dashboard v1</h1>
<div id="machines">connecting...</div>
<h2>Alarms</h2><ul id="alarms"></ul>
<script>
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


@app.route("/")
def index():
    return render_template_string(INDEX)


@app.route("/api/machines")
def api_machines():
    return jsonify(db.machines())


@app.route("/api/telemetry")
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
def api_alarms():
    ack = request.args.get("ack")
    if ack is not None:
        if ack not in ("0", "1"):
            return jsonify({"error": "invalid ack"}), 400
        ack = int(ack)
    return jsonify(db.list_alarms(ack))


@app.route("/api/alarms/<int:aid>/ack", methods=["POST"])
def api_ack(aid):
    db.conn().execute("UPDATE alarms SET ack=1 WHERE id=?", (aid,))
    db.conn().commit()
    return jsonify({"ok": True})


@app.route("/api/models/retrain", methods=["POST"])
def api_retrain():
    payload = request.get_json(silent=True) or {}
    node = payload.get("node", "ALL")
    if node == "ALL":
        nodes = [m["node_id"] for m in db.machines()]
    elif valid_node_id(node):
        nodes = [node]
    else:
        return jsonify({"error": "invalid node"}), 400
    root = paths.project_root()
    script = root / "ml" / "train_baseline.py"
    logs = []
    ok = True
    for item in nodes:
        result = subprocess.run(
            [sys.executable, str(script), "--node", item],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        ok = ok and result.returncode == 0
        logs.append((result.stdout + result.stderr)[-2000:])
    return jsonify({"ok": ok, "log": "\n".join(logs)}), 200 if ok else 500


@app.route("/api/health")
def api_health():
    return jsonify({
        "db": True,
        "time": time.time(),
        "nodes": len(db.machines()),
        "models_loaded": sorted(scorer.aes.keys()),
    })


@app.route("/api/bearing-frequencies")
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


@app.route("/stream")
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
