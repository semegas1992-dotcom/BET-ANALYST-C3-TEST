"""Synthetic structured report, not a sporting prediction."""
from football_pipeline_demo import analyze
from kraft_phase_guard import validate_phase
STATUSES=("Contrôlée","Provisoire","Non recherchée","Accessible, non extraite","Accès bloqué","Périmètre inadéquat","Non trouvée après recherche","Contradictoire")
def build_report(d):
    r=analyze(d)
    evidence={}
    for side,s in r["facts"].items():
        for period in ("advanced_season","advanced_last5"):
            for field,metric in s[period].items():
                rows=sorted((o for o in d["observations"] if o["side"]==side),key=lambda o:(o["event_end"],o["id"]))
                if period=="advanced_last5":rows=rows[-5:]
                evidence[f"{side}:{period}:{field}"]={"status":"Contrôlée" if not s["independent_check"]["issues"] else "Provisoire","scope":"synthetic arithmetic only","source":"synthetic_fixture","cutoff":d["cutoff"],"observation_ids":[o["id"] for o in rows if o["stats"].get(field) is not None],"metric":metric}
    missing={"status":"Non recherchée","reason":"synthetic experiment; external collection excluded"}
    blocks=[
        {"title":"Synthèse rapide","p2_pass":r["p2_pass"],"reading":"Non étayée","evidence_ids":list(evidence)},
        {"title":"Repères et données déterminantes","cutoff":d["cutoff"],"kickoff":d["kickoff"],"evidence_ids":list(evidence),"official_identity":missing},
        {"title":"Analyse sportive","descriptive_only":True,"evidence_ids":list(evidence),"tactics":missing},
        {"title":"Scénarios envisagés","scenarios":[],"reason":"insufficient sporting evidence","evidence_ids":[]},
        {"title":"Projection du déroulement","reason":"insufficient sporting evidence","evidence_ids":[]},
        {"title":"Marchés et lignes éventuelles","candidates":[],"reason":"insufficient sporting evidence","evidence_ids":[]},
        {"title":"Avis sportif final","decision":"ABSTENTION","scope":"technical hold, not sporting NO BET","data_quality":"synthetic arithmetic only","sporting_reading":"Non étayée","market_arguments":"Non étayés","evidence_ids":[]}]
    return validate_phase({"schema":"KRAFT_SYNTHETIC_REPORT_V1","input_sha256":r["input_sha256"],"engine_access":False,"synthetic":True,"p2_pass":r["p2_pass"],"p2_rejections":r["p2_rejections"],"evidence":evidence,"sections":blocks})
