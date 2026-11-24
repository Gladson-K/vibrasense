from collections import defaultdict, deque
import json
import os
import time

import numpy as np

import db
import model_io
import paths
from validation import valid_node_id

FEATURES = ["rms_vel", "peak", "crest", "kurt", "cur_rms", "temp", "b1", "b2", "b3"]
Z_WATCH = 2.5
Z_ALERT = 4.0
ALARM_CONSEC = 3
VOTE_MIN = 3


class AlarmFSM:
    def __init__(self):
        self.state = "OK"
        self.breach_run = 0
        self.normal_since = time.time()

    def step(self, votes, alert_level):
        if alert_level >= Z_ALERT or votes >= VOTE_MIN:
            self.breach_run += 1
        elif alert_level >= Z_WATCH:
            self.breach_run = max(self.breach_run, 1)
        else:
            self.breach_run = 0
        prev = self.state
        if self.breach_run >= ALARM_CONSEC:
            self.state = "ALARM"
        elif self.breach_run >= 1:
            self.state = "WATCH"
        elif self.state != "OK" and time.time() - self.normal_since > 1800:
            self.state = "OK"
        if self.state in ("WATCH", "ALARM"):
            self.normal_since = time.time()
        return prev != self.state


class Baseline:
    def __init__(self):
        self.hist = defaultdict(lambda: deque(maxlen=10080))

    def update(self, node_id, feats):
        self.hist[node_id].append(feats)

    def zscores(self, node_id, feats):
        h = list(self.hist[node_id])
        if len(h) < 100:
            return None
        import statistics
        zs, votes = {}, 0
        for f in FEATURES:
            vals = [r.get(f) for r in h if r.get(f) is not None]
            if len(vals) < 30:
                continue
            mu, sd = statistics.mean(vals), (statistics.pstdev(vals) or 1e-9)
            z = abs((feats.get(f, mu) - mu) / sd)
            zs[f] = round(z, 2)
            if z >= Z_WATCH:
                votes += 1
        return {"z": zs, "votes": votes, "max_z": max(zs.values()) if zs else 0}


class SafeMLP:
    def __init__(self, payload):
        self.features = list(payload["features"])
        self.mu = np.asarray(payload["mu"], dtype=float)
        self.sd = np.asarray(payload["sd"], dtype=float)
        self.layers = payload["layers"]

    def predict(self, vec):
        x = np.asarray(vec, dtype=float)
        x = (x - self.mu) / self.sd
        for layer in self.layers:
            x = x @ np.asarray(layer["coefs"], dtype=float)
            x = x + np.asarray(layer["intercepts"], dtype=float)
            if layer.get("activation") == "relu":
                x = np.maximum(x, 0.0)
        return x


class Scorer:
    def __init__(self):
        self.baseline = Baseline()
        self.fsm = defaultdict(AlarmFSM)
        self.aes = {}

    def load_autoencoders(self, model_dir=None):
        directory = paths.model_dir() if model_dir is None else os.fspath(model_dir)
        if not os.path.isdir(directory):
            return
        for name in sorted(os.listdir(directory)):
            if not name.endswith(".json") or name.endswith(".sha256"):
                continue
            payload = model_io.load_verified_artifact(os.path.join(directory, name))
            if payload.get("features") != FEATURES:
                raise ValueError("model feature list mismatch")
            node = payload.get("node") or name[:-5].replace("model_", "")
            self.aes[node] = SafeMLP(payload)

    def on_telemetry(self, node_id, d):
        if not valid_node_id(node_id):
            return
        zs = self.baseline.zscores(node_id, d)
        self.baseline.update(node_id, d)
        if zs is None:
            return
        reason = "max|z|=%.2f votes=%d/9" % (zs["max_z"], zs["votes"])
        if node_id in self.aes:
            vec = np.array([[d.get(f, 0.0) or 0.0 for f in FEATURES]], dtype=float)
            ae = self.aes[node_id]
            recon = ae.predict(vec)
            mse = float(np.mean((vec - recon) ** 2))
            reason += " ae_mse=%.4f" % mse
        fsm = self.fsm[node_id]
        if fsm.step(zs["votes"], zs["max_z"]):
            db.add_alarm(node_id, fsm.state, reason, json.dumps({"z": zs["z"]}))
