"""Descriptive synthetic adapters. No forecasts or sporting recommendations."""
from d0_contract import validate,stamp
from statistics import mean
FIELDS={"nba":("points_for","points_against","rebounds","assists"),"tennis":("service_points_won","service_points_played","return_points_won","return_points_played")}
def build(d):
    sha=validate(d)
    sport=d["sport"]
    fields=FIELDS[sport]
    participants=d["participants"]
    if not isinstance(participants,list) or len(participants)!=2 or any(not isinstance(p,str) or not p.strip() for p in participants) or len(set(participants))!=2:
        raise ValueError("participants")
    evidence={}
    for o in d["observations"]:
        if o["participant"] not in participants or not isinstance(o["stats"],dict) or not set(o["stats"])<=set(fields):
            raise ValueError("observation scope")
        for v in o["stats"].values():
            if v is not None and (type(v) is not int or v<0):raise ValueError("invalid measurement")
        if sport=="tennis":
            for prefix in ("service","return"):
                w=o["stats"].get(prefix+"_points_won");n=o["stats"].get(prefix+"_points_played")
                if w is not None and n is not None and w>n:raise ValueError("denominator")
    for p in participants:
        rows=[o for o in d["observations"] if o["participant"]==p]
        rows.sort(key=lambda o:(stamp(o["event_end"]),o["id"]))
        for window,rr in (("all",rows),("last5",rows[-5:])):
            metrics=list(fields)
            if sport=="tennis":metrics+=["service_rate","return_rate"]
            for f in metrics:
                if f.endswith("_rate"):
                    prefix=f[:-5];pairs=[(o,o["stats"].get(prefix+"_points_won"),o["stats"].get(prefix+"_points_played")) for o in rr]
                    pairs=[(o,w,n) for o,w,n in pairs if w is not None and n is not None and n>0]
                    ids=[o["id"] for o,w,n in pairs];num=sum(w for o,w,n in pairs);den=sum(n for o,w,n in pairs)
                    metric={"n":len(ids),"eligible":len(rr),"numerator":num,"denominator":den,"ratio":num/den if den else None}
                else:
                    valid=[o for o in rr if o["stats"].get(f) is not None];vals=[o["stats"][f] for o in valid];ids=[o["id"] for o in valid]
                    metric={"n":len(vals),"eligible":len(rr),"sum":sum(vals),"mean":mean(vals) if vals else None,"min":min(vals) if vals else None,"max":max(vals) if vals else None}
                evidence[p+":"+window+":"+f]={"status":"Provisoire","scope":"synthetic descriptive only","source":"synthetic_fixture","cutoff":d["cutoff"],"observation_ids":ids,"metric":metric}
    titles=["Synthèse rapide","Repères et données déterminantes","Analyse sportive","Scénarios envisagés","Projection du déroulement","Marchés et lignes éventuelles","Avis sportif final"]
    sections=[{"title":t,"evidence_ids":list(evidence) if i<3 else [],"status":"DESCRIPTIVE_ONLY" if i<3 else "NOT_IMPLEMENTED"} for i,t in enumerate(titles)]
    sections[-1].update(decision="ABSTENTION",scope="technical hold, not sporting NO BET",data_quality="synthetic only",sporting_reading="Non étayée",market_arguments="Non étayés")
    return {"schema":"KRAFT_SYNTHETIC_REPORT_V1","input_sha256":sha,"engine_access":False,"synthetic":True,"evidence":evidence,"sections":sections}
