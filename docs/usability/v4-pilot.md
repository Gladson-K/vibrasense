# v4 usability pilot plan

## Scope

Fleet onboarding, multi-language dashboard, RBAC, audit log, SNMP health traps, and local-first alert transports.

## Pilot setup

- 50 synthetic or consented test nodes in a staged environment.
- One part-time technician as primary operator.
- Languages tested: EN, ES, HI, PT.
- Roles: viewer, technician, admin.
- Alerts stay local by default; SMTP transport is used only with an approved local relay.

## Procedure

1. Import the fleet CSV through `/api/fleet/import`.
2. Print QR labels from returned payloads.
3. Onboard 50 nodes and verify site/machine hierarchy.
4. Run role checks: viewer cannot acknowledge or retrain; technician can acknowledge and onboard; admin can test alerts and manage users.
5. Trigger one WATCH and one ALARM per language.
6. Verify audit entries for acknowledge, retrain, fleet import, and alert test.
7. Ask each participant to complete the System Usability Scale after a supervised session.

## Acceptance

- 50-node deployment managed by one part-time technician.
- SUS score at least 75.
- No unauthorised role action succeeds.
- No email, SMS, or external service is contacted unless explicitly configured and approved.

No SUS score or pilot completion is claimed without signed records from the named pilot owner.
