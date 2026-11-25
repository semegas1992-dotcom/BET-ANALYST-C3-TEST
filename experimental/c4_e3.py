"""Evidence-bound scenario review, not automatic causal inference."""
from c4_e2_quality import assess
from d0_contract import digest
def review(d,window,reason,context,min_n,min_coverage,atypical_ids,mechanisms,scenarios):
    report=assess(d,window,reason,context,min_n,min_coverage,atypical_ids)
    refs={}
    for participant,windows in report["sensitivity"].items():
        for w,metrics in windows.items():
            for metric,v in metrics.items():
                refs[(participant,w,metric)]=v
    reviewed={}
    def nonempty(v):return isinstance(v,str) and bool(v.strip())
    for m in mechanisms:
        i=m["id"]
        if not nonempty(i) or i in reviewed:raise ValueError("mechanism id")
        if any(not nonempty(m.get(k)) for k in ("interpretation","opponent_effect","objection")):raise ValueError("mechanism narrative")
        a,b=tuple(m["support"]),tuple(m["opposition"])
        if a not in refs or b not in refs or a[0]==b[0]:raise ValueError("opposition references")
        uncertain=[]
        for ref in (a,b):
            v=refs[ref]
            if not v["sample_gate"]:uncertain.append("insufficient sample")
            if v["excluded_ids"]:uncertain.append("atypical sensitivity")
            if v["full"] is None:uncertain.append("missing measurement")
        reviewed[i]={"id":i,"support":list(a),"opposition":list(b),"observed":[refs[a]["full"],refs[b]["full"]],"observation_ids":[refs[a]["ids"],refs[b]["ids"]],"interpretation":m["interpretation"],"opponent_effect":m["opponent_effect"],"objection":m["objection"],"limitations":sorted(set(uncertain+["causality not established"])),"status":"HYPOTHESIS_ONLY"}
    result=[];seen=set()
    for s in scenarios:
        i=s["id"];links=s["mechanism_ids"]
        if not nonempty(i) or i in seen or not isinstance(links,list) or not links or len(set(links))!=len(links) or any(k not in reviewed for k in links):raise ValueError("scenario links")
        if any(not nonempty(s.get(k)) for k in ("condition","course","trigger","consequence","objection")):raise ValueError("scenario narrative")
        seen.add(i)
        result.append({"id":i,"mechanism_ids":links,**{k:s[k] for k in ("condition","course","trigger","consequence","objection")},"limitations":sorted({v for k in links for v in reviewed[k]["limitations"]}),"status":"CONDITIONAL_HYPOTHESIS"})
    return {"schema":"C4_E3_REVIEW_V1","input_sha256":report["input_sha256"],"statistics_sha256":digest(report),"mechanisms":reviewed,"scenarios":result,"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED","automatic_reasoning":False}
