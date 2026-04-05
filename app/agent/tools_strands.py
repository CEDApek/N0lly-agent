from strands import tool

from app.storage.records import get_scan_record
from app.tools.get_job_status_tool import get_job_status_tool
from app.services.scan_processing import process_scan_record_logic


@tool
def get_scan_snapshot(scan_id: str) -> dict:
    """
    Get the current scan record summary for a given scan ID.

    Args:
        scan_id: The scan record ID.
    """
    record = get_scan_record(scan_id)
    if record is None:
        return {
            "ok": False,
            "reason": "Scan record not found",
            "scan_id": scan_id,
        }

    return {
        "ok": True,
        "scan_id": record.scan_id,
        "target": record.target,
        "requested_profile": record.requested_profile,
        "approved_profile": record.approved_profile,
        "scope_status": record.scope_status,
        "current_step": record.current_step,
        "job_id": record.job_id,
        "finding_count": len(record.parsed_findings),
        "followup_allowed": record.followup_allowed,
        "final_report_path": record.final_report_path,
        "has_report": bool(record.metadata.get("report_text")),
        "decision_log": record.decision_log,
        "recommended_followup_profile": record.metadata.get("recommended_followup_profile"),
        "followup_reason": record.metadata.get("followup_reason"),
        "executive_summary": record.metadata.get("executive_summary"),
    }

@tool
def get_scan_snapshot(scan_id: str) -> dict:
    record = get_scan_record(scan_id)
    if record is None:
        return {
            "ok": False,
            "reason": "Scan record not found",
            "scan_id": scan_id,
        }

    return {
        "ok": True,
        "scan_id": record.scan_id,
        "target": record.target,
        "requested_profile": record.requested_profile,
        "approved_profile": record.approved_profile,
        "scope_status": record.scope_status,
        "current_step": record.current_step,
        "job_id": record.job_id,
        "finding_count": len(record.parsed_findings),
        "followup_allowed": record.followup_allowed,
        "final_report_path": record.final_report_path,
        "has_report": bool(record.metadata.get("report_text")),
        "decision_log": record.decision_log,
        "recommended_followup_profile": record.metadata.get("recommended_followup_profile"),
        "followup_reason": record.metadata.get("followup_reason"),
        "executive_summary": record.metadata.get("executive_summary"),
    }


@tool
def get_scan_job_status(scan_id: str) -> dict:
    record = get_scan_record(scan_id)
    if record is None:
        return {
            "ok": False,
            "reason": "Scan record not found",
            "scan_id": scan_id,
        }

    if not record.job_id:
        return {
            "ok": False,
            "reason": "Scan record has no job ID",
            "scan_id": scan_id,
        }

    return get_job_status_tool(record.job_id)


@tool
def process_scan_record(scan_id: str) -> dict:
    try:
        record = process_scan_record_logic(scan_id)
    except Exception as exc:
        return {
            "ok": False,
            "reason": f"Processing failed: {exc}",
            "scan_id": scan_id,
        }

    return {
        "ok": True,
        "scan_id": record.scan_id,
        "current_step": record.current_step,
        "finding_count": len(record.parsed_findings),
        "followup_allowed": record.followup_allowed,
        "recommended_followup_profile": record.metadata.get("recommended_followup_profile"),
        "executive_summary": record.metadata.get("executive_summary"),
    }


@tool
def get_scan_report(scan_id: str) -> dict:
    record = get_scan_record(scan_id)
    if record is None:
        return {
            "ok": False,
            "reason": "Scan record not found",
            "scan_id": scan_id,
        }

    report_text = record.metadata.get("report_text")
    if not report_text:
        return {
            "ok": False,
            "reason": "Report not available",
            "scan_id": scan_id,
        }

    return {
        "ok": True,
        "scan_id": record.scan_id,
        "target": record.target,
        "executive_summary": record.metadata.get("executive_summary"),
        "report_text": report_text,
        "recommended_followup_profile": record.metadata.get("recommended_followup_profile"),
        "followup_reason": record.metadata.get("followup_reason"),
    }