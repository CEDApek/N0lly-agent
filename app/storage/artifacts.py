from pathlib import Path


ARTIFACTS_ROOT = Path("runtime_artifacts") # write artifacts to here


def ensure_job_dir(job_id: str) -> Path:
    job_dir = ARTIFACTS_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def write_job_artifact(job_id: str, filename: str, content: str) -> str:
    job_dir = ensure_job_dir(job_id)
    path = job_dir / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


def read_job_artifact(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")