ROLE_ACTIONS = {
    "viewer": {"read"},
    "technician": {"read", "ack", "retrain", "onboard"},
    "admin": {"read", "ack", "retrain", "onboard", "export", "manage_users"},
}


def allowed(role, action):
    return action in ROLE_ACTIONS.get(role, set())


def role_from_headers(headers, default="viewer"):
    role = headers.get("X-Role", default)
    return role if role in ROLE_ACTIONS else default
