from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import uuid4


class ScanRequest(BaseModel):
    target: str
    requested_profile: str = "baseline"
    authorization_ref: str


class ParsedFinding(BaseModel):
    port: int
    service: Optional[str] = None
    version: Optional[str] = None
    note: Optional[str] = None


class ScanRecord(BaseModel):
    scan_id: str = Field(default_factory=lambda: str(uuid4()))
    target: str
    requested_profile: str
    approved_profile: Optional[str] = None
    authorization_ref: str
    scope_status: str = "pending"
    current_step: str = "request_received"
    job_id: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)
    parsed_findings: List[ParsedFinding] = Field(default_factory=list)
    followup_allowed: bool = False
    decision_log: List[str] = Field(default_factory=list)
    final_report_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)