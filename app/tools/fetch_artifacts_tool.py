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

    if not job["outputs_collected"]:
        return {
            "ok": False,
            "reason": "Artifacts have not been collected yet",
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
        "source": "runner_docker_job",
        "job_id": job_id,
        "target": job["target"],
        "profile": job["profile"],
        "returncode": job["returncode"],
        "command": job["command"],
        "runner_backend": job["runner_backend"],
        "container_name": job["container_name"],
        "cleaned_up": job["cleaned_up"],
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