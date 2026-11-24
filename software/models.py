from collections import defaultdict, deque
import json, time
import db

FEATURES = ["rms_vel", "peak", "crest", "kurt", "cur_rms", "temp", "b1", "b2", "b3"]
Z_WATCH = 2.5
Z_ALERT = 4.0
ALARM_CONSEC = 3
VOTE_MIN = 3

class AlarmFSM:
    # OK -> WATCH -> ALARM; auto-clear after 30 min normal.
    def __init__(self):
        self.state = "OK"
        self.breach_run = 0
        self.normal_since = time.time()

    def step(self, votes, alert_level):
        if alert_level >= Z_ALERT or votes >= VOTE_MIN:
            self.breach_run += 1
        elif alert_level >= Z_WATCH:
            self.breach_run = max(self.breach_run, 1)  # stay warm
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
    # Per-node rolling healthy-window mean/std -> z-scores.
    def __init__(self):
        self.hist = defaultdict(lambda: deque(maxlen=10080))  # 7d @ 10s

    def update(self, node_id, feats):
        self.hist[node_id].append(feats)

    def zscores(self, node_id, feats):
        h = list(self.hist[node_id])
        if len(h) < 100:  # < ~20 min: learning
            return None
        import statistics
        zs, votes = {}, 0
        for f in FEATURES:
            vals = [r.get(f) for r in h if r.get(f) is not None]
            if len(vals) < 30: continue
            mu, sd = statistics.mean(vals), (statistics.pstdev(vals) or 1e-9)
            z = abs((feats.get(f, mu) - mu) / sd)
            zs[f] = round(z, 2)
            if z >= Z_WATCH: votes += 1
        return {"z": zs, "votes": votes, "max_z": max(zs.values()) if zs else 0}

class Scorer:
    # Combines baseline z-scores + optional autoencoder MSE -> FSM transitions.
    def __init__(self):
        self.baseline = Baseline()
        self.fsm = defaultdict(AlarmFSM)
        self.aes = {}

    def load_autoencoders(self, model_dir="ml_models"):
        import os, joblib
        if os.path.isdir(model_dir):
            for f in os.listdir(model_dir):
                if f.endswith(".joblib"):
                    node = f[:-7].replace("model_", "")
                    self.aes[node] = joblib.load(os.path.join(model_dir, f))

    def on_telemetry(self, node_id, d):
        zs = self.baseline.zscores(node_id, d)
        self.baseline.update(node_id, d)
        if zs is None:
            return
        reason = "max|z|=%.2f votes=%d/9" % (zs["max_z"], zs["votes"])
        if node_id in self.aes:
            import numpy as np
            blob = self.aes[node_id]
            mu, sd, ae = blob["mu"], blob["sd"], blob["model"]
            vec = (np.array([[d.get(f, 0.0) or 0.0 for f in FEATURES]]) - mu) / sd
            mse = float(np.mean((vec - ae.predict(vec)) ** 2))
            reason += " ae_mse=%.4f" % mse
        fsm = self.fsm[node_id]
        if fsm.step(zs["votes"], zs["max_z"]):
            db.add_alarm(node_id, fsm.state, reason, json.dumps({"z": zs["z"]}))
