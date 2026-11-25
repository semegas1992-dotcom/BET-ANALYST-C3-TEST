"""Independent arithmetic replay of E2 outputs using exact rational arithmetic."""
from fractions import Fraction
from math import isclose
from d0_contract import stamp,validate
def audit(d,report):
    if validate(d)!=report["input_sha256"]:raise ValueError("input fingerprint")
    issues=[];checks=0
    def check(actual,expected,label):
        nonlocal checks
        checks+=1
        ok=actual==expected if expected is None or isinstance(expected,(list,bool,int)) else isinstance(actual,(int,float)) and isclose(actual,float(expected),rel_tol=1e-12,abs_tol=1e-12)
        if not ok:issues.append(label)
    pairs={"target_rate":("target_for","shots_for"),"service_rate":("service_points_won","service_points_played"),"return_rate":("return_points_won","return_points_played")}
    fields={"football":{"shots_for","shots_against","target_for","target_against","target_rate"},"nba":{"points_for","points_against","rebounds","assists"},"tennis":{"service_points_won","service_points_played","return_points_won","return_points_played","service_rate","return_rate"}}
    key="side" if d["sport"]=="football" else "participant"
    participants=["home","away"] if key=="side" else d["participants"]
    if set(report["sensitivity"])!=set(participants):raise ValueError("participants")
    policy=report["policy"];excluded=report["declared_atypical"];context=report["context_filter"];window=report["window"]
    for p in participants:
        rows=sorted((o for o in d["observations"] if o[key]==p),key=lambda o:(stamp(o["event_end"]),o["id"]))
        groups={"all":rows,"recent":rows[-window:],"prior":rows[:-window],"matched":[o for o in rows if context and all(o.get("context",{}).get(k)==v for k,v in context.items())]}
        if set(report["sensitivity"][p])!=set(groups):raise ValueError("windows")
        for w,rr in groups.items():
            metrics=report["sensitivity"][p][w]
            if set(metrics)!=fields[d["sport"]]:raise ValueError("metrics")
            for f,m in metrics.items():
                valid=[]
                for o in rr:
                    s=o["stats"]
                    if f in pairs:
                        a,b=(s.get(k) for k in pairs[f])
                        if a is None or b is None or b<=0:continue
                    else:
                        a=s.get(f);b=1
                        if a is None:continue
                    valid.append((o["id"],a,b))
                reduced=[v for v in valid if v[0] not in excluded]
                def ratio(v):return Fraction(sum(x[1] for x in v),sum(x[2] for x in v)) if v else None
                full,clean=ratio(valid),ratio(reduced)
                eligible=len(rr);re=sum(o["id"] not in excluded for o in rr)
                cov=Fraction(len(valid),eligible) if eligible else None
                rc=Fraction(len(reduced),re) if re else None
                expected={"n":len(valid),"eligible":eligible,"ids":[v[0] for v in valid],"full":full,"coverage":cov,"reduced_n":len(reduced),"reduced_eligible":re,"reduced_coverage":rc,"without_declared_atypical":clean,"delta":clean-full if clean is not None and full is not None else None,"excluded_ids":[v[0] for v in valid if v[0] in excluded],"sample_gate":len(valid)>=policy["min_n"] and cov is not None and float(cov)>=policy["min_coverage"],"reduced_sample_gate":len(reduced)>=policy["min_n"] and rc is not None and float(rc)>=policy["min_coverage"],"numerator":sum(v[1] for v in valid) if f in pairs and valid else None,"denominator":sum(v[2] for v in valid) if f in pairs and valid else None}
                for k,v in expected.items():check(m[k],v,f"{p}:{w}:{f}:{k}")
    return {"checks":checks,"issues":issues,"passed":not issues}
