"""Synthetic contextual summaries and conservative dependency propagation."""
from fractions import Fraction
from statistics import mean
from c4_context_contract import SEQUENCES
from d0_contract import digest
PAIRS={"football":{},"nba":{"points_per_possession":("points_for","possessions")},"tennis":{"first_serve_rate":("first_serve_won","first_serve_played"),"second_serve_rate":("second_serve_won","second_serve_played"),"break_rate":("break_points_won","break_points_played")}}
def summarize(d,event,extra):
    obs={o["id"]:o for o in d["observations"]}
    rows={i:{} for i in obs}
    for x in extra["indicators"]:
        rows[x["observation_id"]][x["metric"]]=x["value"]
    out={}
    for p in event["participants"]:
        ids=[i for i,o in obs.items() if o.get("side",o.get("participant"))==p]
        metrics={}
        for f in sorted({f for i in ids for f in rows[i]}):
            used=[i for i in ids if f in rows[i]]
            metrics[f]={"ids":used,"n":len(used),"eligible":len(ids),"mean":mean(rows[i][f] for i in used)}
        for label,(a,b) in PAIRS[d["sport"]].items():
            used=[]
            for i in ids:
                x,y=rows[i].get(a),rows[i].get(b)
                if x is None or y is None:continue
                if d["sport"]=="tennis" and x>y:raise ValueError("won exceeds played")
                if y>0:used.append(i)
            num=sum(rows[i][a] for i in used);den=sum(rows[i][b] for i in used)
            metrics[label]={"ids":used,"n":len(used),"eligible":len(ids),"numerator":num,"denominator":den,"ratio":num/den if den else None}
        out[p]=metrics
    return out
def audit(d,event,extra,summary):
    checks=0
    for p,metrics in summary.items():
        ids={o["id"] for o in d["observations"] if o.get("side",o.get("participant"))==p}
        for f,m in metrics.items():
            values={x["observation_id"]:Fraction(str(x["value"])) for x in extra["indicators"] if x["metric"]==f and x["observation_id"] in ids}
            if f in PAIRS[d["sport"]]:
                a,b=PAIRS[d["sport"]][f]
                aa={x["observation_id"]:Fraction(str(x["value"])) for x in extra["indicators"] if x["metric"]==a and x["observation_id"] in ids}
                bb={x["observation_id"]:Fraction(str(x["value"])) for x in extra["indicators"] if x["metric"]==b and x["observation_id"] in ids}
                used={i for i in aa.keys()&bb.keys() if bb[i]>0}
                n=sum((aa[i] for i in used),Fraction(0));den=sum((bb[i] for i in used),Fraction(0))
                if m["numerator"]!=float(n) or m["denominator"]!=float(den) or m["ratio"]!=(float(n/den) if den else None):raise ValueError("ratio audit")
            else:
                used=set(values)
                if m["mean"]!=float(sum(values.values())/len(values)):raise ValueError("mean audit")
            if set(m["ids"])!=used or m["n"]!=len(used) or m["eligible"]!=len(ids):raise ValueError("coverage audit")
            checks+=1
    return checks
def enrich(d,event,extra,context,doc,hypotheses):
    summary=summarize(d,event,extra);checks=audit(d,event,extra,summary)
    issues=[]
    if not doc["synthetic_documentary_gate"]:issues.append("DOCUMENTARY_GATE")
    if context["unlinked_observations"]:issues.append("UNLINKED_OBSERVATIONS")
    if any(not any(x["participant"]==p for x in extra["configurations"]) for p in event["participants"]):issues.append("CONFIGURATION_MISSING")
    if any(x["availability"] in ("uncertain","unknown","absent") for x in extra["configurations"]):issues.append("CONFIGURATION_UNRESOLVED")
    if not extra["comparables"]:issues.append("COMPARABLES_MISSING")
    sequences=[]
    for s in hypotheses["scenarios"]:
        m=hypotheses["mechanisms"][s["mechanism_ids"][0]]
        m["issues"]=sorted(set(m["issues"]+issues))
        m["status"]="BLOCKED" if m["issues"] else "UNVERIFIED_HYPOTHESIS"
        s["issues"]=list(m["issues"]);s["status"]=m["status"]
        for phase in SEQUENCES[d["sport"]]:
            sequences.append({"scenario_id":s["id"],"phase":phase,"condition":s["condition"],"status":s["status"],"issues":s["issues"],"scope":"conditional template; no predicted score or tactical inference"})
    return {"summary":summary,"audit_checks":checks,"context_sha256":digest(extra),"issues":issues,"sequences":sequences,"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
