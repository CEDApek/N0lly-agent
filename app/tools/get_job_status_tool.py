from app.scanner.job_store import get_job, update_job_status, set_job_error
from app.scanner.runner_docker_job import get_docker_scan_job_status
from app.scanner.runner_k8s_job import get_k8s_scan_job_status


def get_job_status_tool(job_id: str) -> dict:
    job = get_job(job_id)

    if not job:
        return {
            "ok": False,
            "reason": "Job not found",
            "job_id": job_id,
        }

    if job["runner_backend"] == "docker" and job["container_name"]:
        docker_status = get_docker_scan_job_status(job["container_name"])
        if not docker_status["ok"]:
            set_job_error(job_id, docker_status["reason"])
            return {
                "ok": False,
                "reason": docker_status["reason"],
                "job_id": job_id,
            }
        update_job_status(job_id, docker_status["status"])

    elif job["runner_backend"] == "kubernetes" and job["platform_job_name"]:
        k8s_status = get_k8s_scan_job_status(job["platform_job_name"])
        if not k8s_status["ok"]:
            set_job_error(job_id, k8s_status["reason"])
            return {
                "ok": False,
                "reason": k8s_status["reason"],
                "job_id": job_id,
            }
        update_job_status(job_id, k8s_status["status"])

    refreshed_job = get_job(job_id)

    return {
        "ok": True,
        "job_id": refreshed_job["job_id"],
        "target": refreshed_job["target"],
        "profile": refreshed_job["profile"],
        "status": refreshed_job["status"],
        "artifacts": refreshed_job["artifacts"],
        "error": refreshed_job["error"],
        "runner_backend": refreshed_job["runner_backend"],
        "container_name": refreshed_job["container_name"],
        "platform_job_name": refreshed_job.get("platform_job_name"),
        "outputs_collected": refreshed_job["outputs_collected"],
        "cleaned_up": refreshed_job["cleaned_up"],
    }