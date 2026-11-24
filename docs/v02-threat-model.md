# v2 OTA threat model

## Scope

Firmware update path, device identity, manifest verification, and rollback.

## Assets

- Firmware image.
- Signing key.
- Device configuration, including Wi-Fi and broker settings.
- Boot slot state.

## Threats and controls

| Threat | Control | Residual risk |
| --- | --- | --- |
| Unsigned image accepted | Verify manifest signature before marking slot bootable | HMAC test harness needs replacement with asymmetric signing before field use |
| Image modified in transit | SHA-256 in manifest checked against image bytes | Transport must be authenticated and encrypted |
| Failed update bricks node | Dual slots and rollback to known-good slot | Bootloader behaviour needs hardware evidence |
| Signing key committed | Key read only from `VIBRASENSE_OTA_KEY` and ignored by git | Operators must protect their environment |
| Credentials exposed in config | No credentials in repository; provisioning remains local | Captive portal needs hardening before production |

## Gate

OTA must remain disabled outside the test bench until a named security reviewer accepts the production signing scheme, bootloader evidence, and device identity design.
