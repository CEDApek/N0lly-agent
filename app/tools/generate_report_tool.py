def generate_report_tool(record) -> dict:
    """
    Generates a simple report payload from the current scan record.
    In v1 this is deterministic and template-based.
    """

    findings_lines = []
    if record.parsed_findings:
        for finding in record.parsed_findings:
            line = f"- Port {finding.port}"
            if finding.service:
                line += f" / service: {finding.service}"
            if finding.version:
                line += f" / version: {finding.version}"
            if finding.note:
                line += f" / note: {finding.note}"
            findings_lines.append(line)
    else:
        findings_lines.append("- No open services detected in parsed findings")

    executive_summary = (
        f"Scan completed for target '{record.target}' using profile "
        f"'{record.approved_profile}'. Parsed {len(record.parsed_findings)} finding(s)."
    )

    limitations = [
        "This is a bounded, simulated workflow in a controlled lab environment.",
        "Results are based on approved profiles only, not arbitrary scanner options.",
        "No exploitation or unrestricted probing was performed.",
    ]

    next_steps = []
    if record.followup_allowed and record.metadata.get("recommended_followup_profile"):
        next_steps.append(
            f"An approved follow-up may be considered with profile "
            f"'{record.metadata['recommended_followup_profile']}'."
        )
    else:
        next_steps.append("No further approved follow-up is recommended at this stage.")

    report_text = "\n".join([
        "# Nolly Scan Report",
        "",
        "## Executive Summary",
        executive_summary,
        "",
        "## Technical Findings",
        *findings_lines,
        "",
        "## Evidence References",
        *([f"- {path}" for path in record.artifacts] if record.artifacts else ["- No artifacts recorded"]),
        "",
        "## Limitations",
        *[f"- {item}" for item in limitations],
        "",
        "## Suggested Next Steps",
        *[f"- {item}" for item in next_steps],
    ])

    return {
        "ok": True,
        "executive_summary": executive_summary,
        "report_text": report_text,
    }