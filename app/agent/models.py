from typing import Literal, Optional
from pydantic import BaseModel, Field


class AgentDecision(BaseModel):
    action: Literal["wait", "process_scan", "summarize_report", "inspect_scan"]
    rationale: str = Field(description="Short explanation for why this action was chosen")
    user_message: str = Field(description="User-facing explanation of the current scan state")
    recommended_followup_profile: Optional[str] = Field(
        default=None,
        description="Approved follow-up profile if relevant",
    )