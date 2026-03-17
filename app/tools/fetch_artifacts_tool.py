from app.scanner.job_store import get_job


def fetch_artifacts_tool(job_id: str) -> dict:
    job = get_job(job_id)

    if not job:
        return {
            "ok": False,
            "reason": "Job not found",
            "job_id": job_id,
        }

    if job["status"] != "done":
        return {
            "ok": False,
            "reason": "Artifacts are not ready until job is done",
            "job_id": job_id,
            "status": job["status"],
        }

    target = job["target"]

    # Simulated artifact content for now
    if target == "target-web":
        xml_content = """<nmaprun>
  <host>
    <ports>
      <port protocol="tcp" portid="80">
        <state state="open"/>
        <service name="http" product="nginx" version="1.24"/>
      </port>
    </ports>
  </host>
</nmaprun>"""
    elif target == "target-ssh":
        xml_content = """<nmaprun>
  <host>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh" product="OpenSSH" version="9.0"/>
      </port>
    </ports>
  </host>
</nmaprun>"""
    elif target == "target-multi":
        xml_content = """<nmaprun>
  <host>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh" product="OpenSSH" version="9.0"/>
      </port>
      <port protocol="tcp" portid="80">
        <state state="open"/>
        <service name="http" product="nginx" version="1.24"/>
      </port>
      <port protocol="tcp" portid="8080">
        <state state="open"/>
        <service name="http-proxy" product="simple-server" version="1.0"/>
      </port>
    </ports>
  </host>
</nmaprun>"""
    else:
        xml_content = """<nmaprun>
  <host>
    <ports>
    </ports>
  </host>
</nmaprun>"""

    stdout_log = f"Simulated scan completed for {target}"
    metadata = {
        "source": "simulated",
        "job_id": job_id,
        "target": target,
        "profile": job["profile"],
    }

    return {
        "ok": True,
        "job_id": job_id,
        "xml": xml_content,
        "stdout": stdout_log,
        "metadata": metadata,
        "artifacts": job["artifacts"],
    }