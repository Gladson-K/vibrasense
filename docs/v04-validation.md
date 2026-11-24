# v04 validation record

## Scope

Scale and usability: i18n, fleet CSV onboarding, RBAC, audit log, SNMP health trap representation, and local-first alert transports.

## Automated evidence

| Check | Command | Coverage |
| --- | --- | --- |
| Syntax | `make syntax-check` | Python sources |
| Unit tests | `make test` | i18n catalogs, RBAC matrix, audit log, fleet CSV, alert router, SNMP trap |
| Docker tests | `make test-docker` | Requires approved dependency install/build |

## API evidence

API tests are included but skipped when Flask is not installed in the local environment. They cover i18n, fleet import, SNMP trap representation, and RBAC denial.

## Physical and human evidence still required

- 50-node staged deployment completed.
- One part-time technician manages the staged fleet.
- SUS score at least 75 with named participants.
- Local SMTP relay configured only if approved.
- External SMS or email providers reviewed before use.

No usability score or production readiness claim is made without signed records.
