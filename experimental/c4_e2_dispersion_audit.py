"""Independent descriptive replay using rational moments."""
from fractions import Fraction
from math import sqrt,isclose
from d0_contract import validate,stamp
def audit(d,report):
    if validate(d)!=report["input_sha256"]:raise ValueError("fingerprint")
    fields={"football":("shots_for","shots_against","target_for","target_against"),"nba":("points_for","points_against","rebounds","assists"),"tennis":("service_points_won","service_points_played","return_points_won","return_points_played")}
    key="side" if d["sport"]=="football" else "participant"
    ps=["home","away"] if key=="side" else d["participants"]
    issues=[];checks=0
    def check(a,b,label):
        nonlocal checks
        checks+=1
        if not (isclose(a,float(b),rel_tol=1e-12,abs_tol=1e-12) if isinstance(b,(Fraction,float)) and type(a) in (int,float) else a==b):issues.append(label)
    w=report["window"];ctx=report["context_filter"]
    if type(w) is not int or w<1:raise ValueError("window")
    if set(report["metrics"])!=set(ps):raise ValueError("participants")
    for p in ps:
        rows=sorted([o for o in d["observations"] if o[key]==p],key=lambda o:(stamp(o["event_end"]),o["id"]))
        batches={"all":rows,"recent":rows[-w:],"prior":rows[:-w],"matched":[o for o in rows if ctx and all(o.get("context",{}).get(k)==v for k,v in ctx.items())]}
        if set(report["metrics"][p])!=set(fields[d["sport"]]):raise ValueError("fields")
        for f in fields[d["sport"]]:
            m=report["metrics"][p][f];means={}
            for name,rr in batches.items():
                valid=[o for o in rr if o["stats"].get(f) is not None];v=sorted(o["stats"][f] for o in valid);n=len(v)
                avg=Fraction(sum(v),n) if n else None;means[name]=avg
                variance=Fraction(sum(x*x for x in v),n)-avg*avg if n else None
                expected={"eligible":len(rr),"n":n,"missing":len(rr)-n,"mean":avg,"median":Fraction(v[(n-1)//2]+v[n//2],2) if n else None,"population_sd":sqrt(variance) if n else None,"min":v[0] if n else None,"max":v[-1] if n else None,"ids":[o["id"] for o in valid]}
                for k,b in expected.items():check(m[name][k],b,f"{p}:{f}:{name}:{k}")
            a,b=means["recent"],means["prior"]
            check(m["recent_minus_prior"],a-b if a is not None and b is not None else None,f"{p}:{f}:delta")
    return {"checks":checks,"issues":issues,"passed":not issues}
