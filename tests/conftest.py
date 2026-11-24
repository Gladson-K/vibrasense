import atexit
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TMP = tempfile.TemporaryDirectory(prefix="vibrasense-tests-")
atexit.register(TMP.cleanup)

os.environ["VIBRASENSE_DB"] = str(Path(TMP.name) / "vibrasense.db")
os.environ["VIBRASENSE_MODEL_DIR"] = str(Path(TMP.name) / "ml_models")
os.environ["VIBRASENSE_AUDIT_LOG"] = str(Path(TMP.name) / "audit.jsonl")

for path in (ROOT, ROOT / "software", ROOT / "ml"):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)
