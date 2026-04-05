from fastapi import HTTPException

from app.storage.schemas import ParsedFinding, ScanRecord
from app.storage.records import get_scan_record, save_scan_record
from app.tools.get_job_status_tool import get_job_status_tool
from app.tools.finalize_scan_job_tool import finalize_scan_job_tool
from app.tools.fetch_artifacts_tool import fetch_artifacts_tool
from app.tools.parse_nmap_results_tool import parse_nmap_results_tool
from app.tools.decide_followup_tool import decide_followup_tool
from app.tools.generate_report_tool import generate_report_tool
from app.agent.state import add_decision, set_step


def process_scan_record_logic(scan_id: str) -> ScanRecord:
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
    record.metadata["stderr_preview"] = (
        artifact_result["stderr"][:500] if artifact_result.get("stderr") else ""
    )
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