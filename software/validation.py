import re

NODE_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def valid_node_id(value):
    return isinstance(value, str) and bool(NODE_ID_RE.fullmatch(value))


def require_node_id(value):
    if not valid_node_id(value):
        raise ValueError("invalid node id")
    return value
