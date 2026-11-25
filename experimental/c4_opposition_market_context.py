"""Historical context only; a contrast is not a team total."""
from d0_contract import digest
from c4_market_scope import RULES
def route(event,documented,envelope,market):
    if envelope["documented_sha256"]!=digest(documented):raise ValueError("documented hash")
    c=market["contract"];sport=event["sport"]
    unit,period,kind=RULES[sport][c["family"]]
    if c["event_sha256"]!=digest(event) or c["sport"]!=sport or c["unit"]!=unit or c["period"]!=period:raise ValueError("market scope")
    metric={"football":"goals_for","nba":"points_for"}.get(sport)
    accepted=[]
    if c["family"]=="team_total" and kind=="team" and c["subject"] in event["participants"] and metric in envelope["metrics"]:
        for s in envelope["metrics"][metric]["strata"]:
            sp,m,ctx,opp=s["stratum"]
            if sp!=sport or m!=metric or s["contrast"] is None:continue
            traces=[t for t in documented["trace"] if t["metric"]==m and t["claims"]["opponent_id"][0]==opp and digest([t["claims"]["format"][0],t["claims"]["conditions"][0]])==ctx]
            if not traces or any(t["unit"]!=unit or t["claims"]["format"][0]!=period for t in traces):continue
            if {t["participant"] for t in traces}!=set(event["participants"]):continue
            accepted.append({"stratum":s["stratum"],"observation_ids":sorted(t["observation_id"] for t in traces if t["participant"]==c["subject"]),"scope":"CONTEXT_ONLY_NOT_THRESHOLD_COMPARABLE"})
    return {"contract_sha256":digest(c),"envelope_sha256":digest(envelope),"references":accepted,"status":"CONTEXT_ONLY" if accepted else "NO_COMPATIBLE_CONTEXT","estimate":None,"decision":"NOT_EVALUATED","qualification":"BLOCKED"}
