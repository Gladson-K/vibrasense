import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "software"))

from firmware_security import sha256_file, sign_manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--slot", choices=("A", "B"), required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    key = os.environ.get("VIBRASENSE_OTA_KEY")
    if not key:
        raise SystemExit("VIBRASENSE_OTA_KEY is required")

    payload = {
        "slot": args.slot,
        "version": args.version,
        "size": Path(args.image).stat().st_size,
        "sha256": sha256_file(args.image),
    }
    manifest = sign_manifest(payload, key)
    Path(args.out).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote %s for slot %s" % (args.out, args.slot))


if __name__ == "__main__":
    main()
