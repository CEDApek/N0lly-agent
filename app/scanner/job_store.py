from typing import Optional
from uuid import uuid4


JOB_STORE: dict[str, dict] = {}


def create_job(target: str, profile: str) -> dict:
    job_id = str(uuid4())

    job = {
        "job_id": job_id,
        "target": target,
        "profile": profile,
        "status": "queued",
        "artifacts": [],
        "error": None,
        "returncode": None,
        "command": None,
    }

    JOB_STORE[job_id] = job
    return job


def get_job(job_id: str) -> Optional[dict]:
    return JOB_STORE.get(job_id)


def update_job_status(job_id: str, status: str) -> Optional[dict]:
    job = JOB_STORE.get(job_id)
    if not job:
        return None

    job["status"] = status
    return job


def set_job_artifacts(job_id: str, artifacts: list[str]) -> Optional[dict]:
    job = JOB_STORE.get(job_id)
    if not job:
        return None

    job["artifacts"] = artifacts
    return job


def set_job_error(job_id: str, error: str) -> Optional[dict]:
    job = JOB_STORE.get(job_id)
    if not job:
        return None

    job["error"] = error
    return job


def set_job_result(job_id: str, command: list[str], returncode: int) -> Optional[dict]:
    job = JOB_STORE.get(job_id)
    if not job:
        return None

    job["command"] = command
    job["returncode"] = returncode
    return job