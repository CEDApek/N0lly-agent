from app.utils.validation import validate_target_format, is_private_ip
from app.config import settings

"""
This is the tool for validating target
"""

def validate_target_tool(target: str) -> dict:
    is_valid, normalized = validate_target_format(target)

    if not is_valid:
        return {
            "ok": False,
            "reason": "Invalid target format",
            "normalized_target": normalized,
        }

    if is_private_ip(normalized) and not settings.allow_private_targets: # depends on allow_private_targets
        return {
            "ok": False,
            "reason": "Private targets are not allowed in current environment",
            "normalized_target": normalized,
        }

    return {
        "ok": True,
        "reason": "Target validated",
        "normalized_target": normalized,
    }