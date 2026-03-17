from app.tools.submit_scan_tool import submit_scan_tool
from app.tools.get_job_status_tool import get_job_status_tool
from app.tools.fetch_artifacts_tool import fetch_artifacts_tool
from app.tools.parse_nmap_results_tool import parse_nmap_results_tool

"""
Mini checkpoint test for nmap fake data parsing
"""

def run():
    submit_result = submit_scan_tool("target-ssh", "baseline")
    print("submit_result:", submit_result)

    job_id = submit_result["job_id"]

    job_status = get_job_status_tool(job_id)
    print("job_status:", job_status)

    artifact_result = fetch_artifacts_tool(job_id)
    print("artifact_result:", artifact_result)

    parse_result = parse_nmap_results_tool(artifact_result["xml"])
    print("parse_result:", parse_result)

if __name__ == "__main__":
    run()