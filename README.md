# VibraSense

Advisory machine-health monitoring kit for small industry. Alerts are decision support only; they are not certified safety functions, medical claims, or legal compliance evidence.

## Implemented scope

- `dev/version1` / v01: working kit — sensing, telemetry, Flask dashboard, SQLite, MQTT, statistical baseline, safe JSON model artefacts, seeded-fault replay.
- `dev/version2` / v02: robustness — signed manifest verification model, rollback selection, OTA threat model, PCB design contract, manufacturing jig specification.
- `dev/version3` / v03: high-frequency sensing — extended bands to 10 kHz, Hilbert envelope analysis, bearing-frequency calculators, mounting and LoRaWAN variant guidance.
- `dev/version4` / v04: scale and usability — EN/ES/HI/PT i18n, fleet CSV onboarding, RBAC, audit log, SNMP trap representation, local-first alert transports.
- v05–v10 remain roadmap-only. v11–v15 are planned in the original roadmap but have no specification files yet.

## Repository layout

| Path | Content |
| --- | --- |
| `firmware/vibrasense_node/` | ESP32 node firmware source and build configuration |
| `software/` | Gateway API, dashboard, ingest, storage, scoring, RBAC, audit, alerts |
| `ml/` | Feature extraction, baseline training, high-frequency DSP, backtesting |
| `tests/` | pytest suite |
| `hardware/` | BOM, assembly guide, PCB/v2, jig/v2, mounting/v3, LoRaWAN/v3 artefacts |
| `docs/` | Validation records and threat model |
| `docker/` | Dockerfile and broker config used by Docker Compose |
| `.github/workflows/ci.yml.disabled` | CI workflow kept disabled until approved |
| `v01.md`–`v10.md` | Version roadmap documents |

## Local test commands

```bash
make syntax-check
make test
make test-docker
make fw-check
```

`make test` uses the local Python environment. API tests skip when Flask is not installed. `make test-docker` builds and runs the pytest service with a local MQTT broker. `make fw-check` compiles firmware with PlatformIO. Docker build and PlatformIO library resolution may require network access; run only with approval.

## Dashboard

```bash
docker compose up -d mosquitto gateway
```

Open `http://127.0.0.1:5000`. The gateway is published on loopback only. Do not expose it to an untrusted network.

## Main API endpoints

| Endpoint | Purpose |
| --- | --- |
| `/api/machines` | List nodes |
| `/api/telemetry?node=<id>` | Recent telemetry for a node |
| `/api/alarms` | Alarm list |
| `/api/bearing-frequencies` | BPFO/BPFI/BSF/FTF calculator |
| `/api/i18n/<lang>` | UI catalog |
| `/api/fleet/import` | CSV onboarding with QR payloads |
| `/api/snmp/trap` | SNMP trap representation |
| `/api/alerts/test` | Local alert transport test |
| `/api/models/retrain` | Retrain baseline model |

## Synthetic data

```bash
python3 software/sample_data/make_sample.py
python3 ml/backtest.py --node demo-mill-01 --fault-at <timestamp printed by generator>
```

Use synthetic data only. Never commit plant telemetry, credentials, `.env`, keys, or model artefacts with real data.

## Governance

Risk tier: **A2** per `../_governance/RISK-REGISTER.md`. AI-assisted changes must record tools used, delegated work, human verification, data used, and gate status. Security reviews, privacy reviews, and named human approval are required before release.

## Licences

Hardware: CERN-OHL-S v2. Software: MIT. Docs: CC-BY-4.0.
