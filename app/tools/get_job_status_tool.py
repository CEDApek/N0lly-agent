from app.scanner.job_store import get_job


def get_job_status_tool(job_id: str) -> dict:
    job = get_job(job_id)

    if not job:
        return {
            "ok": False,
            "reason": "Job not found",
            "job_id": job_id,
        }

    return {
        "ok": True,
        "job_id": job["job_id"],
        "target": job["target"],
        "profile": job["profile"],
        "status": job["status"],
        "artifacts": job["artifacts"],
        "error": job["error"],
    }