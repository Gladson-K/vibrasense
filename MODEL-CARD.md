# Model card — VibraSense advisory baseline

## Identity

- Repository: `vibrasense`
- Version: v01 baseline
- Released artefact: none checked in
- Runtime format: canonical JSON with SHA-256 sidecar, verified before load

## Intended use

Advisory anomaly scoring for machine-health decision support. A human reviews alarms and decides whether to inspect equipment.

## Out of scope

Safety shutdown, protective relaying, medical use, certification evidence, autonomous control, and any claim of regulatory compliance.

## Metrics and limits

- Statistical baseline requires at least 100 windows before scoring.
- Autoencoder training requires at least 500 healthy windows.
- Seeded-fault replay acceptance target: at least 90% of injected fault windows in ALARM after escalation.
- No field accuracy, false-alarm rate, or production detection performance is claimed without recorded evidence.

Known failure modes: loose mounting, changing load regime, sensor drift, network loss, and unrepresentative healthy data.

## Safety

- Human oversight: technician review required.
- Artefact verification: SHA-256 sidecar checked before load; tampered artefacts are rejected.
- Advisory/autonomous: advisory only.
- Independent control: plant protection remains outside VibraSense.

## Maintenance

Owner: named project owner to be assigned. Record every retrain, threshold change, dataset change, and artefact hash change in the change description and update this card in the same commit.
