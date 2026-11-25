"""Evidence-bound scenario review, not automatic causal inference."""
from c4_e2_quality import assess
from d0_contract import digest
from kraft_phase_guard import validate_phase
def review(d,window,reason,context,min_n,min_coverage,atypical_ids,mechanisms,scenarios):
    validate_phase({"engine_access":False,"mechanisms":mechanisms,"scenarios":scenarios})
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
            if v["excluded_ids"]:
                uncertain.append("atypical sensitivity")
                if not v["reduced_sample_gate"]:uncertain.append("reduced sample insufficient")
            if v["full"] is None:uncertain.append("missing measurement")
        reviewed[i]={"id":i,"support":list(a),"opposition":list(b),"observed":[refs[a]["full"],refs[b]["full"]],"observation_ids":[refs[a]["ids"],refs[b]["ids"]],"interpretation":m["interpretation"],"opponent_effect":m["opponent_effect"],"objection":m["objection"],"limitations":sorted(set(uncertain+["causality not established"])),"status":"BLOCKED" if uncertain else "HYPOTHESIS_ONLY"}
    result=[];seen=set()
    for s in scenarios:
        i=s["id"];links=s["mechanism_ids"]
        if not nonempty(i) or i in seen or not isinstance(links,list) or not links or len(set(links))!=len(links) or any(k not in reviewed for k in links):raise ValueError("scenario links")
        if any(not nonempty(s.get(k)) for k in ("condition","course","trigger","consequence","objection")):raise ValueError("scenario narrative")
        seen.add(i)
        result.append({"id":i,"mechanism_ids":links,**{k:s[k] for k in ("condition","course","trigger","consequence","objection")},"limitations":sorted({v for k in links for v in reviewed[k]["limitations"]}),"status":"BLOCKED" if any(reviewed[k]["status"]=="BLOCKED" for k in links) else "CONDITIONAL_HYPOTHESIS"})
    return {"schema":"C4_E3_REVIEW_V1","input_sha256":report["input_sha256"],"statistics_sha256":digest(report),"mechanisms":reviewed,"scenarios":result,"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED","automatic_reasoning":False}

def build(d,window,reason,context,min_n,min_coverage,atypical_ids,mechanisms,scenarios):
    stats=assess(d,window,reason,context,min_n,min_coverage,atypical_ids)
    validate_phase({"engine_access":False,"mechanisms":mechanisms,"scenarios":scenarios})
    evidence=stats["sensitivity"];out={};result=[]
    def nonempty(v):return isinstance(v,str) and bool(v.strip())
    for m in mechanisms:
        i=m["id"]
        if not nonempty(i) or i in out:raise ValueError("mechanism id")
        if any(not nonempty(m.get(k)) for k in ("interpretation","opponent_effect","objection")):raise ValueError("mechanism rationale")
        refs=m["refs"]
        if not isinstance(refs,list) or len(refs)<2:raise ValueError("opposition evidence")
        facts=[];participants=set();issues=set()
        for ref in refs:
            if not isinstance(ref,list) or len(ref)!=3:raise ValueError("reference")
            p,w,f=ref
            if p not in evidence or w not in evidence[p] or f not in evidence[p][w]:raise ValueError("unknown evidence")
            v=evidence[p][w][f];participants.add(p)
            if not v["sample_gate"]:issues.add("INSUFFICIENT_SAMPLE")
            if v["full"] is None:issues.add("MISSING_MEASUREMENT")
            if v["excluded_ids"]:
                if not v["reduced_sample_gate"]:issues.add("REDUCED_SAMPLE_INSUFFICIENT")
                if v["delta"] is None or v["delta"]!=0:issues.add("ATYPICAL_SENSITIVITY")
            facts.append({"ref":ref,"measurement":v})
        if len(participants)!=2:raise ValueError("both participants required")
        out[i]={"id":i,"facts":facts,"interpretation":m["interpretation"],"opponent_effect":m["opponent_effect"],"objection":m["objection"],"issues":sorted(issues),"status":"BLOCKED" if issues else "UNVERIFIED_HYPOTHESIS"}
    seen=set()
    for s in scenarios:
        i=s["id"];refs=s["mechanism_ids"]
        if not nonempty(i) or i in seen or not isinstance(refs,list) or not refs or len(set(refs))!=len(refs) or any(x not in out for x in refs):raise ValueError("scenario reference")
        seen.add(i)
        if any(not nonempty(s.get(k)) for k in ("condition","course","trigger","consequence","objection")):raise ValueError("scenario rationale")
        issues=sorted({x for ref in refs for x in out[ref]["issues"]})
        result.append({"id":i,"mechanism_ids":refs,**{k:s[k] for k in ("condition","course","trigger","consequence","objection")},"issues":issues,"status":"BLOCKED" if issues else "UNVERIFIED_HYPOTHESIS"})
    return {"schema":"C4_E3_SYNTHETIC_V1","input_sha256":stats["input_sha256"],"statistics_sha256":digest(stats),"mechanisms":out,"scenarios":result,"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED","sporting_analysis_complete":False}
