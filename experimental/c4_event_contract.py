"""Synthetic event scope and threshold nesting, not market evaluation."""
from math import isfinite
from d0_contract import digest
RULES={"football":("match_goals","goals","regulation"),"nba":("match_total","points","including_overtime"),"tennis":("match_total","games","completed_match")}
def compare(event,contract,thresholds):
    family,unit,period=RULES[event["sport"]]
    expected={"event_sha256":digest(event),"sport":event["sport"],"family":family,"unit":unit,"period":period,"subject":"match","direction":"over"}
    if contract!=expected:raise ValueError("incompatible event contract")
    if not isinstance(thresholds,list) or len(thresholds)<2 or any(type(t) not in (int,float) or not isfinite(t) or t<0 or t%1!=.5 for t in thresholds) or len(set(thresholds))!=len(thresholds):raise ValueError("half-unit thresholds required")
    ts=sorted(thresholds)
    return {"contract":expected,"thresholds":ts,"implications":[[b,a] for a,b in zip(ts,ts[1:])],"status":"NOT_EVALUATED","engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
def audit(event,report):
    c=report["contract"];ts=report["thresholds"]
    if c["event_sha256"]!=digest(event) or c["sport"]!=event["sport"] or tuple(c[k] for k in ("family","unit","period"))!=RULES[event["sport"]] or c["subject"]!="match" or c["direction"]!="over":raise ValueError("scope audit")
    if len(ts)<2 or any(type(t) not in (int,float) or not isfinite(t) or t<0 or t%1!=.5 for t in ts) or any(a>=b for a,b in zip(ts,ts[1:])) or report["implications"]!=[[ts[i],ts[i-1]] for i in range(1,len(ts))]:raise ValueError("nesting audit")
    if report["status"]!="NOT_EVALUATED" or report["engine_access"] is not False or report["publication"]!="BLOCKED" or report["qualification"]!="BLOCKED":raise ValueError("locks")
    return {"passed":True,"checks":len(ts)-1}
