"""Read-only intake checks. Never authorizes real-data engine access."""
from hashlib import sha256
from d0_contract import stamp
def inspect(raw,expected_sha256,manifest):
    if not isinstance(raw,bytes) or sha256(raw).hexdigest()!=expected_sha256:raise ValueError("original byte integrity")
    cutoff=stamp(manifest["cutoff"])
    issues=[]
    if not manifest.get("event_id"):issues.append("EVENT_ID_MISSING")
    sources=manifest.get("sources",[])
    if not sources:issues.append("SOURCES_MISSING")
    for s in sources:
        if not s.get("url"):issues.append("SOURCE_URL_MISSING")
        if s.get("rights")!="verified":issues.append("RIGHTS_UNVERIFIED")
        if not s.get("available_at") or not s.get("captured_at"):issues.append("TIMESTAMP_MISSING")
        elif not stamp(s["available_at"])<=stamp(s["captured_at"])<=cutoff:issues.append("TEMPORAL_VIOLATION")
    return {"original_sha256":expected_sha256,"issues":sorted(set(issues+["MANUAL_ADMISSION_REQUIRED","SCHEMA_ADAPTER_REQUIRED"])),"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
