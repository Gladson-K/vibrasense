import argparse
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "software"))
sys.path.insert(0, os.path.join(ROOT, "ml"))

from models import FEATURES, AlarmFSM, Baseline
from paths import database_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True)
    ap.add_argument("--fault-at", required=True, help="YYYY-MM-DDTHH:MM:SS UTC")
    ap.add_argument("--data", default=None)
    args = ap.parse_args()
    fault_ts = datetime.strptime(args.fault_at, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
    db_path = os.fspath(database_path()) if args.data is None else args.data

    c = sqlite3.connect(db_path)
    rows = c.execute("SELECT ts," + ",".join(FEATURES) +
                     " FROM telemetry WHERE node_id=? ORDER BY ts", (args.node,)).fetchall()
    base = Baseline()
    fsm = AlarmFSM()
    detected = None
    for r in rows:
        d = {f: r[i + 1] for i, f in enumerate(FEATURES)}
        zs = base.zscores(args.node, d)
        base.update(args.node, d)
        if zs:
            fsm.step(zs["votes"], zs["max_z"])
        if fsm.state == "ALARM" and detected is None and r[0] > fault_ts:
            detected = r[0]
    if detected:
        print("ALARM detected at %s, latency after fault: %.1f h" %
              (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(detected)),
               (detected - fault_ts) / 3600))
    else:
        print("no alarm raised after fault time - FAIL")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
