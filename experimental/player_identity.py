from datetime import date
from dunk_enrichment import namekey,player_summary

def identity(bdl,dunk,team_map):
    """Canonical inputs only; provider-specific schema adapters must be qualified."""
    matches=[]
    for p in dunk:
        if namekey(p["name"])!=namekey(bdl["name"]):continue
        if not bdl.get("birth_date") or not p.get("birth_date"):continue
        if date.fromisoformat(bdl["birth_date"])!=date.fromisoformat(p["birth_date"]):continue
        if str(team_map.get(str(bdl["team_id"])))!=str(p["team_id"]):continue
        matches.append(p)
    if len(matches)!=1:return {"status":"UNRESOLVED","engine_access":False}
    return {"status":"CANDIDATE_MATCH","bdl_id":str(bdl["id"]),"dunk_id":str(matches[0]["id"]),"engine_access":False}

def qualify(profile,match,cutoff,season):
    if match.get("status")!="CANDIDATE_MATCH":return {"status":"UNRESOLVED","engine_access":False}
    summary=player_summary(profile,match["dunk_id"],cutoff,season)
    return {"status":"QUARANTINE_UNVERIFIED","identity":match,"summary":summary,"engine_access":False}
