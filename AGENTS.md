# vibrasense — agent rules

Tier: **A2 (safety/physical systems)**. See `@governance/RISK-REGISTER.md` for the gate.

1. Read `@governance/AGENTS.md`, `POLICY.md`, `DATA-MAP.md`, and `SECURITY-BASELINE.md` before changes to code, data, or models.
2. Data restrictions: Follow `@governance/DATA-MAP.md`. Never send secrets, personal data, health recordings, or plant telemetry to models or web tools. Use synthetic fixtures only for AI-assisted work.
3. Commands: `make syntax-check`, `make test`, `make test-docker`, `make fw-check`, `make lint`, `make sbom`.
4. Never publish, deploy, push, or contact external services without approval.
5. Record AI assistance and human verification in the change description.
6. Run focused tests/lint after edits; report files changed, commands, results, and residual risks.
7. Keep alarms advisory. Do not claim certification, functional safety, medical validation, or legal compliance without documented evidence and named human sign-off.
