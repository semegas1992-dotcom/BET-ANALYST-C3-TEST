"""Declared comparison templates; no causality or forecasts."""
from c4_e3 import build
CATALOG={"football":("shots_for","shots_against"),"nba":("points_for","points_against"),"tennis":("service_rate","return_rate")}
def prototype(d,window,reason,context,min_n,min_coverage,atypical_ids):
    p,q=["home","away"] if d["sport"]=="football" else d["participants"]
    f,g=CATALOG[d["sport"]]
    mechanisms=[]
    for i,(a,b) in enumerate(((p,q),(q,p))):
        mechanisms.append({"id":str(i),"refs":[[a,"all",f],[b,"all",g]],"interpretation":"Compare descriptive production and opposing concession or return","opponent_effect":"Conditional matchup hypothesis only","objection":"Context and causal relationship not established"})
    return build(d,window,reason,context,min_n,min_coverage,atypical_ids,mechanisms,[])
