from app.config import settings
from app.scanner.profiles import get_profile
from app.scanner.job_store import (
    create_job,
    update_job_status,
    set_job_artifacts,
    set_job_error,
    set_job_result,
)
from app.scanner.runner_local import run_local_scan
from app.scanner.runner_docker import run_docker_scan
from app.storage.artifacts import write_job_artifact


def submit_scan_tool(target: str, approved_profile: str) -> dict:
    profile = get_profile(approved_profile)
    job = create_job(target=target, profile=profile.name)

    update_job_status(job["job_id"], "running")

    if settings.runner_backend == "docker":
        result = run_docker_scan(
            target=target,
            profile=profile.name,
            timeout=profile.max_duration_seconds,
        )
    else:
        result = run_local_scan(
            target=target,
            profile=profile.name,
            timeout=profile.max_duration_seconds,
        )

    if not result["ok"]:
        update_job_status(job["job_id"], "failed")
        set_job_error(job["job_id"], result["reason"])
        return {
            "ok": False,
            "job_id": job["job_id"],
            "reason": result["reason"],
        }

    set_job_result(
        job["job_id"],
        command=result["command"],
        returncode=result["returncode"],
    )

    stdout_path = write_job_artifact(job["job_id"], "stdout.log", result["stdout"])
    stderr_path = write_job_artifact(job["job_id"], "stderr.log", result["stderr"])
    xml_path = write_job_artifact(job["job_id"], "scan.xml", result["stdout"])

    artifacts = [stdout_path, stderr_path, xml_path]
    set_job_artifacts(job["job_id"], artifacts)

    if result["returncode"] != 0:
        update_job_status(job["job_id"], "failed")
        set_job_error(job["job_id"], f"Scanner exited with return code {result['returncode']}")
        return {
            "ok": False,
            "job_id": job["job_id"],
            "reason": f"Scanner exited with return code {result['returncode']}",
            "artifacts": artifacts,
        }

    update_job_status(job["job_id"], "done")

    return {
        "ok": True,
        "job_id": job["job_id"],
        "profile_used": profile.name,
        "status": "done",
        "artifacts": artifacts,
        "message": f"Scan job submitted successfully using backend '{settings.runner_backend}'",
    }