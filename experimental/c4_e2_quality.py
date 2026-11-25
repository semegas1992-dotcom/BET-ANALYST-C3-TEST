"""Synthetic sensitivity; thresholds are explicit experimental inputs."""
from c4_e2 import describe
from d0_contract import stamp
from statistics import mean,median
def assess(d,window,reason,context,min_n,min_coverage,atypical_ids):
    base=describe(d,window,reason,context)
    if type(min_n) is not int or min_n<1 or type(min_coverage) not in (int,float) or not 0<min_coverage<=1:raise ValueError("policy")
    known={o["id"] for o in d["observations"]}
    if not isinstance(atypical_ids,dict) or not set(atypical_ids)<=known or any(not isinstance(v,str) or not v.strip() for v in atypical_ids.values()):raise ValueError("exclusion rationale")
    ratios={"football":{"target_rate":("target_for","shots_for")},"tennis":{"service_rate":("service_points_won","service_points_played"),"return_rate":("return_points_won","return_points_played")},"nba":{}}
    def summary(rows,fn):
        vals=[(o["id"],fn(o)) for o in rows];valid=[(i,v) for i,v in vals if v is not None]
        def calc(items):
            if not items:return None
            if isinstance(items[0][1],tuple):return sum(v[0] for i,v in items)/sum(v[1] for i,v in items)
            return mean(v for i,v in items)
        n=len(valid);coverage=n/len(rows) if rows else None
        clean=[(i,v) for i,v in valid if i not in atypical_ids]
        full=calc(valid);reduced=calc(clean)
        reduced_eligible=len([o for o in rows if o["id"] not in atypical_ids])
        reduced_coverage=len(clean)/reduced_eligible if reduced_eligible else None
        return {"n":n,"eligible":len(rows),"coverage":coverage,"ids":[i for i,v in valid],"full":full,"without_declared_atypical":reduced,"excluded_ids":[i for i,v in valid if i in atypical_ids],"delta":reduced-full if reduced is not None and full is not None else None,"reduced_n":len(clean),"reduced_eligible":reduced_eligible,"reduced_coverage":reduced_coverage,"reduced_sample_gate":len(clean)>=min_n and reduced_coverage is not None and reduced_coverage>=min_coverage,"sample_gate":n>=min_n and coverage is not None and coverage>=min_coverage,"numerator":sum(v[0] for i,v in valid) if valid and isinstance(valid[0][1],tuple) else None,"denominator":sum(v[1] for i,v in valid) if valid and isinstance(valid[0][1],tuple) else None}
    key="side" if d["sport"]=="football" else "participant"
    out={}
    for p,metrics in base["metrics"].items():
        rows=sorted([o for o in d["observations"] if o[key]==p],key=lambda o:(stamp(o["event_end"]),o["id"]))
        batches={"all":rows,"recent":rows[-window:],"prior":rows[:-window],"matched":[o for o in rows if context and all(o.get("context",{}).get(k)==v for k,v in context.items())]}
        out[p]={}
        for name,rr in batches.items():
            result={f:summary(rr,lambda o,f=f:o["stats"].get(f)) for f in metrics}
            for label,(num,den) in ratios[d["sport"]].items():
                def pair(o):
                    a,b=o["stats"].get(num),o["stats"].get(den)
                    return (a,b) if a is not None and b is not None and b>0 else None
                result[label]=summary(rr,pair)
            out[p][name]=result
    base.update(sensitivity=out,policy={"min_n":min_n,"min_coverage":min_coverage,"calibrated":False},declared_atypical=atypical_ids,representativeness_verified=False)
    return base
