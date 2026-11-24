import argparse
import hashlib
import os
import sqlite3
import sys
import time

import numpy as np
from sklearn.neural_network import MLPRegressor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ml"))
sys.path.insert(0, os.path.join(ROOT, "software"))

from features import FEATURES
from model_io import write_artifact
from paths import database_path


def healthy_rows(db_path, node, days):
    c = sqlite3.connect(str(db_path))
    cutoff = time.time() - days * 86400
    alarm_ts = [r[0] for r in c.execute(
        "SELECT ts FROM alarms WHERE node_id=? AND state='ALARM'", (node,))]
    rows = c.execute(
        "SELECT ts," + ",".join(FEATURES) +
        " FROM telemetry WHERE node_id=? AND ts>? ORDER BY ts", (node, cutoff)).fetchall()
    out = []
    for r in rows:
        if any(abs(r[0] - a) < 3600 for a in alarm_ts):
            continue
        vals = [r[i] for i in range(1, 10)]
        if any(v is None for v in vals):
            continue
        out.append(vals)
    return np.array(out, dtype=float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True)
    ap.add_argument("--data", default=None)
    ap.add_argument("--healthy-days", type=int, default=3)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    db_path = os.fspath(database_path()) if args.data is None else args.data
    out_dir = os.path.join(ROOT, "software", "ml_models") if args.out is None else args.out

    X = healthy_rows(db_path, args.node, args.healthy_days)
    if len(X) < 500:
        raise SystemExit("not enough healthy data: %d windows (<500)" % len(X))
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xn = (X - mu) / sd
    ae = MLPRegressor(
        hidden_layer_sizes=(8, 4),
        activation="relu",
        max_iter=800,
        random_state=42,
        early_stopping=True,
    )
    ae.fit(Xn, Xn)
    n = min(500, len(Xn))
    rec = ae.predict(Xn[:n])
    mse = float(np.mean((Xn[:n] - rec) ** 2))
    if mse > 0.5:
        raise SystemExit("autoencoder reconstruction MSE=%.3f; check data" % mse)

    layers = []
    for coefs, intercepts in zip(ae.coefs_, ae.intercepts_):
        layers.append({
            "coefs": np.asarray(coefs).tolist(),
            "intercepts": np.asarray(intercepts).tolist(),
            "activation": "relu",
        })
    layers[-1]["activation"] = "linear"
    payload = {
        "node": args.node,
        "features": FEATURES,
        "mu": mu.tolist(),
        "sd": sd.tolist(),
        "layers": layers,
        "trained_ts": time.time(),
        "samples": int(len(X)),
        "healthy_window_days": args.healthy_days,
        "data_hash": hashlib.sha256(X.tobytes()).hexdigest(),
        "healthy_mse": mse,
        "model": "MLPRegressor 9->8->4->9 (normalized)",
        "notes": "Advisory only; retrain monthly or after repair.",
    }
    path = os.path.join(out_dir, "model_%s.json" % args.node)
    digest = write_artifact(path, payload)
    print("saved %s sha256=%s healthy MSE=%.4f on %d windows" % (path, digest, mse, len(X)))


if __name__ == "__main__":
    main()
