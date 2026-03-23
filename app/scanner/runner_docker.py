import subprocess

from app.scanner.docker_config import DOCKER_SCANNER_IMAGE, DOCKER_LAB_NETWORK
from app.scanner.profiles import get_profile


PROFILE_COMMANDS = {
    "baseline": [
        "-oX", "-",
        "-Pn",
        "-sV",
        "--top-ports", "20",
    ],
    "web_light": [
        "-oX", "-",
        "-Pn",
        "-sV",
        "-p", "80,443,8080,8000",
    ],
    "followup_safe": [
        "-oX", "-",
        "-Pn",
        "-sV",
        "--top-ports", "30",
    ],
}


def run_docker_scan(target: str, profile: str, timeout: int | None = None) -> dict:
    if profile not in PROFILE_COMMANDS:
        return {
            "ok": False,
            "reason": f"Unknown profile: {profile}",
        }

    try:
        profile_obj = get_profile(profile)
    except ValueError as exc:
        return {
            "ok": False,
            "reason": str(exc),
        }

    effective_timeout = timeout or profile_obj.max_duration_seconds

    cmd = [
        "docker", "run", "--rm",
        "--network", DOCKER_LAB_NETWORK,
        DOCKER_SCANNER_IMAGE,
        *PROFILE_COMMANDS[profile],
        target,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=effective_timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "reason": "Dockerized scan timed out",
        }
    except Exception as exc:
        return {
            "ok": False,
            "reason": f"Docker runner error: {exc}",
        }

    return {
        "ok": True,
        "command": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }