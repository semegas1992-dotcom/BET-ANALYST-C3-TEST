"""Replay only independently frozen synthetic event dossiers."""
import json
from pathlib import Path
from copy import deepcopy
from d0_contract import digest
from c4_event_conditional import compare_bound

REGISTRY_PATH=Path(__file__).with_name("p27c_registry.json")
REGISTRY_SHA256="097c46201063c2ea461071b6a315f82dee9b0c33eddc7301cd1aecd4cecb37b8"

def replay(case_id,dossier):
    rejected=dict(state="REJECT",engine_access=False,publication="BLOCKED",qualification="BLOCKED",predictive_validity_verified=False)
    try:
        d=deepcopy(dossier)
        registry=json.loads(REGISTRY_PATH.read_text())
        if digest(registry)!=REGISTRY_SHA256 or d["id"]!=case_id or d["origin"]!="synthetic" or d["engine_access"] is not False or registry["entries"].get(case_id)!=digest(d):
            return rejected
        x=d["payload"]
        return compare_bound(x["d"],x["event"],x["dependencies"],x["trajectories"],x["contract"],x["packet"],digest(x["packet"]),x["threshold"])
    except (OSError,ValueError,TypeError,KeyError,AttributeError,OverflowError,IndexError):
        return rejected
