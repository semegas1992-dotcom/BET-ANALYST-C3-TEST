import os,json
from urllib.parse import urlencode
from datetime import datetime,timezone
from dunkapi_client import Budget,call
from dunk_enrichment import namekey,player_summary
from nba_history import request_json
from dunk_join import mapping

def candidate(b,p,mapped):
    if namekey(b["first_name"]+" "+b["last_name"])!=namekey(p["name"]):return False
    t=mapped.get(str(b["team"]["id"]))
    if not t or str(t["team_id"])!=str(p.get("team_id")):return False
    # Without birth date, require independent corroboration, not just name/team.
    for k in ("birth_date","jersey_number"):
        if b.get(k) is not None and p.get(k) is not None and str(b[k])!=str(p[k]):return False
    return any(b.get(k) not in (None,"") and p.get(k) not in (None,"") and str(b[k])==str(p[k]) for k in ("birth_date","jersey_number"))

def main():
    now=datetime.now(timezone.utc)
    key=os.environ["DUNK_KEY"]; bkey=os.environ["BDL_KEY"]
    budget=Budget("probe-budget.db")
    report={"engine_access":False,"status":"UNRESOLVED","publication":"BLOCKED_RIGHTS_NOT_CONFIRMED"}
    try:
        bdl=request_json("https://api.balldontlie.io/v1/teams",bkey)["data"]
        mapped={}
        def teams(d):
            mapped.update(mapping(bdl,d["teams"]))
            return {"mapped":len(mapped)}
        report["teams"]=call("list_teams",{"season":now.year+int(now.month>=7)},key,budget,inspect=teams)
        b=request_json("https://api.balldontlie.io/v1/players?"+urlencode({"search":"Jayson Tatum","per_page":100}),bkey)
        rows=b["data"]
        if b["meta"].get("next_cursor") or len(rows)!=1:raise ValueError("ambiguous BDL search")
        def profile(d):
            p=d["player"]
            report["field_names"]={"bdl":sorted(rows[0]),"dunk":sorted(p)}
            ok=candidate(rows[0],p,mapped)
            report["identity_status"]="CANDIDATE_MATCH" if ok else "UNRESOLVED"
            s=player_summary(d,"4065648",now,now.year+int(now.month>=7))
            return {"accepted_games":s["n"],"identity_status":report["identity_status"]}
        report["profile"]=call("get_player",{"player_id":"4065648"},key,budget,inspect=profile)
        if report["identity_status"]=="CANDIDATE_MATCH" and report["profile"]["summary"]["accepted_games"]>0 and len(mapped)==30:report["status"]="QUARANTINE_UNVERIFIED"
    except Exception as e:
        report.update(error_type=type(e).__name__,http_code=getattr(e,"code",None))
    with open("player-probe.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps(report))
    return int(report["status"]!="QUARANTINE_UNVERIFIED")
if __name__=="__main__":raise SystemExit(main())
