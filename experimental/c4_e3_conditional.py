"""Sport-specific conditional templates; no inferred causality or forecast."""
from c4_e3 import build
CATALOG={
"football":[("volume","shots_for","shots_against","volume de tirs"),("accuracy","target_for","target_against","tirs cadrés")],
"nba":[("scoring","points_for","points_against","production de points")],
"tennis":[("serve_return","service_rate","return_rate","opposition service-retour")]}
def generate(d,window,reason,context,min_n,min_coverage,atypical_ids):
    p,q=["home","away"] if d["sport"]=="football" else d["participants"]
    mechanisms=[];scenarios=[]
    for index,(a,b) in enumerate(((p,q),(q,p))):
        for label,f,g,description in CATALOG[d["sport"]]:
            i=f"{index}:{label}"
            mechanisms.append({"id":i,"refs":[[a,"recent",f],[b,"recent",g]],"interpretation":f"Comparer {description} pour {a} face à {b}","opponent_effect":f"Hypothèse conditionnelle: {a} impose sa production face à {b}","objection":"Les mesures historiques ne démontrent ni causalité ni avantage futur."})
            scenarios.append({"id":i+":conditional","mechanism_ids":[i],"condition":f"Si {a} impose effectivement sa production face à {b}","course":f"Examiner la persistance de {description}","trigger":"Modification observée de la configuration ou de la résistance adverse","consequence":"Réexaminer le mécanisme et ses limites","objection":"Aucune probabilité ni direction future déduite des seules moyennes."})
    result=build(d,window,reason,context,min_n,min_coverage,atypical_ids,mechanisms,scenarios)
    result["generation"]="CONDITIONAL_TEMPLATES_ONLY"
    return result
