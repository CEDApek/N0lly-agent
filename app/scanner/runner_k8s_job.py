import json
import subprocess
from uuid import uuid4

from app.scanner.k8s_config import (
    K8S_NAMESPACE,
    K8S_SCANNER_IMAGE,
    K8S_JOB_TTL_SECONDS,
)


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


def _build_job_manifest(job_name: str, target: str, profile: str) -> dict:
    if profile not in PROFILE_COMMANDS:
        raise ValueError(f"Unknown profile: {profile}")

    cmd = PROFILE_COMMANDS[profile] + [target]

    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": job_name,
            "namespace": K8S_NAMESPACE,
            "labels": {
                "app": "nolly-scan",
                "profile": profile,
            },
        },
        "spec": {
            "ttlSecondsAfterFinished": K8S_JOB_TTL_SECONDS,
            "backoffLimit": 0,
            "template": {
                "metadata": {
                    "labels": {
                        "app": "nolly-scan",
                        "job-name": job_name,
                    }
                },
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [
                        {
                            "name": "scanner",
                            "image": K8S_SCANNER_IMAGE,
                            "imagePullPolicy": "IfNotPresent",
                            "args": cmd,
                        }
                    ],
                },
            },
        },
    }


def submit_k8s_scan_job(target: str, profile: str) -> dict:
    if profile not in PROFILE_COMMANDS:
        return {
            "ok": False,
            "reason": f"Unknown profile: {profile}",
        }

    job_name = f"nolly-scan-{uuid4().hex[:12]}"
    manifest = _build_job_manifest(job_name, target, profile)

    cmd = ["kubectl", "apply", "-f", "-"]

    try:
        result = subprocess.run(
            cmd,
            input=json.dumps(manifest),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "reason": f"Failed to submit k8s job: {exc}",
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "reason": result.stderr.strip() or "kubectl apply failed",
            "command": cmd,
            "manifest": manifest,
        }

    return {
        "ok": True,
        "job_name": job_name,
        "command": cmd,
        "manifest": manifest,
    }


def get_k8s_scan_job_status(job_name: str) -> dict:
    cmd = [
        "kubectl", "get", "job", job_name,
        "-n", K8S_NAMESPACE,
        "-o", "json",
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
            "reason": f"Failed to inspect k8s job: {exc}",
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "reason": result.stderr.strip() or "Job not found",
        }

    data = json.loads(result.stdout)
    status = data.get("status", {})

    if status.get("active", 0) > 0:
        mapped_status = "running"
    elif status.get("succeeded", 0) > 0:
        mapped_status = "done"
    elif status.get("failed", 0) > 0:
        mapped_status = "failed"
    else:
        mapped_status = "queued"

    return {
        "ok": True,
        "status": mapped_status,
        "raw_status": status,
    }


def get_k8s_job_pod_name(job_name: str) -> dict:
    cmd = [
        "kubectl", "get", "pods",
        "-n", K8S_NAMESPACE,
        "-l", f"job-name={job_name}",
        "-o", "json",
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
            "reason": f"Failed to get pods for job: {exc}",
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "reason": result.stderr.strip() or "Failed to get pods",
        }

    data = json.loads(result.stdout)
    items = data.get("items", [])
    if not items:
        return {
            "ok": False,
            "reason": "No pod found for job",
        }

    pod_name = items[0]["metadata"]["name"]
    return {
        "ok": True,
        "pod_name": pod_name,
    }


def collect_k8s_scan_job_output(job_name: str) -> dict:
    pod_result = get_k8s_job_pod_name(job_name)
    if not pod_result["ok"]:
        return pod_result

    pod_name = pod_result["pod_name"]

    logs_cmd = [
        "kubectl", "logs",
        "-n", K8S_NAMESPACE,
        pod_name,
    ]

    phase_cmd = [
        "kubectl", "get", "pod",
        "-n", K8S_NAMESPACE,
        pod_name,
        "-o", "json",
    ]

    try:
        logs_result = subprocess.run(
            logs_cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        phase_result = subprocess.run(
            phase_cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "reason": f"Failed to collect k8s job output: {exc}",
        }

    if phase_result.returncode != 0:
        return {
            "ok": False,
            "reason": phase_result.stderr.strip() or "Failed to inspect pod",
        }

    pod_data = json.loads(phase_result.stdout)
    phase = pod_data.get("status", {}).get("phase", "Unknown")

    returncode = 0 if phase == "Succeeded" else 1

    return {
        "ok": True,
        "stdout": logs_result.stdout,
        "stderr": logs_result.stderr,
        "returncode": returncode,
        "pod_name": pod_name,
        "phase": phase,
    }


def cleanup_k8s_scan_job(job_name: str) -> dict:
    cmd = [
        "kubectl", "delete", "job",
        job_name,
        "-n", K8S_NAMESPACE,
        "--ignore-not-found=true",
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
            "reason": f"Failed to delete k8s job: {exc}",
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "reason": result.stderr.strip() or "Failed to delete job",
        }

    return {
        "ok": True,
        "message": result.stdout.strip() or f"Deleted {job_name}",
    }