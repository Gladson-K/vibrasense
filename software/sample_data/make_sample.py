# Generate a synthetic demo dataset: 3 days healthy + outer-race fault onset,
# inserted directly into vibrasense.db so dashboard/ML/backtest work out of the box.
import sys, os, time, sqlite3
import numpy as np
sys.path.insert(0, "../../ml")
sys.path.insert(0, "..")
from features import window_features, band_energies, FEATURES
import db

def synth_window(rng, fault_level, rpm=1200):
    t = np.arange(1000) / 1000.0
    f_shaft = rpm / 60.0
    mag = 1.0 + 0.03*np.sin(2*np.pi*f_shaft*t)
    if fault_level > 0:
        bpfo = 4.5 * f_shaft                     # outer-race ball pass freq
        mag += fault_level * np.sin(2*np.pi*bpfo*t) * (1 + 0.3*np.sin(2*np.pi*2*t))
    mag += 0.02 * rng.standard_normal(1000)
    amps = 4.0 + 0.2*np.sin(2*np.pi*t) + 0.1*rng.standard_normal(1000)
    if fault_level > 0:
        amps += fault_level * 1.5 * np.abs(np.sin(2*np.pi*bpfo*t))
    temp = 45.0 + fault_level * 6.0 + rng.normal(0, 0.3)
    return mag, amps, temp

def main(node="demo-mill-01", days_healthy=3):
    rng = np.random.default_rng(42)
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    db.conn()
    db.upsert_node(node)
    now = time.time()
    start = now - (days_healthy*86400 + 86400)   # healthy period + 1 fault day
    fault_at = start + days_healthy*86400
    ts = start
    while ts < now:
        hours_in = (ts - fault_at) / 3600.0
        level = 0.0 if hours_in < 0 else min(0.08, hours_in * 0.004)
        mag, amps, temp = synth_window(rng, level)
        f = window_features(mag, amps, temp)
        b = band_energies(mag)
        f.update({"b1": b[0], "b2": b[1], "b3": b[2]})
        db.insert_telemetry(node, ts, f)
        ts += 10
    print("inserted demo data for", node, "fault onset at",
          time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(fault_at)))
    print("run backtest: python ../../ml/backtest.py --node %s --fault-at %s" %
          (node, time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(fault_at))))

if __name__ == "__main__":
    main()
