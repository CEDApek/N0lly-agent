import subprocess
from pathlib import Path


PROFILE_COMMANDS = {
    "baseline": [
        "nmap",
        "-oX",
        "-",
        "-Pn",
        "-sV",
        "--top-ports",
        "20",
    ],
    "web_light": [
        "nmap",
        "-oX",
        "-",
        "-Pn",
        "-sV",
        "-p",
        "80,443,8080,8000",
    ],
    "followup_safe": [
        "nmap",
        "-oX",
        "-",
        "-Pn",
        "-sV",
        "--top-ports",
        "30",
    ],
}


def run_local_scan(target: str, profile: str, timeout: int = 120) -> dict:
    if profile not in PROFILE_COMMANDS:
        return {
            "ok": False,
            "reason": f"Unknown profile: {profile}",
        }

    cmd = PROFILE_COMMANDS[profile] + [target]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired: # timeout ? exit timeout
        return {
            "ok": False,
            "reason": "Scan timed out",
        }
    except Exception as exc:        # General exception handling
        return {
            "ok": False,
            "reason": f"Runner error: {exc}",
        }

    return {                # success return
        "ok": True,
        "command": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }