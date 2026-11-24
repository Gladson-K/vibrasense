import hashlib
import hmac
import json
from pathlib import Path


def canonical_bytes(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_digest(payload):
    unsigned = {k: v for k, v in payload.items() if k != "signature"}
    return sha256_bytes(canonical_bytes(unsigned))


def sign_manifest(payload, key):
    if isinstance(key, str):
        key = key.encode("utf-8")
    unsigned = {k: v for k, v in payload.items() if k != "signature"}
    signature = hmac.new(key, canonical_bytes(unsigned), hashlib.sha256).hexdigest()
    return dict(unsigned, signature=signature)


def verify_manifest(manifest, key):
    signature = manifest.get("signature")
    if not signature:
        return False
    expected = sign_manifest(manifest, key)["signature"]
    return hmac.compare_digest(str(signature), expected)


def verify_image(manifest, key, path):
    return verify_manifest(manifest, key) and manifest.get("sha256") == sha256_file(path)


def choose_boot_slot(running_slot, verified_slots):
    for slot in ("B", "A"):
        if slot != running_slot and verified_slots.get(slot):
            return slot
    if verified_slots.get(running_slot):
        return running_slot
    return None
