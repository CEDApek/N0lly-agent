from typing import Dict, List
from pydantic import BaseModel


class ScanProfile(BaseModel):
    name: str
    description: str
    allowed_options: List[str]
    max_duration_seconds: int
    service_detection: bool
    followup_permitted: bool
    max_target_count: int = 1


SCAN_PROFILES: Dict[str, ScanProfile] = {
    "baseline": ScanProfile(
        name="baseline",
        description="Safe initial reconnaissance profile",
        allowed_options=["top_ports"],
        max_duration_seconds=120,
        service_detection=True,
        followup_permitted=True,
        max_target_count=1,
    ),
    "web_light": ScanProfile(
        name="web_light",
        description="Lightweight web-focused follow-up profile",
        allowed_options=["web_ports"],
        max_duration_seconds=90,
        service_detection=True,
        followup_permitted=False,
        max_target_count=1,
    ),
    "followup_safe": ScanProfile(
        name="followup_safe",
        description="Bounded second-step follow-up profile",
        allowed_options=["limited_followup"],
        max_duration_seconds=120,
        service_detection=True,
        followup_permitted=False,
        max_target_count=1,
    ),
}


def get_profile(profile_name: str) -> ScanProfile:
    if profile_name not in SCAN_PROFILES:
        raise ValueError(f"Unknown scan profile: {profile_name}")
    return SCAN_PROFILES[profile_name]