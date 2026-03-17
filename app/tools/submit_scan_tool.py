from app.scanner.profiles import get_profile
from app.scanner.job_store import create_job, update_job_status, set_job_artifacts


def submit_scan_tool(target: str, approved_profile: str) -> dict:
    profile = get_profile(approved_profile)

    job = create_job(target=target, profile=profile.name)

    # fake lifecycle progression for now
    update_job_status(job["job_id"], "running")
    set_job_artifacts(
        job["job_id"],
        [
            f"artifacts/{job['job_id']}/stdout.log",
            f"artifacts/{job['job_id']}/scan.xml",
        ],
    )
    update_job_status(job["job_id"], "done")

    return {
        "ok": True,
        "job_id": job["job_id"],
        "profile_used": profile.name,
        "status": "done",
        "artifacts": [
            f"artifacts/{job['job_id']}/stdout.log",
            f"artifacts/{job['job_id']}/scan.xml",
        ],
        "message": "Simulated scan job submitted successfully",
    }