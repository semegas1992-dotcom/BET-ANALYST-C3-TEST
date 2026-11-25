"""Fictional settlement contracts; no commercial rules or predictions."""
from math import isfinite
from d0_contract import digest
RULES={
"football": {"result":("goals","regulation","team"),"handicap":("goals","regulation","team"),"match_total":("goals","regulation","match"),"team_total":("goals","regulation","team"),"scorer":("goals","regulation","person"),"assists":("assists","regulation","person")},
"nba":{"result":("points","including_overtime","team"),"handicap":("points","including_overtime","team"),"match_total":("points","including_overtime","match"),"team_total":("points","including_overtime","team"),"player_points":("points","including_overtime","person"),"player_rebounds":("rebounds","including_overtime","person")},
"tennis":{"result":("sets","completed_match","team"),"handicap":("games","completed_match","team"),"match_total":("games","completed_match","match"),"team_total":("games","completed_match","team"),"aces":("aces","completed_match","person"),"double_faults":("double_faults","completed_match","person")}}
def evaluate(event,extra,trajectories,contract,thresholds):
    sport=event["sport"];family=contract["family"]
    unit,period,kind=RULES[sport][family]
    subject=contract["subject"]
    if contract!={"event_sha256":digest(event),"sport":sport,"family":family,"unit":unit,"period":period,"subject":subject,"direction":contract["direction"]}:raise ValueError("scope")
    configs=[x for x in extra["configurations"] if x["person_id"]==subject]
    if kind=="match" and subject!="match" or kind=="team" and subject not in event["participants"] or kind=="person" and len(configs)!=1:raise ValueError("subject")
    direction=contract["direction"]
    if family=="result":
        if direction!="win" or thresholds!=[]:raise ValueError("result")
    elif direction not in ("over","under") or len(thresholds)<2 or any(type(t) not in (int,float) or not isfinite(t) or t%1!=.5 or (family!="handicap" and t<0) for t in thresholds) or len(set(thresholds))!=len(thresholds):raise ValueError("threshold")
    ts=sorted(thresholds)
    edges=[[b,a] if direction=="over" else [a,b] for a,b in zip(ts,ts[1:])]
    rows=[]
    for row in trajectories["trajectories"]:
        issues=set(row["issues"])
        if kind=="person":
            if configs[0]["availability"]!="available":issues.add("PERSON_UNRESOLVED")
            issues.add("INDIVIDUAL_ESTIMATE_MISSING")
        issues.add("EVENT_ESTIMATE_MISSING")
        rows.append({"assignment":row["assignment"],"issues":sorted(issues),"status":"BLOCKED"})
    return {"contract":contract,"thresholds":ts,"implications":edges,"trajectory_sha256":digest(trajectories),"assessment":rows,"status":"NOT_EVALUATED","engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
def audit(event,extra,trajectories,report):
    if report["trajectory_sha256"]!=digest(trajectories):raise ValueError("trajectory hash")
    c=report["contract"];ts=report["thresholds"]
    expected=evaluate(event,extra,trajectories,c,ts)
    if report!=expected:raise ValueError("replay mismatch")
    # Independently check nesting on integer observations around each threshold.
    for a,b in report["implications"]:
        for n in range(int(min(a,b))-2,int(max(a,b))+3):
            if (n>a if c["direction"]=="over" else n<a) and not (n>b if c["direction"]=="over" else n<b):raise ValueError("nesting")
    return {"passed":True,"checks":len(report["assessment"])+len(report["implications"]),"scope":"replay and integer nesting; not independent contract validation"}
