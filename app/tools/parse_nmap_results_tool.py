import xml.etree.ElementTree as ET


def parse_nmap_results_tool(xml_content: str) -> dict:
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as exc:
        return {
            "ok": False,
            "reason": f"Failed to parse XML: {exc}",
            "parsed_findings": [],
        }

    findings = []

    for port in root.findall(".//port"):
        state = port.find("state")
        if state is None or state.attrib.get("state") != "open":
            continue

        service = port.find("service")
        port_id = port.attrib.get("portid")

        service_name = service.attrib.get("name") if service is not None else None
        product = service.attrib.get("product") if service is not None else None
        version = service.attrib.get("version") if service is not None else None

        note_parts = []
        if product:
            note_parts.append(product)
        if version:
            note_parts.append(version)

        note = " ".join(note_parts) if note_parts else None

        exposure_hint = None
        if service_name in {"http", "http-proxy"}:
            exposure_hint = "Web service exposed"
        elif service_name == "ssh":
            exposure_hint = "Remote administration service exposed"

        findings.append(
            {
                "port": int(port_id),
                "service": service_name,
                "version": version,
                "note": note,
                "exposure_hint": exposure_hint,
            }
        )

    return {
        "ok": True,
        "parsed_findings": findings,
        "finding_count": len(findings),
    }