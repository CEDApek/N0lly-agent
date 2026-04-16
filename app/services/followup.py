from fastapi import HTTPException

from app.storage.schemas import ScanRequest, ScanRecord
from app.storage.records import get_scan_record, save_scan_record
from app.tools.submit_scan_tool import submit_scan_tool
from app.agent.state import add_decision, set_step


def create_followup_scan_logic(scan_id: str) -> ScanRecord:
    parent_record = get_scan_record(scan_id)
    if parent_record is None:
        raise HTTPException(status_code=404, detail="Parent scan record not found")

    if not parent_record.followup_allowed:
        raise HTTPException(status_code=400, detail="Follow-up is not allowed for this scan")

    recommended_profile = parent_record.metadata.get("recommended_followup_profile")
    if not recommended_profile:
        raise HTTPException(status_code=400, detail="No approved follow-up profile available")

    child_record = ScanRecord(
        target=parent_record.target,
        requested_profile=recommended_profile,
        approved_profile=recommended_profile,
        authorization_ref=parent_record.authorization_ref,
        scope_status="approved",
        followup_allowed=False,
        metadata={
            "validation_reason": "Inherited from approved parent scan",
            "scope_reason": "Approved follow-up derived from parent scan policy",
            "runner_backend": parent_record.metadata.get("runner_backend"),
            "parent_scan_id": parent_record.scan_id,
            "is_followup": True,
        },
    )

    add_decision(child_record, f"Follow-up created from parent scan: {parent_record.scan_id}")
    add_decision(child_record, f"Approved follow-up profile: {recommended_profile}")
    set_step(child_record, "followup_initialized")

    submit_result = submit_scan_tool(
        target=child_record.target,
        approved_profile=child_record.approved_profile,
    )
    if not submit_result["ok"]:
        raise HTTPException(status_code=500, detail=submit_result)

    child_record.job_id = submit_result["job_id"]
    add_decision(child_record, f"Follow-up job submitted: {child_record.job_id}")
    add_decision(child_record, f"Job backend: {submit_result['runner_backend']}")
    set_step(child_record, "scan_submitted")

    save_scan_record(child_record)

    parent_record.metadata["followup_scan_id"] = child_record.scan_id
    add_decision(parent_record, f"Follow-up scan created: {child_record.scan_id}")
    save_scan_record(parent_record)

    return child_record