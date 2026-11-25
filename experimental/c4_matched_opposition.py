"""Synthetic matched-opposition descriptive contrasts, not forecasts."""
from math import isfinite
from statistics import mean

def contrast(rows, min_n=3):
    if type(min_n) is not int or min_n<3: raise ValueError("min_n")
    seen=set()
    groups={}
    for row in rows:
        key=(row["sport"],row["metric"],row["context"],row["opponent"])
        if row["sport"] not in ("football","nba","tennis"): raise ValueError("sport")
        side=row["side"]
        if side not in ("A","B"): raise ValueError("side")
        identity=(row["sport"],side,row["observation_id"],row["metric"])
        if identity in seen: raise ValueError("duplicate")
        seen.add(identity)
        value=row["value"]
        if type(value) not in (int,float) or not isfinite(value): raise ValueError("value")
        groups.setdefault(key,{"A":[],"B":[]})[side].append(value)
    output=[]
    for key,g in sorted(groups.items()):
        eligible=min(len(g["A"]),len(g["B"]))>=min_n
        output.append({"stratum":list(key),"counts":{s:len(v) for s,v in g.items()},
                       "contrast":mean(g["A"])-mean(g["B"]) if eligible else None,
                       "status":"DESCRIPTIVE_MATCHED" if eligible else "INSUFFICIENT"})
    return {"strata":output,"forecast":None,"dominant_trajectory":None,"qualification":"BLOCKED"}

def linked_contrast(rows, d, event, extra, records, min_n=3):
    """Check numeric and identity linkage; context labels remain supplied assertions."""
    from d0_contract import digest, stamp
    indicators={(i["observation_id"],i["metric"]):i for i in extra["indicators"]}
    observations={o["id"]:o for o in d["observations"]}
    links={o["observation_id"]:o for o in extra["observations"]}
    comparables={o["observation_id"]:o for o in extra["comparables"]}
    rec={r["id"]:r for r in records}
    evidence=[]
    context_issues=[]
    for row in rows:
        oid=row["observation_id"]
        i=indicators.get((oid,row["metric"]))
        link=links.get(oid)
        comp=comparables.get(oid)
        if not i or not link or not comp or oid not in observations:raise ValueError("unlinked opposition")
        if row["sport"]!=d["sport"] or row["side"] not in ("A","B") or link["participant"]!=event["participants"][("A","B").index(row["side"])]:raise ValueError("opposition identity")
        if row["value"]!=i["value"]:raise ValueError("opposition measurement")
        ids=sorted(set(i["record_ids"]+link["record_ids"]+comp["record_ids"]))
        if any(j not in rec or rec[j]["status"]!="Contrôlée" or not stamp(observations[oid]["event_end"])<=stamp(rec[j]["available_at"])<=stamp(rec[j]["captured_at"])<=stamp(d["cutoff"]) for j in ids):raise ValueError("opposition chronology")
        context_issues.append({"observation_id":oid,"opponent":row["opponent"],"context":row["context"],"status":"UNVERIFIED","issues":["OPPONENT_IDENTITY_UNVERIFIED","HISTORICAL_FORMAT_UNVERIFIED","CONTEXT_EQUIVALENCE_UNVERIFIED","REPRESENTATIVENESS_UNESTABLISHED"]})
        evidence.append({"observation_id":oid,"metric":row["metric"],"unit":i["unit"],"record_ids":ids})
    return {"result":contrast(rows,min_n),"evidence":evidence,"comparability":{"status":"NOT_ESTABLISHED","observations":context_issues,"sporting_estimate":None},"input_sha256":digest(rows),"provenance":"SYNTHETIC_MEASUREMENT_LINKED_CONTEXT_UNVERIFIED","qualification":"BLOCKED"}
