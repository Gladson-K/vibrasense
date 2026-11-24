OID_BASE = "1.3.6.1.4.1.99999.1"
SEVERITY_CODE = {"OK": 0, "WATCH": 1, "ALARM": 2}


def encode_trap(oid, value, severity):
    return {
        "oid": oid,
        "value": value,
        "severity": severity,
        "severity_code": SEVERITY_CODE.get(severity, 0),
    }


def health_trap(node_id, state):
    return encode_trap(OID_BASE + ".1.0", "%s:%s" % (node_id, state), state)
