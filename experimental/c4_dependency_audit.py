"""Separate structural replay of scoped dependency output."""
from c4_context_contract import SEQUENCES
def audit(d,event,extra,doc,hypotheses,result):
    roles={"football":{"volume":("creator","defender"),"target":("finisher","defender")},"nba":{"scoring":("handler","defender"),"rebounds":("interior","interior")},"tennis":{"serve":("server","returner"),"return":("returner","server")}}
    if set(result["mechanisms"])!=set(hypotheses["mechanisms"]):raise ValueError("mechanism coverage")
    links={x["observation_id"]:x for x in extra["observations"]}
    for key,m in hypotheses["mechanisms"].items():
        i,label=key.split(":");a,b=event["participants"][int(i)],event["participants"][1-int(i)]
        expected=set(m["issues"]);refs=set()
        if not doc["synthetic_documentary_gate"]:expected.add("DOCUMENTARY_GATE")
        for p,role in zip((a,b),roles[d["sport"]][label]):
            rows=[x for x in extra["configurations"] if (x["participant"],x["role"])==(p,role)]
            if not rows:expected.add("ROLE_MISSING:"+p+":"+role)
            if any(x["availability"]!="available" for x in rows):expected.add("ROLE_UNRESOLVED:"+p+":"+role)
            refs.update(i for x in rows for i in x["record_ids"])
            cs=[x for x in extra["comparables"] if links.get(x["observation_id"],{}).get("participant")==p]
            if not cs:expected.add("COMPARABLE_MISSING:"+p)
            refs.update(i for x in cs for i in x["record_ids"])
        for oid in {i for f in m["facts"] for i in f["measurement"]["ids"]}:
            if oid not in links:expected.add("UNLINKED:"+oid)
            else:refs.update(links[oid]["record_ids"])
        if any(refs.intersection(c["record_ids"]) for c in doc["contradictions"]):expected.add("LINKED_CONTRADICTION")
        row=result["mechanisms"][key]
        if row["issues"]!=sorted(expected) or row["record_ids"]!=sorted(refs) or row["status"]!=("BLOCKED" if expected else "UNVERIFIED_HYPOTHESIS"):raise ValueError("dependency audit")
    expected={(s["id"],p) for s in hypotheses["scenarios"] for p in SEQUENCES[d["sport"]]}
    rows=result["sequences"]
    if len(rows)!=len(expected) or {(s["scenario_id"],s["phase"]) for s in rows}!=expected:raise ValueError("sequence coverage")
    for s in hypotheses["scenarios"]:
        rr=[x for x in rows if x["scenario_id"]==s["id"]];m=result["mechanisms"][s["mechanism_ids"][0]]
        if len({x["argument"] for x in rr})!=len(rr) or any(x["issues"]!=m["issues"] or x["status"]!=m["status"] or x["record_ids"]!=m["record_ids"] for x in rr):raise ValueError("sequence audit")
    return {"passed":True,"checks":len(result["mechanisms"])+len(rows)}
