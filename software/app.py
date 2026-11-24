import json, time, threading, queue, subprocess, sys
from flask import Flask, jsonify, request, Response, render_template_string
import db, ingest, models

app = Flask(__name__)
scorer = models.Scorer()

INDEX = """
<!doctype html><title>VibraSense</title>
<h1>VibraSense Dashboard v1</h1>
<div id="machines">connecting...</div>
<h2>Alarms</h2><ul id="alarms"></ul>
<script>
const es = new EventSource("/stream");
es.onmessage = e => {
  const d = JSON.parse(e.data);
  document.getElementById("machines").innerHTML =
    d.machines.map(m => `<b>${m.node_id}</b> ${m.status} last seen: ${new Date(m.last_seen*1000).toLocaleTimeString()}`).join("<br>");
  document.getElementById("alarms").innerHTML =
    d.alarms.map(a => `<li>${a.node_id} [${a.state}] ${a.reason} — ${new Date(a.ts*1000).toLocaleString()}</li>`).join("");
};
</script>
"""

@app.route("/")
def index(): return render_template_string(INDEX)

@app.route("/api/machines")
def api_machines(): return jsonify(db.machines())

@app.route("/api/telemetry")
def api_telemetry():
    node = request.args.get("node"); minutes = int(request.args.get("minutes", 60))
    return jsonify(db.recent(node, minutes))

@app.route("/api/alarms")
def api_alarms(): return jsonify(db.list_alarms(request.args.get("ack")))

@app.route("/api/alarms/<int:aid>/ack", methods=["POST"])
def api_ack(aid):
    db.conn().execute("UPDATE alarms SET ack=1 WHERE id=?", (aid,)); db.conn().commit()
    return jsonify({"ok": True})

@app.route("/api/models/retrain", methods=["POST"])
def api_retrain():
    node = (request.json or {}).get("node", "ALL")
    r = subprocess.run([sys.executable, "ml/train_baseline.py", "--node", node],
                       capture_output=True, text=True, cwd="..")
    return jsonify({"ok": r.returncode == 0, "log": r.stdout[-2000:] + r.stderr[-2000:]})

@app.route("/api/health")
def api_health():
    return jsonify({"db": True, "time": time.time(),
                    "nodes": len(db.machines()),
                    "models_loaded": list(scorer.aes.keys())})

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
    ing = ingest.Ingestor(on_telemetry=scorer.on_telemetry)
    scorer.load_autoencoders()
    ing.start()
    app.run(host="0.0.0.0", port=5000, threaded=True)
