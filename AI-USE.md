# AI use — vibrasense

AI-assisted development is permitted under the workspace policy (`../_governance/POLICY.md`). Every change must record the tools used, the human verification performed, and the data used. A human is the author of record and reviews all AI output before merge and release.

Risk tier and release gate: **A2**, see `../_governance/RISK-REGISTER.md`. Legal screening: `../_governance/AI-REGULATIONS.md`. This is engineering screening, not legal advice.

## Disclosure

No chatbot, generative feature, or synthetic media is shipped in v01–v04. If one is added, users must be told they are interacting with AI and generated output must be labelled. EU AI Act Article 50 duties apply since 2 August 2026.

## Human oversight

A named human reviews AI output before merge. Tier A2 additionally requires a model card for deployed models, threat model for OTA/fleet connectivity, local-first data handling, and explicit human approval before pilot deployment or kit sales.

## Data

Follow `../_governance/DATA-MAP.md`. Sensor telemetry, alarm state, and the local database stay inside the plant unless reviewed. Never send secrets, personal data, health recordings, plant telemetry, or restricted datasets to models, hosted APIs, web tools, issues, or shared sessions. Tests use synthetic fixtures only.
