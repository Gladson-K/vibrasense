# v03 validation record

## Scope

High-frequency sensing: extended bands to 10 kHz, Hilbert envelope analysis, bearing-frequency calculators, mounting guidance, and LoRaWAN variant definition.

## Automated evidence

| Check | Command | Coverage |
| --- | --- | --- |
| Syntax | `make syntax-check` | Python sources |
| Unit tests | `make test` | Bearing calculators, envelope peak detection, extended bands |
| Firmware compile | `make fw-check` | Requires approved PlatformIO dependency resolution |

## Physical evidence still required

- Inner-race fault detected at least 2× earlier than v1 on rig.
- LoRaWAN range at least 500 m in plant.
- Stud, adhesive, and magnet mounting resonance measurements.
- High-rate sensor driver review and sampling accuracy evidence.

No physical detection or range claim is made without signed rig and plant records.
