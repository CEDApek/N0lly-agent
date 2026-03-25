import subprocess
from uuid import uuid4

from app.scanner.docker_config import DOCKER_SCANNER_IMAGE, DOCKER_LAB_NETWORK


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


def submit_docker_scan_job(target: str, profile: str) -> dict:
    if profile not in PROFILE_COMMANDS:
        return {
            "ok": False,
            "reason": f"Unknown profile: {profile}",
        }

    container_name = f"nolly-scan-{uuid4().hex[:12]}"

    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
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
            check=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "reason": f"Failed to submit docker job: {exc}",
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "reason": result.stderr.strip() or f"Docker run failed with code {result.returncode}",
            "command": cmd,
        }

    container_id = result.stdout.strip()

    return {
        "ok": True,
        "container_name": container_name,
        "container_id": container_id,
        "command": cmd,
    }


def get_docker_scan_job_status(container_name: str) -> dict:
    cmd = [
        "docker", "inspect",
        "-f", "{{.State.Status}}",
        container_name,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "reason": f"Failed to inspect docker job: {exc}",
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "reason": result.stderr.strip() or "Container not found",
        }

    raw_status = result.stdout.strip()

    if raw_status == "running":
        mapped_status = "running"
    elif raw_status == "created":
        mapped_status = "queued"
    elif raw_status == "exited":
        mapped_status = "done"
    else:
        mapped_status = raw_status

    return {
        "ok": True,
        "status": mapped_status,
        "raw_status": raw_status,
    }


def collect_docker_scan_job_output(container_name: str) -> dict:
    logs_cmd = ["docker", "logs", container_name]
    inspect_cmd = ["docker", "inspect", "-f", "{{.State.ExitCode}}", container_name]

    try:
        logs_result = subprocess.run(
            logs_cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        inspect_result = subprocess.run(
            inspect_cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "reason": f"Failed to collect docker output: {exc}",
        }

    if inspect_result.returncode != 0:
        return {
            "ok": False,
            "reason": inspect_result.stderr.strip() or "Failed to inspect exit code",
        }

    try:
        exit_code = int(inspect_result.stdout.strip())
    except ValueError:
        exit_code = -1

    return {
        "ok": True,
        "stdout": logs_result.stdout,
        "stderr": logs_result.stderr,
        "returncode": exit_code,
    }


def cleanup_docker_scan_job(container_name: str) -> dict:
    cmd = ["docker", "rm", "-f", container_name]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "reason": f"Failed to remove container: {exc}",
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "reason": result.stderr.strip() or "Failed to remove container",
        }

    return {
        "ok": True,
        "message": f"Removed {container_name}",
    }