from fastapi import FastAPI, HTTPException
from app.agent.nolly_agent import NollyAgent
from app.storage.schemas import ParsedFinding

from app.config import settings
from app.storage.schemas import ScanRequest, ScanRecord, ParsedFinding
from app.storage.records import save_scan_record, get_scan_record
from app.tools.validate_target_tool import validate_target_tool
from app.tools.check_scope_tool import check_scope_tool
from app.tools.submit_scan_tool import submit_scan_tool
from app.tools.get_job_status_tool import get_job_status_tool
from app.tools.fetch_artifacts_tool import fetch_artifacts_tool
from app.tools.finalize_scan_job_tool import finalize_scan_job_tool
from app.tools.parse_nmap_results_tool import parse_nmap_results_tool
from app.agent.state import add_decision, set_step
from app.tools.decide_followup_tool import decide_followup_tool
from app.tools.generate_report_tool import generate_report_tool

agent = NollyAgent()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Nolly - guarded agentic security scan orchestrator",
)


@app.get("/")
def root() -> dict:
    return {
        "app": settings.app_name,
        "env": settings.app_env,
        "message": "Nolly API is running",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
    }


@app.post("/scans", response_model=ScanRecord)
def create_scan(request: ScanRequest) -> ScanRecord:
    target_check = validate_target_tool(request.target)
    if not target_check["ok"]:
        raise HTTPException(status_code=400, detail=target_check)

    scope_check = check_scope_tool(
        target=target_check["normalized_target"],
        requested_profile=request.requested_profile,
        authorization_ref=request.authorization_ref,
    )
    if not scope_check["ok"]:
        raise HTTPException(status_code=403, detail=scope_check)

    record = ScanRecord(
        target=target_check["normalized_target"],
        requested_profile=request.requested_profile,
        approved_profile=scope_check["approved_profile"],
        authorization_ref=request.authorization_ref,
        scope_status=scope_check["scope_status"],
        followup_allowed=False,
        metadata={
            "validation_reason": target_check["reason"],
            "scope_reason": scope_check["reason"],
            "runner_backend": settings.runner_backend,
        },
    )

    add_decision(record, f"Target validated: {target_check['normalized_target']}")
    add_decision(record, f"Scope approved with profile: {scope_check['approved_profile']}")
    set_step(record, "scope_approved")

    submit_result = submit_scan_tool(
        target=record.target,
        approved_profile=record.approved_profile,
    )
    if not submit_result["ok"]:
        raise HTTPException(status_code=500, detail=submit_result)

    record.job_id = submit_result["job_id"]
    add_decision(record, f"Job submitted: {record.job_id}")
    add_decision(record, f"Job backend: {submit_result['runner_backend']}")
    set_step(record, "scan_submitted")

    save_scan_record(record)
    return record


