# v01 validation record

## Scope

Baseline kit: 3-axis vibration at 1 kHz, current clamp, temperature, 10 s telemetry, 60 s band features, statistical baseline, advisory WATCH/ALARM logic, Flask dashboard, SQLite storage, MQTT ingest, store-and-forward, and synthetic seeded-fault replay.

## Automated evidence

| Check | Command | Status |
| --- | --- | --- |
| Syntax | `make syntax-check` | Recorded in commit verification |
| Unit and integration tests | `make test` | Recorded in commit verification |
| Docker tests | `make test-docker` | Requires approved dependency install/build |
| Firmware compile | `make fw-check` | Requires approved PlatformIO dependency resolution |

## L2 seeded-fault criterion

`tests/test_l2_seeded_fault.py` feeds 240 synthetic healthy windows followed by 40 synthetic fault windows. The acceptance threshold is at least 90% of fault windows in ALARM after escalation. This is synthetic evidence only.

## Physical evidence still required

- Bench-rig vibration, current, and temperature calibration records.
- Store-and-forward validation with broker outage.
- Field pilot start date, site, node IDs, and named owner.
- Human review of advisory alarm wording and dashboard usability.

No physical validation result is claimed in this repository without signed evidence.
