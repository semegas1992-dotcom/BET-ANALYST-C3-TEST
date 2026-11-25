"""Synthetic descriptive context, not a forecast."""
from d0_contract import validate,stamp
from kraft_integration import run
from statistics import mean,pstdev,median
FIELDS={"football":("shots_for","shots_against","target_for","target_against"),"nba":("points_for","points_against","rebounds","assists"),"tennis":("service_points_won","service_points_played","return_points_won","return_points_played")}
def describe(d,window,reason,context):
    sha=validate(d)
    run(d)
    if type(window) is not int or window<1 or not isinstance(reason,str) or not reason.strip():raise ValueError("window rationale")
    sport=d["sport"];key="side" if sport=="football" else "participant"
    participants=["home","away"] if sport=="football" else d["participants"]
    allowed={"venue","surface","opponent_level","configuration"}
    if not isinstance(context,dict) or not set(context)<=allowed or any(not isinstance(v,str) or not v.strip() for v in context.values()):raise ValueError("context")
    def stats(rows,field):
        valid=[o for o in rows if o["stats"].get(field) is not None]
        v=[o["stats"][field] for o in valid]
        return {"eligible":len(rows),"n":len(v),"missing":len(rows)-len(v),"mean":mean(v) if v else None,"median":median(v) if v else None,"population_sd":pstdev(v) if v else None,"min":min(v) if v else None,"max":max(v) if v else None,"ids":[o["id"] for o in valid]}
    result={}
    for p in participants:
        rows=sorted([o for o in d["observations"] if o[key]==p],key=lambda o:(stamp(o["event_end"]),o["id"]))
        recent=rows[-window:];prior=rows[:-window]
        matched=[o for o in rows if context and all(o.get("context",{}).get(k)==v for k,v in context.items())]
        result[p]={}
        for field in FIELDS[sport]:
            a,b=stats(recent,field),stats(prior,field)
            result[p][field]={"all":stats(rows,field),"recent":a,"prior":b,"matched":stats(matched,field),"recent_minus_prior":a["mean"]-b["mean"] if a["n"] and b["n"] else None}
    return {"schema":"C4_E2_DESCRIPTIVE_V1","input_sha256":sha,"sport":sport,"window":window,"window_reason":reason,"context_filter":context,"metrics":result,"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED","scope":"synthetic descriptive only"}
