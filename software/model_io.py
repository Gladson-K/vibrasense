import hashlib
import hmac
import json
from pathlib import Path


SCHEMA = "vibrasense-mlp-v1"


def canonical_bytes(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def artifact_digest(payload):
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def write_artifact(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    document = dict(payload)
    document.setdefault("schema", SCHEMA)
    digest = artifact_digest(document)
    target.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    target.with_suffix(".json.sha256").write_text(digest + "\n", encoding="utf-8")
    return digest


def load_verified_artifact(path):
    target = Path(path)
    document = json.loads(target.read_text(encoding="utf-8"))
    sidecar = target.with_suffix(".json.sha256")
    expected = sidecar.read_text(encoding="utf-8").strip()
    actual = artifact_digest(document)
    if not hmac.compare_digest(expected, actual):
        raise ValueError("model artefact hash mismatch")
    if document.get("schema") != SCHEMA:
        raise ValueError("unsupported model artefact schema")
    return document
