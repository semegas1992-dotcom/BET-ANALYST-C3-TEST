"""Conservative quick read of the synthetic report."""
from d0_contract import digest
def build(result):
    s=result["stages"]
    if result["stage_sha256"]!={k:digest(v) for k,v in s.items()}:raise ValueError("stage integrity")
    return {"event_sha256":result["event_sha256"],"sporting_conclusion":"NOT_ESTABLISHED","dominant_trajectory":None,"markets":[{"contract":m["contract"],"status":"NOT_EVALUATED"} for m in s["E5"].get("market_scopes",[])][:5],"missing":s["E1"]["missing_or_unresolved"],"decision":"NOT_ESTABLISHED","limitations":result["limitations"],"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
