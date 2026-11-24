import json
import os
import time
from pathlib import Path

import paths


def audit_path():
    value = os.environ.get("VIBRASENSE_AUDIT_LOG")
    if value:
        return Path(value).expanduser().resolve()
    return paths.project_root() / "logs" / "audit.jsonl"


def append(actor, action, target="", result="ok", **details):
    path = audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": time.time(),
        "actor": actor,
        "action": action,
        "target": target,
        "result": result,
    }
    record.update(details)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def read_all(path=None):
    target = Path(path) if path else audit_path()
    if not target.exists():
        return []
    return [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line]
