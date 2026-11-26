"""Real dossier preflight, read-only; never authorizes engine access."""
import json
from c4_t01_receipt import receive
from c4_quarantine import inspect
from c4_t01_mapping import validate
from d0_contract import stamp

def preflight(raw, expected_sha256, manifest):
    receipt = receive(raw, expected_sha256)
    data = json.loads(raw)
    gate = inspect(raw, expected_sha256, manifest)
    issues = set(gate["issues"])
    if not manifest.get("kickoff") or stamp(manifest["cutoff"]) >= stamp(manifest["kickoff"]):
        issues.add("KICKOFF_OR_CUTOFF_INVALID")
    if data.get("event_id") != manifest.get("event_id") or not data.get("event_id"):
        issues.add("EVENT_ID_NOT_BOUND")
    if not manifest.get("mappings"):
        issues.add("MAPPING_EMPTY")
    else:
        try:
            validate(manifest)
            for row in manifest["mappings"]:
                value = data
                for part in row["source_pointer"].split("/")[1:]:
                    part = part.replace("~1", "/").replace("~0", "~")
                    if isinstance(value, list):
                        if not part.isascii() or not part.isdecimal() or str(int(part)) != part:
                            raise ValueError("pointer")
                        value = value[int(part)]
                    else:
                        value = value[part]
                if value is None:
                    raise ValueError("missing")
        except (ValueError, KeyError, TypeError, IndexError):
            issues.add("MAPPING_INVALID")
    return {"sha256": receipt["sha256"], "issues": sorted(issues),
            "engine_access": False, "publication": "BLOCKED",
            "qualification": "BLOCKED", "status": "PREFLIGHT_ONLY"}

if __name__ == "__main__":
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("dossier")
    p.add_argument("sha256")
    p.add_argument("manifest")
    a = p.parse_args()
    print(json.dumps(preflight(Path(a.dossier).read_bytes(), a.sha256,
                              json.loads(Path(a.manifest).read_text())), indent=2))
