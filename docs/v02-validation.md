# v02 validation record

## Scope

Production PCB and robustness artefacts: watchdog, dual-bank OTA, signed manifest verification, rollback, boot time, brownout hold, low-temperature validation, and manufacturing jig definition.

## Automated evidence

| Check | Command | Coverage |
| --- | --- | --- |
| Syntax | `make syntax-check` | Python sources |
| Unit tests | `make test` | Manifest signing, image hash, tamper rejection, rollback selection, OTA sign tool |
| Firmware compile | `make fw-check` | Requires approved PlatformIO dependency resolution |

## Physical evidence still required

- PCB rev A passes EMC pre-scan.
- Watchdog reset measured on hardware.
- Brownout hold test completed without configuration corruption.
- Boot time below 3 s recorded across pilot units.
- −10 °C validation completed.
- 100-unit pilot with fewer than 2% dead-on-arrival units.
- Asymmetric signing design accepted before field OTA.

No hardware acceptance claim is made without signed records from a named hardware owner.
