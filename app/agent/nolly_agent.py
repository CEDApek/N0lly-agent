from strands import Agent

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.models import AgentDecision
from app.agent.tools_strands import (
    get_scan_snapshot,
    get_scan_job_status,
    process_scan_record,
    get_scan_report,
)


class NollyStrandsAgent:
    def __init__(self):
        self.agent = Agent(
            system_prompt=SYSTEM_PROMPT,
            tools=[
                get_scan_snapshot,
                get_scan_job_status,
                process_scan_record,
                get_scan_report,
            ],
        )

    def run_for_scan(self, scan_id: str):
        prompt = f"""
You are reviewing scan_id={scan_id}.

Your job:
1. inspect the scan state
2. decide the best next action
3. if the scan is done but not yet processed, process it
4. if a report already exists, summarize it
5. return a structured decision

Use tools when needed.
"""

        result = self.agent(
            prompt,
            structured_output_model=AgentDecision,
        )

        return result