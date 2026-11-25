"""Seven-section synthetic evidence report; never a sporting conclusion."""
from d0_contract import digest
def render(result):
    stages=result["stages"]
    if result["stage_sha256"]!={k:digest(v) for k,v in stages.items()}:raise ValueError("stage integrity")
    context=stages.get("context_analysis",{})
    return {"schema":"C4_KRAFT_REPORT_SYNTHETIC_V1","input_sha256":result["input_sha256"],"sections":[
        {"number":1,"title":"Synthèse rapide","status":"INCOMPLETE","detail":"Synthetic replay; no verified sporting conclusion"},
        {"number":2,"title":"Repères et données déterminantes","evidence":result["stage_sha256"]["E1"],"missing":stages["E1"]["missing_or_unresolved"]},
        {"number":3,"title":"Analyse sportive","evidence":result["stage_sha256"]["E2"],"context":context.get("summary",{}),"status":"DESCRIPTIVE_ONLY"},
        {"number":4,"title":"Scénarios envisagés","evidence":result["stage_sha256"]["E3"],"scenarios":stages["E3"]["scenarios"]},
        {"number":5,"title":"Projection du déroulement","sequences":context.get("sequences",[]),"status":"UNVERIFIED_TEMPLATES"},
        {"number":6,"title":"Marchés et lignes éventuelles","evidence":result["stage_sha256"]["E5"],"status":"NOT_EVALUATED"},
        {"number":7,"title":"Avis sportif final","status":"NOT_ESTABLISHED","data_quality":"SYNTHETIC_ONLY","sporting_reasoning":"UNVERIFIED","market_arguments":"NOT_EVALUATED"}],
        "limitations":result["limitations"],"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
