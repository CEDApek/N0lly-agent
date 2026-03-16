from fastapi import FastAPI, HTTPException

from app.config import settings
from app.storage.schemas import ScanRequest, ScanRecord
from app.storage.records import save_scan_record, get_scan_record
from app.tools.validate_target_tool import validate_target_tool
from app.tools.check_scope_tool import check_scope_tool
from app.agent.state import add_decision, set_step


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="N0lly - guarded agentic security scan orchestrator",
)


@app.get("/")
def root() -> dict:
    return {
        "app": settings.app_name,
        "env": settings.app_env,
        "message": "N0lly API is running",
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
        },
    )

    add_decision(record, f"Target validated: {target_check['normalized_target']}")
    add_decision(record, f"Scope approved with profile: {scope_check['approved_profile']}")
    set_step(record, "scope_approved")

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

    return {
        "scan_id": record.scan_id,
        "target": record.target,
        "scope_status": record.scope_status,
        "current_step": record.current_step,
        "approved_profile": record.approved_profile,
        "followup_allowed": record.followup_allowed,
    }