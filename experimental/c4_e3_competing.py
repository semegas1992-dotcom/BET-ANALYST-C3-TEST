"""Conditional competing branches, not forecasts or verified tactics."""
from c4_e3 import build
CATALOG={"football":[("volume","shots_for","shots_against","volume de tirs"),("target","target_for","target_against","tirs cadrés")],"nba":[("scoring","points_for","points_against","production de points"),("rebounds","rebounds","rebounds","rebonds")],"tennis":[("serve","service_rate","return_rate","service face au retour"),("return","return_rate","service_rate","retour face au service")]}
def generate(d,window,reason,context,min_n,min_coverage,atypical_ids):
    p,q=["home","away"] if d["sport"]=="football" else d["participants"]
    mechanisms=[];scenarios=[];branches=[]
    for i,(a,b) in enumerate(((p,q),(q,p))):
        for label,f,g,desc in CATALOG[d["sport"]]:
            mid=f"{i}:{label}"
            refs=[[a,"recent",f],[b,"recent",g]]
            if context:refs.extend([[a,"matched",f],[b,"matched",g]])
            mechanisms.append({"id":mid,"refs":refs,"interpretation":f"Comparer {desc} de {a} et opposition de {b}","opponent_effect":"Interaction à examiner, non démontrée","objection":"Contexte et causalité non établis"})
            for state in ("holds","fails"):
                sid=mid+":"+state
                condition=f"{desc} de {a}: hypothèse {'confirmée' if state=='holds' else 'non confirmée'} en observation future"
                scenarios.append({"id":sid,"mechanism_ids":[mid],"condition":condition,"course":"Maintien du mécanisme" if state=="holds" else "Révision du mécanisme","trigger":"Observation future contraire à la condition","consequence":"Réexaminer les hypothèses liées","objection":"Aucun seuil ni probabilité calibrés"})
                branches.append({"id":sid,"group":mid,"condition_state":state})
    result=build(d,window,reason,context,min_n,min_coverage,atypical_ids,mechanisms,scenarios)
    for s,b in zip(result["scenarios"],branches):
        if s["id"]!=b["id"]:raise ValueError("branch order")
        s.update(group=b["group"],condition_state=b["condition_state"])
    check(result)
    result["generation"]="COMPETING_CONDITIONAL_TEMPLATES"
    return result
def check(report):
    groups={}
    for s in report["scenarios"]:
        g=s["group"];state=s["condition_state"]
        if state not in ("holds","fails") or state in groups.setdefault(g,set()):raise ValueError("duplicate or invalid branch")
        groups[g].add(state)
        if s["mechanism_ids"]!=[g] or g not in report["mechanisms"]:raise ValueError("branch link")
        m=report["mechanisms"][g]
        if s["issues"]!=m["issues"] or s["status"]!=m["status"]:raise ValueError("uncertainty propagation")
    if set(groups)!=set(report["mechanisms"]) or any(v!={"holds","fails"} for v in groups.values()):raise ValueError("incomplete branches")
    return True
