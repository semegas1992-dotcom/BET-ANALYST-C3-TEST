"""Pinned synthetic registry; integrity only, not real-source authentication."""
from pathlib import Path
import json
from d0_contract import digest

REGISTRY_PATH=Path(__file__).with_name("p27_registry.json")
REGISTRY_SHA256="45494b4566bcb956511e2dff451e2419ab7a3be29d4444a5e38cbdfea2041319"

def verify(case_id,dossier):
    state="REJECT"
    try:
        registry=json.loads(REGISTRY_PATH.read_text())
        if (digest(registry)==REGISTRY_SHA256 and dossier["origin"]=="synthetic"
                and dossier["engine_access"] is False and dossier["id"]==case_id
                and registry["entries"].get(case_id)==digest(dossier)):
            state="VERIFIED"
    except (OSError,ValueError,TypeError,KeyError,AttributeError,OverflowError):
        pass
    return dict(state=state,engine_access=False,publication="BLOCKED",qualification="BLOCKED",predictive_validity_verified=False)
