from app.storage.schemas import ScanRecord, ParsedFinding
from app.tools.generate_report_tool import generate_report_tool

def run():
    record = ScanRecord(
        target="target-web",
        requested_profile="baseline",
        approved_profile="baseline",
        authorization_ref="approved-local-lab",
        scope_status="approved",
        followup_allowed=True,
        artifacts=[
            "artifacts/demo/stdout.log",
            "artifacts/demo/scan.xml",
        ],
        parsed_findings=[
            ParsedFinding(
                port=80,
                service="http",
                version="1.24",
                note="nginx 1.24",
            )
        ],
        metadata={
            "recommended_followup_profile": "web_light"
        },
    )

    result = generate_report_tool(record)
    print(result["report_text"])

if __name__ == "__main__":
    run()