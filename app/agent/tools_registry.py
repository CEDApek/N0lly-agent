from app.tools.validate_target_tool import validate_target_tool
from app.tools.check_scope_tool import check_scope_tool
from app.tools.submit_scan_tool import submit_scan_tool
from app.tools.get_job_status_tool import get_job_status_tool
from app.tools.fetch_artifacts_tool import fetch_artifacts_tool
from app.tools.parse_nmap_results_tool import parse_nmap_results_tool
from app.tools.decide_followup_tool import decide_followup_tool
from app.tools.generate_report_tool import generate_report_tool


TOOLS = {
    "validate_target": validate_target_tool,
    "check_scope": check_scope_tool,
    "submit_scan": submit_scan_tool,
    "get_job_status": get_job_status_tool,
    "fetch_artifacts": fetch_artifacts_tool,
    "parse_results": parse_nmap_results_tool,
    "decide_followup": decide_followup_tool,
    "generate_report": generate_report_tool,
}