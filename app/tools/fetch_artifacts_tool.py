from app.scanner.job_store import get_job
from app.storage.artifacts import read_job_artifact


def fetch_artifacts_tool(job_id: str) -> dict:
    job = get_job(job_id)

    if not job:
        return {
            "ok": False,
            "reason": "Job not found",
            "job_id": job_id,
        }

    if job["status"] != "done":
        return {
            "ok": False,
            "reason": "Artifacts are not ready until job is done",
            "job_id": job_id,
            "status": job["status"],
        }

    xml_path = None
    stdout_path = None
    stderr_path = None

    for path in job["artifacts"]:
        if path.endswith("scan.xml"):
            xml_path = path
        elif path.endswith("stdout.log"):
            stdout_path = path
        elif path.endswith("stderr.log"):
            stderr_path = path

    if not xml_path:
        return {
            "ok": False,
            "reason": "XML artifact not found",
            "job_id": job_id,
        }

    xml_content = read_job_artifact(xml_path)
    stdout_content = read_job_artifact(stdout_path) if stdout_path else ""
    stderr_content = read_job_artifact(stderr_path) if stderr_path else ""

    metadata = {
        "source": "runner_local",
        "job_id": job_id,
        "target": job["target"],
        "profile": job["profile"],
        "returncode": job["returncode"],
        "command": job["command"],
    }

    return {
        "ok": True,
        "job_id": job_id,
        "xml": xml_content,
        "stdout": stdout_content,
        "stderr": stderr_content,
        "metadata": metadata,
        "artifacts": job["artifacts"],
    }