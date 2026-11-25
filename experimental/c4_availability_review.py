"""Availability review: historical measurements unchanged; no numerical penalty."""
from d0_contract import digest
ROLES={"football":{"creator":["match_total","team_total","handicap","result","assists"],"finisher":["match_total","team_total","handicap","result","scorer"],"defender":["match_total","team_total","handicap","result"]},"nba":{"handler":["match_total","team_total","handicap","result","player_points"],"interior":["match_total","team_total","handicap","result","player_rebounds"],"defender":["match_total","team_total","handicap","result","player_points"]},"tennis":{"server":["match_total","team_total","handicap","result","aces","double_faults"],"returner":["match_total","team_total","handicap","result"]}}
def review(sport, configs, historical):
    rows=[]
    for c in configs:
        if c["availability"]=="available":continue
        role=c["role"]
        candidates=[x["person_id"] for x in configs if x["participant"]==c["participant"] and x["role"]==role and x["availability"]=="available"]
        rows.append({"participant":c["participant"],"person_id":c["person_id"],"role":role,"availability":c["availability"],"record_ids":c["record_ids"],"replacement_candidates":sorted(set(candidates)),"replacement_equivalence":"NOT_ESTABLISHED","families_to_review":ROLES[sport].get(role,[]),"effect":None})
    return {"historical_sha256":digest(historical),"current_capacity":"NOT_ESTABLISHED","dependencies":rows,"qualification":"BLOCKED"}