@app.get("/scans/{scan_id}", response_model=ScanRecord)
def read_scan(scan_id: str) -> ScanRecord:
    record = get_scan_record(scan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Scan record not found")
    return record


@app.get("/scans/{scan_id}/status")
def read_scan_status(scan_id: str) -> dict:
    record = get_scan_record(scan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Scan record not found")

    job_status = None
    if record.job_id:
        job_status = get_job_status_tool(record.job_id)

    return {
        "scan_id": record.scan_id,
        "target": record.target,
        "scope_status": record.scope_status,
        "current_step": record.current_step,
        "approved_profile": record.approved_profile,
        "job_id": record.job_id,
        "job_status": job_status["status"] if job_status and job_status["ok"] else None,
        "outputs_collected": job_status["outputs_collected"] if job_status and job_status["ok"] else None,
        "cleaned_up": job_status["cleaned_up"] if job_status and job_status["ok"] else None,
        "finding_count": len(record.parsed_findings),
        "followup_allowed": record.followup_allowed,
    }

@app.get("/scans/{scan_id}/report") #report endpoint
def read_scan_report(scan_id: str) -> dict:
    record = get_scan_record(scan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Scan record not found")

    report_text = record.metadata.get("report_text")
    if not report_text:
        raise HTTPException(status_code=404, detail="Report not available")

    return {
        "scan_id": record.scan_id,
        "target": record.target,
        "report_path": record.final_report_path,
        "executive_summary": record.metadata.get("executive_summary"),
        "report_text": report_text,
    }

@app.get("/scans/{scan_id}/agent-analysis") # agent analysis from record
def agent_analysis(scan_id: str) -> dict:
    record = get_scan_record(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail="Scan not found")

    result = agent.analyze_record(record)

    return {
        "scan_id": scan_id,
        "agent_result": result,
    }

# Check job scanning process
@app.post("/scans/{scan_id}/process", response_model=ScanRecord)
def process_scan(scan_id: str) -> ScanRecord:
    record = get_scan_record(scan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Scan record not found")

    if not record.job_id:
        raise HTTPException(status_code=400, detail="Scan record has no job_id")

    job_status = get_job_status_tool(record.job_id)
    if not job_status["ok"]:
        raise HTTPException(status_code=500, detail=job_status)

    record.metadata["job_status"] = job_status["status"]
    add_decision(record, f"Job status checked: {job_status['status']}")

    if job_status["status"] not in {"done", "failed"}:
        set_step(record, "waiting_for_job_completion")
        save_scan_record(record)
        return record

    finalize_result = finalize_scan_job_tool(record.job_id)
    if not finalize_result["ok"]:
        raise HTTPException(status_code=500, detail=finalize_result)

    record.artifacts = finalize_result["artifacts"]
    add_decision(record, "Job finalized and artifacts collected")
    set_step(record, "artifacts_collected")

    artifact_result = fetch_artifacts_tool(record.job_id)
    if not artifact_result["ok"]:
        raise HTTPException(status_code=500, detail=artifact_result)

    record.metadata["artifact_metadata"] = artifact_result["metadata"]
    record.metadata["stderr_preview"] = artifact_result["stderr"][:500] if artifact_result.get("stderr") else ""
    add_decision(record, "Artifacts fetched successfully")
    set_step(record, "artifacts_fetched")

    parse_result = parse_nmap_results_tool(artifact_result["xml"])
    if not parse_result["ok"]:
        raise HTTPException(status_code=500, detail=parse_result)

    record.parsed_findings = [
        ParsedFinding(
            port=item["port"],
            service=item.get("service"),
            version=item.get("version"),
            note=item.get("note"),
        )
        for item in parse_result["parsed_findings"]
    ]

    record.metadata["finding_count"] = parse_result["finding_count"]
    record.metadata["parsed_exposure_hints"] = [
        item.get("exposure_hint")
        for item in parse_result["parsed_findings"]
        if item.get("exposure_hint")
    ]

    add_decision(record, f"Parsed findings: {parse_result['finding_count']}")
    set_step(record, "findings_parsed")

    followup_result = decide_followup_tool(
        parsed_findings=parse_result["parsed_findings"],
        approved_profile=record.approved_profile,
    )
    if not followup_result["ok"]:
        raise HTTPException(status_code=500, detail=followup_result)

    record.followup_allowed = followup_result["followup_allowed"]
    record.metadata["recommended_followup_profile"] = followup_result["recommended_profile"]
    record.metadata["followup_reason"] = followup_result["reason"]

    add_decision(record, f"Follow-up allowed: {record.followup_allowed}")
    add_decision(record, f"Follow-up decision reason: {followup_result['reason']}")
    set_step(record, "followup_decided")

    report_result = generate_report_tool(record)
    if not report_result["ok"]:
        raise HTTPException(status_code=500, detail=report_result)

    record.final_report_path = f"reports/{record.scan_id}.md"
    record.metadata["report_text"] = report_result["report_text"]
    record.metadata["executive_summary"] = report_result["executive_summary"]

    add_decision(record, "Report generated successfully")
    set_step(record, "report_generated")

    save_scan_record(record)
    return record