"""Independent structural replay of scoped dependencies."""
from c4_context_contract import SEQUENCES
def audit(d,event,extra,doc,hypotheses,report):
    ms=report["mechanisms"];ps=event["participants"]
    if set(ms)!=set(hypotheses["mechanisms"]):raise ValueError("mechanism coverage")
    roles={"football":{"volume":["creator","defender"],"target":["finisher","defender"]},"nba":{"scoring":["handler","defender"],"rebounds":["interior","interior"]},"tennis":{"serve":["server","returner"],"return":["returner","server"]}}
    links={x["observation_id"]:x for x in extra["observations"]}
    for mid,m in ms.items():
        idx,label=mid.split(":");idx=int(idx);ordered=[ps[idx],ps[1-idx]]
        original=hypotheses["mechanisms"][mid];issues=set(original["issues"]);refs=set()
        if not doc["synthetic_documentary_gate"]:issues.add("DOCUMENTARY_GATE")
        for participant,role in zip(ordered,roles[d["sport"]][label]):
            rows=[x for x in extra["configurations"] if (x["participant"],x["role"])==(participant,role)]
            if not rows:issues.add("ROLE_MISSING:"+participant+":"+role)
            if any(x["availability"]!="available" for x in rows):issues.add("ROLE_UNRESOLVED:"+participant+":"+role)
            for x in rows:refs.update(x["record_ids"])
            comps=[x for x in extra["comparables"] if links.get(x["observation_id"],{}).get("participant")==participant]
            if not comps:issues.add("COMPARABLE_MISSING:"+participant)
            for x in comps:refs.update(x["record_ids"])
        for fact in original["facts"]:
            for oid in fact["measurement"]["ids"]:
                if oid not in links:issues.add("UNLINKED:"+oid)
                else:refs.update(links[oid]["record_ids"])
        if m["participants"]!=ordered or m["roles"]!=roles[d["sport"]][label] or m["issues"]!=sorted(issues) or m["record_ids"]!=sorted(refs) or m["status"]!=("BLOCKED" if issues else "UNVERIFIED_HYPOTHESIS"):raise ValueError("dependency replay")
    scenarios={s["id"]:s for s in hypotheses["scenarios"]}
    expected={(i,p) for i in scenarios for p in SEQUENCES[d["sport"]]}
    rows=report["sequences"]
    if len(rows)!=len(expected) or {(x["scenario_id"],x["phase"]) for x in rows}!=expected:raise ValueError("sequence coverage")
    for x in rows:
        s=scenarios[x["scenario_id"]];m=ms[s["mechanism_ids"][0]]
        if any(x[k]!=m[k] for k in ("issues","status","record_ids")) or x["branch"]!=s["condition_state"]:raise ValueError("sequence propagation")
    for i in scenarios:
        if len({x["argument"] for x in rows if x["scenario_id"]==i})!=len(SEQUENCES[d["sport"]]):raise ValueError("phase differentiation")
    return {"passed":True,"checks":len(ms)+len(rows),"scope":"structural replay only"}
