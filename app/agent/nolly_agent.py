from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools_registry import TOOLS


class NollyAgent:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT

    def analyze_record(self, record) -> dict:
        """
        Simulated agent reasoning layer.
        In future this will be replaced with Strands runtime.
        """

        reasoning = []

        reasoning.append("Analyzing scan record...")
        reasoning.append(f"Target: {record.target}")
        reasoning.append(f"Findings count: {len(record.parsed_findings)}")

        if not record.parsed_findings: #if no finding, show no need follow up
            reasoning.append("No findings detected → no follow-up needed")
            return {
                "action": "none",
                "reasoning": reasoning,
            }

        services = [f.service for f in record.parsed_findings if f.service]

        if "http" in services: # we can add more later for more detected services type
            reasoning.append("HTTP detected → considering web follow-up")
            return {
                "action": "consider_followup",
                "recommended_profile": "web_light",
                "reasoning": reasoning,
            }

        reasoning.append("No actionable follow-up identified")

        return {
            "action": "none",
            "reasoning": reasoning,
        }