"""Synthetic descriptive prototype; not a KRAFT implementation or betting engine."""
from d0_contract import validate,digest
from football_demo_audit import audit_side
from kraft_phase_guard import validate_phase
from football_qualification_v5 import rejection_reasons
def analyze(d):
    fingerprint=validate(d)
    if d["sport"]!="football":raise ValueError("sport")
    sides={}
    for side in ("home","away"):
        rows=[o for o in d["observations"] if o["side"]==side]
        rows.sort(key=lambda o:(o["event_end"],o["id"]))
        sides[side]={}
        for period,rr in (("advanced_season",rows),("advanced_last5",rows[-5:])):
            fields={}
            for k in ("shots_for","shots_against","target_for","target_against"):
                vals=[o["stats"][k] for o in rr if o["stats"].get(k) is not None]
                if any(type(v) is not int or v<0 for v in vals):raise ValueError("invalid statistic")
                fields[k]={"n":len(vals),"eligible":len(rr),"sum":sum(vals),"mean":sum(vals)/len(vals) if vals else None}
            sides[side][period]=fields
        sides[side]["independent_check"]=audit_side(d["observations"],side,sides[side])
    reasons=rejection_reasons(sides)
    return validate_phase({"input_sha256":fingerprint,"engine_access":False,"synthetic":True,"facts":sides,"p2_rejections":reasons,"scenarios":[],"scenario_status":"insufficient evidence; no forced scenarios","p2_pass":not reasons,"market_comparison":{"status":"blocked","reason":"P2 or KRAFT implementation pending"},"decision":"ABSTENTION","decision_scope":"technical hold, not sporting NO BET"})
