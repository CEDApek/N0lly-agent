from app.config import settings
from app.scanner.profiles import get_profile
from app.scanner.job_store import (
    create_job,
    update_job_status,
    set_job_error,
    set_job_runner_info,
)
from app.scanner.runner_docker_job import submit_docker_scan_job


def submit_scan_tool(target: str, approved_profile: str) -> dict:
    profile = get_profile(approved_profile)
    job = create_job(target=target, profile=profile.name)

    if settings.runner_backend != "docker":
        return {
            "ok": False,
            "job_id": job["job_id"],
            "reason": "This step expects RUNNER_BACKEND=docker",
        }

    submit_result = submit_docker_scan_job(
        target=target,
        profile=profile.name,
    )

    if not submit_result["ok"]:
        update_job_status(job["job_id"], "failed")
        set_job_error(job["job_id"], submit_result["reason"])
        return {
            "ok": False,
            "job_id": job["job_id"],
            "reason": submit_result["reason"],
        }

    update_job_status(job["job_id"], "running")
    set_job_runner_info(
        job["job_id"],
        runner_backend="docker",
        container_name=submit_result["container_name"],
        container_id=submit_result["container_id"],
    )

    return {
        "ok": True,
        "job_id": job["job_id"],
        "profile_used": profile.name,
        "status": "running",
        "runner_backend": "docker",
        "container_name": submit_result["container_name"],
        "message": "Docker scan job submitted successfully",
    }