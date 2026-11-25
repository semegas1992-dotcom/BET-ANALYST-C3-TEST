"""Seven-section synthetic evidence report; never a sporting conclusion."""
from d0_contract import digest
from c4_quick_summary import build as quick_summary
def render(result):
    stages=result["stages"]
    if result["stage_sha256"]!={k:digest(v) for k,v in stages.items()}:raise ValueError("stage integrity")
    context=stages.get("context_analysis",{})
    opposition=(stages.get("matched_opposition") or {}).get("envelope",{})
    return {"schema":"C4_KRAFT_REPORT_SYNTHETIC_V1","input_sha256":result["input_sha256"],"stage_sha256":result["stage_sha256"],"event_sha256":result["event_sha256"],"audits":result["audits"],"quick_summary":quick_summary(result),"sections":[
        {"number":1,"title":"Synthèse rapide","status":"INCOMPLETE","detail":"Synthetic replay; no verified sporting conclusion"},
        {"number":2,"title":"Repères et données déterminantes","evidence":result["stage_sha256"]["E1"],"missing":stages["E1"]["missing_or_unresolved"]},
        {"number":3,"title":"Analyse sportive","evidence":result["stage_sha256"]["E2"],"context":context.get("summary",{}),"matched_opposition":stages.get("matched_opposition"),"status":"DESCRIPTIVE_ONLY"},
        {"number":4,"title":"Scénarios envisagés","evidence":result["stage_sha256"]["E3"],"scenarios":stages["E3"]["scenarios"],"opposition_context":opposition.get("scenario_context",{}),"trajectories":stages.get("trajectories",{}),"interactions":stages.get("interactions",{}),"observation_prompts":stages.get("trajectory_prompts",{}),"scoped_uncertainty":stages.get("scoped_uncertainty",{})},
        {"number":5,"title":"Projection du déroulement","evidence":result["stage_sha256"]["E4"],"descriptive_envelopes":opposition.get("metrics",{}),"sequences":context.get("sequences",[]),"scoped_arguments":stages.get("specific_dependencies",{}).get("sequences",[]),"status":"UNVERIFIED_TEMPLATES"},
        {"number":6,"title":"Marchés et lignes éventuelles","evidence":result["stage_sha256"]["E5"],"event_contracts":stages["E5"].get("event_contracts",[]),"market_scopes":stages["E5"].get("market_scopes",[]),"opposition_context":stages["E5"].get("opposition_context",[]),"availability_routing":stages.get("availability_routing",{}),"status":"NOT_EVALUATED"},
        {"number":7,"title":"Avis sportif final","status":"NOT_ESTABLISHED","data_quality":"SYNTHETIC_ONLY","sporting_reasoning":"UNVERIFIED","market_arguments":"NOT_EVALUATED"}],
        "limitations":result["limitations"],"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
