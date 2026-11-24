import sqlite3
import threading
import time

from paths import database_path

_local = threading.local()


def conn():
    if not hasattr(_local, "c"):
        path = database_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        _local.c = sqlite3.connect(str(path), check_same_thread=False)
        _local.c.row_factory = sqlite3.Row
        migrate(_local.c)
    return _local.c


def migrate(c):
    c.executescript("""
    CREATE TABLE IF NOT EXISTS nodes(
      node_id TEXT PRIMARY KEY, name TEXT, machine_class TEXT,
      first_seen REAL, last_seen REAL, status TEXT DEFAULT "learning");
    CREATE TABLE IF NOT EXISTS telemetry(
      id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT, ts REAL,
      rms_vel REAL, peak REAL, crest REAL, kurt REAL,
      cur_rms REAL, temp REAL, b1 REAL, b2 REAL, b3 REAL, flags INTEGER);
    CREATE INDEX IF NOT EXISTS idx_tel ON telemetry(node_id, ts);
    CREATE TABLE IF NOT EXISTS alarms(
      id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT, ts REAL,
      state TEXT, reason TEXT, snapshot TEXT, ack INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS models(
      node_id TEXT, version INTEGER, trained_ts REAL,
      model_path TEXT, data_hash TEXT, PRIMARY KEY(node_id, version));
    """)
    c.commit()


def upsert_node(node_id, ts=None):
    c = conn()
    ts = ts or time.time()
    c.execute("INSERT OR IGNORE INTO nodes(node_id,first_seen,last_seen) VALUES(?,?,?)",
              (node_id, ts, ts))
    c.execute("UPDATE nodes SET last_seen=? WHERE node_id=?", (ts, node_id))
    c.commit()


def insert_telemetry(node_id, ts, d):
    conn().execute(
      "INSERT INTO telemetry(node_id,ts,rms_vel,peak,crest,kurt,cur_rms,temp,b1,b2,b3,flags)"
      " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      (node_id, ts, d.get("rms_vel"), d.get("peak"), d.get("crest"), d.get("kurt"),
       d.get("cur_rms"), d.get("temp"), d.get("b1"), d.get("b2"), d.get("b3"),
       d.get("flags", 0)))
    conn().commit()


def recent(node_id, minutes=60):
    return [dict(r) for r in conn().execute(
      "SELECT * FROM telemetry WHERE node_id=? AND ts>? ORDER BY ts",
      (node_id, time.time() - minutes * 60)).fetchall()]


def add_alarm(node_id, state, reason, snapshot):
    conn().execute("INSERT INTO alarms(node_id,ts,state,reason,snapshot) VALUES(?,?,?,?,?)",
                   (node_id, time.time(), state, reason, snapshot))
    conn().commit()


def list_alarms(ack=None):
    q = "SELECT * FROM alarms" + (" WHERE ack=?" if ack is not None else "") + " ORDER BY ts DESC LIMIT 500"
    rows = conn().execute(q, (ack,) if ack is not None else ()).fetchall()
    return [dict(r) for r in rows]


def machines():
    return [dict(r) for r in conn().execute("SELECT * FROM nodes").fetchall()]
