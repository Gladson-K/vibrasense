# Replay recorded telemetry through the scoring logic; report detection latency.
# Usage: python backtest.py --node X --fault-at 2026-11-10T08:00:00 --data ../software/vibrasense.db
import argparse, sys, time, sqlite3
sys.path.insert(0, "../software")
from models import Baseline, AlarmFSM, FEATURES

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True)
    ap.add_argument("--fault-at", required=True, help="YYYY-MM-DDTHH:MM:SS (UTC)")
    ap.add_argument("--data", default="../software/vibrasense.db")
    args = ap.parse_args()
    fault_ts = time.mktime(time.strptime(args.fault_at, "%Y-%m-%dT%H:%M:%S"))

    c = sqlite3.connect(args.data)
    rows = c.execute("SELECT ts," + ",".join(FEATURES) +
                     " FROM telemetry WHERE node_id=? ORDER BY ts", (args.node,)).fetchall()
    base = Baseline(); fsm = AlarmFSM(); detected = None
    for r in rows:
        d = {f: r[i+1] for i, f in enumerate(FEATURES)}
        zs = base.zscores(args.node, d)
        base.update(args.node, d)
        if zs:
            fsm.step(zs["votes"], zs["max_z"])
        if fsm.state == "ALARM" and detected is None and r[0] > fault_ts:
            detected = r[0]
    if detected:
        print("ALARM detected at %s, latency after fault: %.1f h" %
              (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(detected)),
               (detected - fault_ts)/3600))
    else:
        print("no alarm raised after fault time - FAIL")

if __name__ == "__main__":
    main()
