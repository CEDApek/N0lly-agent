from app.scanner.job_store import (
    get_job,
    set_job_artifacts,
    set_job_error,
    set_job_result,
    mark_outputs_collected,
    mark_cleaned_up,
)
from app.scanner.runner_docker_job import (
    collect_docker_scan_job_output,
    cleanup_docker_scan_job,
)
from app.storage.artifacts import write_job_artifact


def finalize_scan_job_tool(job_id: str) -> dict:
    job = get_job(job_id)

    if not job:
        return {
            "ok": False,
            "reason": "Job not found",
            "job_id": job_id,
        }

    if job["status"] not in {"done", "failed"}:
        return {
            "ok": False,
            "reason": f"Job is not finished yet. Current status: {job['status']}",
            "job_id": job_id,
        }

    if not job["container_name"]:
        return {
            "ok": False,
            "reason": "No container associated with this job",
            "job_id": job_id,
        }

    if job["outputs_collected"]:
        return {
            "ok": True,
            "job_id": job_id,
            "artifacts": job["artifacts"],
            "message": "Outputs already collected",
        }

    output_result = collect_docker_scan_job_output(job["container_name"])
    if not output_result["ok"]:
        set_job_error(job_id, output_result["reason"])
        return {
            "ok": False,
            "job_id": job_id,
            "reason": output_result["reason"],
        }

    set_job_result(
        job_id,
        command=job["command"] or [],
        returncode=output_result["returncode"],
    )

    stdout_path = write_job_artifact(job_id, "stdout.log", output_result["stdout"])
    stderr_path = write_job_artifact(job_id, "stderr.log", output_result["stderr"])
    xml_path = write_job_artifact(job_id, "scan.xml", output_result["stdout"])

    artifacts = [stdout_path, stderr_path, xml_path]
    set_job_artifacts(job_id, artifacts)
    mark_outputs_collected(job_id, True)

    cleanup_result = cleanup_docker_scan_job(job["container_name"])
    if cleanup_result["ok"]:
        mark_cleaned_up(job_id, True)

    if output_result["returncode"] != 0:
        set_job_error(job_id, f"Scanner exited with return code {output_result['returncode']}")
        return {
            "ok": False,
            "job_id": job_id,
            "reason": f"Scanner exited with return code {output_result['returncode']}",
            "artifacts": artifacts,
        }

    return {
        "ok": True,
        "job_id": job_id,
        "artifacts": artifacts,
        "message": "Job finalized successfully",
    }