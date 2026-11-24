import json
import os
import subprocess
import sys
from pathlib import Path

import firmware_security

ROOT = Path(__file__).resolve().parents[1]


def test_sign_and_verify_manifest():
    payload = {"slot": "A", "version": "2.0.0", "size": 4, "sha256": "abc"}
    manifest = firmware_security.sign_manifest(payload, "test-key")
    assert firmware_security.verify_manifest(manifest, "test-key")
    assert not firmware_security.verify_manifest(manifest, "other-key")


def test_image_hash_is_checked(tmp_path):
    image = tmp_path / "firmware.bin"
    image.write_bytes(b"firmware")
    payload = {
        "slot": "A",
        "version": "2.0.0",
        "size": image.stat().st_size,
        "sha256": firmware_security.sha256_file(image),
    }
    manifest = firmware_security.sign_manifest(payload, "test-key")
    assert firmware_security.verify_image(manifest, "test-key", image)
    image.write_bytes(b"tampered")
    assert not firmware_security.verify_image(manifest, "test-key", image)


def test_rollback_prefers_verified_inactive_slot():
    assert firmware_security.choose_boot_slot("A", {"A": True, "B": True}) == "B"
    assert firmware_security.choose_boot_slot("A", {"A": True, "B": False}) == "A"
    assert firmware_security.choose_boot_slot("B", {"A": True, "B": True}) == "A"
    assert firmware_security.choose_boot_slot("A", {"A": False, "B": False}) is None


def test_ota_sign_tool(tmp_path):
    image = tmp_path / "firmware.bin"
    manifest_path = tmp_path / "manifest.json"
    image.write_bytes(b"v2-image")
    env = dict(os.environ, VIBRASENSE_OTA_KEY="test-key")
    result = subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "ota_sign.py"),
        "--image", str(image),
        "--slot", "B",
        "--version", "2.0.0",
        "--out", str(manifest_path),
    ], env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    manifest = json.loads(manifest_path.read_text())
    assert manifest["slot"] == "B"
    assert firmware_security.verify_image(manifest, "test-key", image)
