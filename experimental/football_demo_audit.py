"""Independent descriptive recomputation from synthetic observations."""
from statistics import mean
def audit_side(observations,side,reported):
    rows=sorted((o for o in observations if o["side"]==side),key=lambda o:(o["event_end"],o["id"]),reverse=True)
    issues=[];checks=0
    for period,rr in (("advanced_season",rows),("advanced_last5",rows[:5])):
        for field in ("shots_for","shots_against","target_for","target_against"):
            vals=[]
            for row in rr:
                v=row["stats"].get(field)
                if v is not None:vals.append(v)
            expected={"n":len(vals),"eligible":len(rr),"sum":sum(vals),"mean":mean(vals) if vals else None}
            for key,value in expected.items():
                checks+=1
                if reported[period][field].get(key)!=value:issues.append(f"{period}:{field}:{key}")
    return {"checks":checks,"issues":issues}
