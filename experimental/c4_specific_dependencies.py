"""Scoped synthetic dependencies; no causal or predictive certification."""
from c4_context_contract import SEQUENCES
RULES={"football":{"volume":("creator","defender","creation of shooting opportunities"),"target":("finisher","defender","quality of shooting opportunities")},"nba":{"scoring":("handler","defender","creation of scoring opportunities"),"rebounds":("interior","interior","contested rebound opportunities")},"tennis":{"serve":("server","returner","service pressure"),"return":("returner","server","return pressure")}}
def evaluate(d,event,extra,doc,hypotheses):
    ps=event["participants"];out={}
    obs={o["id"]:o for o in d["observations"]}
    links={x["observation_id"]:x for x in extra["observations"]}
    for mid,m in hypotheses["mechanisms"].items():
        idx,label=mid.split(":");a=ps[int(idx)];b=ps[1-int(idx)]
        ra,rb,effect=RULES[d["sport"]][label]
        issues=[];refs=[];comparables=[]
        if not doc["synthetic_documentary_gate"]:issues.append("DOCUMENTARY_GATE")
        for participant,role in ((a,ra),(b,rb)):
            configs=[x for x in extra["configurations"] if x["participant"]==participant and x["role"]==role]
            if not configs:issues.append("ROLE_MISSING:"+participant+":"+role)
            for x in configs:
                refs.extend(x["record_ids"])
                if x["availability"]!="available":issues.append("ROLE_UNRESOLVED:"+participant+":"+role)
            candidates=[x for x in extra["comparables"] if x["observation_id"] in links and links[x["observation_id"]]["participant"]==participant]
            if not candidates:issues.append("COMPARABLE_MISSING:"+participant)
            comparables.extend(candidates)
        for fact in m["facts"]:
            for oid in fact["measurement"]["ids"]:
                if oid not in links:issues.append("UNLINKED:"+oid)
                else:refs.extend(links[oid]["record_ids"])
        out[mid]={"participants":[a,b],"roles":[ra,rb],"effect_to_examine":effect,"record_ids":sorted(set(refs+[i for x in comparables for i in x["record_ids"]])),"comparables":comparables,"issues":sorted(set(issues)),"status":"BLOCKED" if issues else "UNVERIFIED_HYPOTHESIS"}
    sequences=[]
    for s in hypotheses["scenarios"]:
        dep=out[s["mechanism_ids"][0]]
        for phase in SEQUENCES[d["sport"]]:
            sequences.append({"scenario_id":s["id"],"phase":phase,"condition":s["condition"],"argument":"If the stated roles and historical context remain applicable, examine "+dep["effect_to_examine"],"opponent_response":"Check whether opposing "+dep["roles"][1]+" changes the interaction","turning_point":"Role availability or contrary observed interaction","objection":"Historical comparability does not establish causal effect","record_ids":dep["record_ids"],"status":dep["status"],"issues":dep["issues"]})
    return {"mechanisms":out,"sequences":sequences,"scope":"supplemental scoped hypotheses; global gate remains authoritative","engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
