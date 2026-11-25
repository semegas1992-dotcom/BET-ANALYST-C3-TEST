"""Independent checks of scope output and conservative uncertainty propagation."""
from d0_contract import digest
def audit(event,extra,trajectories,report):
    c=report["contract"];sport=event["sport"];family=c["family"]
    periods={"football":"regulation","nba":"including_overtime","tennis":"completed_match"}
    units={"football":"goals","nba":"points","tennis":"games"}
    individual={"scorer":"goals","assists":"assists","player_points":"points","player_rebounds":"rebounds","aces":"aces","double_faults":"double_faults"}
    unit=individual.get(family, "sets" if sport=="tennis" and family=="result" else units[sport])
    if c["event_sha256"]!=digest(event) or c["sport"]!=sport or c["period"]!=periods[sport] or c["unit"]!=unit:raise ValueError("scope")
    if family=="match_total":
        if c["subject"]!="match":raise ValueError("match subject")
    elif family in individual:
        if sum(x["person_id"]==c["subject"] for x in extra["configurations"])!=1:raise ValueError("person")
    elif c["subject"] not in event["participants"]:raise ValueError("participant")
    if report["trajectory_sha256"]!=digest(trajectories) or len(report["assessment"])!=len(trajectories["trajectories"]):raise ValueError("coverage")
    for t,m in zip(trajectories["trajectories"],report["assessment"]):
        expected=set(t["issues"])|{"EVENT_ESTIMATE_MISSING"}
        if family in individual:
            expected.add("INDIVIDUAL_ESTIMATE_MISSING")
            if any(x["person_id"]==c["subject"] and x["availability"]!="available" for x in extra["configurations"]):expected.add("PERSON_UNRESOLVED")
        if m["assignment"]!=t["assignment"] or set(m["issues"])!=expected or m["status"]!="BLOCKED":raise ValueError("propagation")
    if report["engine_access"] is not False or report["publication"]!="BLOCKED" or report["qualification"]!="BLOCKED":raise ValueError("locks")
    return {"passed":True,"checks":len(report["assessment"]),"scope":"independent scope and propagation checks"}
