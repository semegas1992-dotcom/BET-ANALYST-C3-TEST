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
