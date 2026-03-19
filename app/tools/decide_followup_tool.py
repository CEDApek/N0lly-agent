def decide_followup_tool(parsed_findings: list[dict], approved_profile: str) -> dict:
    """
    Rule-based follow-up decision for v1.
    Keeps policy deterministic before introducing agent reasoning.
    """

    if approved_profile != "baseline":
        return {
            "ok": True,
            "followup_allowed": False,
            "recommended_profile": None,
            "reason": "Follow-up is only considered after baseline scans",
        }

    if not parsed_findings:
        return {
            "ok": True,
            "followup_allowed": False,
            "recommended_profile": None,
            "reason": "No findings detected, so no follow-up is needed",
        }

    services = {item.get("service") for item in parsed_findings if item.get("service")}

    if services.issubset({"http", "http-proxy"}):
        return {
            "ok": True,
            "followup_allowed": True,
            "recommended_profile": "web_light",
            "reason": "Only web-related services detected, lightweight web follow-up may be allowed",
        }

    return {
        "ok": True,
        "followup_allowed": False,
        "recommended_profile": None,
        "reason": "Findings do not justify an approved follow-up profile",
    }