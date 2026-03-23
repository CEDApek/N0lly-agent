from app.scanner.profiles import SCAN_PROFILES


ALLOWED_TARGETS = {
    "target-web",
    "target-ssh",
    "target-multi",
    "target-empty",
    "127.0.0.1",
    "localhost",
    "172.20.0.3", # This is the target-web temporary target
}

AUTHORIZED_REFS = {
    "lab-internal-dev",
    "approved-local-lab",
}


def check_scope_tool(target: str, requested_profile: str, authorization_ref: str) -> dict:
    if target not in ALLOWED_TARGETS:
        return {
            "ok": False,
            "scope_status": "denied",
            "reason": "Target not in allowlist",
        }

    if authorization_ref not in AUTHORIZED_REFS:
        return {
            "ok": False,
            "scope_status": "denied",
            "reason": "Authorization reference not recognized",
        }

    if requested_profile not in SCAN_PROFILES:
        return {
            "ok": False,
            "scope_status": "denied",
            "reason": "Requested profile is not approved",
        }

    return {
        "ok": True,
        "scope_status": "approved",
        "approved_profile": requested_profile,
        "reason": "Scope check passed",
    }