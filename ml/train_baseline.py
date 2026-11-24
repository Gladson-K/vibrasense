# Train per-node healthy-baseline autoencoder + model card.
# Usage: python train_baseline.py --node NODE_ID --data ../software/vibrasense.db --healthy-days 3
# Only windows with no nearby alarm are used (healthy filter).
import argparse, hashlib, json, os, time
import numpy as np
import sqlite3
from sklearn.neural_network import MLPRegressor
import joblib
from features import FEATURES

def healthy_rows(db, node, days):
    c = sqlite3.connect(db)
    cutoff = time.time() - days*86400
    alarm_ts = [r[0] for r in c.execute(
        "SELECT ts FROM alarms WHERE node_id=? AND state='ALARM'", (node,))]
    rows = c.execute(
        "SELECT ts," + ",".join(FEATURES) +
        " FROM telemetry WHERE node_id=? AND ts>? ORDER BY ts", (node, cutoff)).fetchall()
    out = []
    for r in rows:
        if any(abs(r[0]-a) < 3600 for a in alarm_ts):   # 1h guard around alarms
            continue
        vals = [r[i] for i in range(1, 10)]
        if any(v is None for v in vals): continue
        out.append(vals)
    return np.array(out, dtype=float)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True)
    ap.add_argument("--data", default="../software/vibrasense.db")
    ap.add_argument("--healthy-days", type=int, default=3)
    ap.add_argument("--out", default="../software/ml_models")
    args = ap.parse_args()

    X = healthy_rows(args.data, args.node, args.healthy_days)
    if len(X) < 500:
        raise SystemExit("not enough healthy data: %d windows (<500)" % len(X))
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xn = (X - mu) / sd
    ae = MLPRegressor(hidden_layer_sizes=(8, 4), activation="relu", max_iter=800,
                      random_state=42, early_stopping=True)
    ae.fit(Xn, Xn)
    n = min(500, len(Xn))
    rec = ae.predict(Xn[:n])
    mse = float(np.mean((Xn[:n] - rec) ** 2))
    if mse > 0.5:
        raise SystemExit("autoencoder unhealthy reconstruction MSE=%.3f; check data" % mse)

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, "model_%s.joblib" % args.node)
    joblib.dump({"model": ae, "mu": mu, "sd": sd}, path)
    card = {
        "node": args.node, "trained_ts": time.time(),
        "samples": int(len(X)), "features": FEATURES,
        "healthy_window_days": args.healthy_days,
        "data_hash": hashlib.sha256(X.tobytes()).hexdigest()[:16],
        "healthy_mse": mse, "model": "MLPRegressor 9->8->4->8->9 (normalized)",
        "notes": "Trained on alarm-free windows only; retrain monthly or after repair.",
    }
    with open(path.replace(".joblib", ".card.json"), "w") as f:
        json.dump(card, f, indent=2)
    print("saved %s; healthy MSE=%.4f on %d windows" % (path, mse, len(X)))

if __name__ == "__main__":
    main()
