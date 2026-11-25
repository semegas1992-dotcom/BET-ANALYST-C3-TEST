"""Independent replay of envelope aggregation; synthetic only."""
from c4_e2_quality import assess
from d0_contract import digest
def audit(d,report,windows,reason,context,min_n,min_coverage,atypical_ids,thresholds):
    reports=[assess(d,w,reason,context,min_n,min_coverage,atypical_ids) for w in windows]
    issues=[];checks=0
    def check(a,b,label):
        nonlocal checks
        checks+=1
        if a!=b:issues.append(label)
    check(report["input_sha256"],digest(d),"input")
    check(set(report["metrics"]),set(reports[0]["sensitivity"]),"participants")
    for p,groups in reports[0]["sensitivity"].items():
        check(set(report["metrics"][p]),set(groups["recent"]),"fields")
        for f in groups["recent"]:
            expected=[]
            for w,r in zip(windows,reports):
                for mode,group,value,gate in [("full","recent","full","sample_gate"),("reduced","recent","without_declared_atypical","reduced_sample_gate")]+([("matched","matched","full","sample_gate")] if context else []):
                    m=r["sensitivity"][p][group][f]
                    expected.append(dict(window=w,mode=mode,value=m[value],qualified=m[gate],report_sha256=digest(r)))
            m=report["metrics"][p][f];label=p+":"+f
            check(m["variants"],expected,label+":variants")
            vals=sorted(v["value"] for v in expected if v["qualified"] and v["value"] is not None)
            complete=len(vals)==len(expected)
            check(m["complete"],complete,label+":complete")
            check(m["descriptive_envelope"],[vals[0],vals[-1]] if vals else [None,None],label+":envelope")
            t=thresholds.get(p,{}).get(f)
            state="NOT_REQUESTED" if t is None else "BLOCKED" if not complete else "ALL_AT_OR_ABOVE" if all(v>=t for v in vals) else "ALL_BELOW" if all(v<t for v in vals) else "SENSITIVE"
            check(m["threshold"],t,label+":threshold")
            check(m["threshold_state"],state,label+":state")
            check(m["conditional_estimate"],expected[0]["value"] if complete else None,label+":baseline")
    return {"passed":not issues,"checks":checks,"issues":issues}
