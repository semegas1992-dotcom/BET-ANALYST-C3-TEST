import os, json, time, urllib.request, urllib.parse
from datetime import datetime, timezone
from statistics import mean

BASE = "https://api.balldontlie.io/v1/games"

def stamp(s):
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("timezone required")
    return d.astimezone(timezone.utc)

def collect(team, season, cutoff, key):
    rows, cursors, cursor = [], set(), None
    for _ in range(30):
        q = {"team_ids[]": team, "seasons[]": season, "end_date": cutoff.date().isoformat(), "per_page": 100}
        if cursor is not None: q["cursor"] = cursor
        url = BASE + "?" + urllib.parse.urlencode(q)
        req = urllib.request.Request(url, headers={"Authorization": key, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as res:
            payload = json.load(res)
        rows.extend(payload["data"])
        cursor = payload.get("meta", {}).get("next_cursor")
        time.sleep(13)
        if cursor is None: return rows
        if cursor in cursors: raise ValueError("pagination loop")
        cursors.add(cursor)
    raise ValueError("pagination incomplete")

def normalize(rows, team, cutoff):
    accepted, seen, issues = [], set(), []
    for g in rows:
        try:
            i = g["id"]
            if type(i) is not int or i <= 0: raise ValueError("invalid id")
            if i in seen: raise ValueError("duplicate id")
            seen.add(i)
            h, a = g["home_team"]["id"], g["visitor_team"]["id"]
            if h == a or team not in (h,a): raise ValueError("team mismatch")
            if g.get("status") != "Final": continue
            if g.get("postseason") is True: continue
            d = stamp(g["datetime"])
            if d >= cutoff: continue
            # Same UTC day excluded: final status alone cannot prove completion before cutoff.
            if d.date() >= cutoff.date(): continue
            x,y = g["home_team_score"],g["visitor_team_score"]
            if any(type(v) is not int or v <= 0 for v in (x,y)) or x == y: raise ValueError("invalid final score")
            accepted.append({"id":i,"datetime":d.isoformat(),"home":h==team,"pf":x if h==team else y,"pa":y if h==team else x})
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            issues.append({"id":g.get("id") if isinstance(g,dict) else None,"reason":str(e)})
    return sorted(accepted,key=lambda g:g["datetime"],reverse=True),issues

def stats(rows):
    n=len(rows)
    return {"n":n,"wins":sum(g["pf"]>g["pa"] for g in rows),"losses":sum(g["pf"]<g["pa"] for g in rows),
            "pf":mean(g["pf"] for g in rows) if n else None,"pa":mean(g["pa"] for g in rows) if n else None,
            "margin":mean(g["pf"]-g["pa"] for g in rows) if n else None,
            "game_ids":[g["id"] for g in rows]}

def summarize(rows):
    return {"season":stats(rows),"L5":stats(rows[:5]),"L10":stats(rows[:10]),"L15":stats(rows[:15]),
            "home":stats([g for g in rows if g["home"]]),"away":stats([g for g in rows if not g["home"]])}

def main():
    cutoff=stamp(os.environ["CUTOFF"])
    now=datetime.now(timezone.utc)
    if cutoff > now: cutoff=now
    report={"schema":"BET_ANALYST_NBA_PREMATCH_V1","source":BASE,"cutoff":cutoff.isoformat(),"collected_at":now.isoformat(),
            "status":"QUARANTINE_UNVERIFIED","publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","engine_access":False,"teams":{},
            "limitations":["Same UTC day excluded conservatively","No independent verification","No injuries or individual statistics","Historical completeness not independently verified"]}
    try:
        key=os.environ["BDL_KEY"]
        if not key: raise ValueError("missing secret")
        event_id=int(os.environ["EVENT_ID"])
        req=urllib.request.Request(BASE+"/"+str(event_id),headers={"Authorization":key,"Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=30) as res:
            event=json.load(res)["data"]
        if event["id"]!=event_id or event["home_team"]["full_name"]!="Denver Nuggets" or event["visitor_team"]["full_name"]!="Dallas Mavericks": raise ValueError("event mismatch")
        tip=stamp(event["datetime"])
        if tip!=stamp(os.environ["CUTOFF"]) or now>=tip: raise ValueError("event time mismatch or expired")
        if event["season"]!=int(os.environ["SEASON"]): raise ValueError("season mismatch")
        report["event"]={"id":event_id,"tipoff":tip.isoformat(),"home":event["home_team"]["full_name"],"away":event["visitor_team"]["full_name"]}
        time.sleep(13)
        for team in (event["home_team"]["id"],event["visitor_team"]["id"]):
            rows,issues=normalize(collect(team,int(os.environ["SEASON"]),cutoff,os.environ["BDL_KEY"]),team,cutoff)
            report["teams"][str(team)]={"games":rows,"issues":issues,"stats":summarize(rows)}
    except Exception as e:
        report["status"]="COLLECTION_ERROR"
        report["error_type"]=type(e).__name__
    with open("nba-history-quarantine.json","w") as f: json.dump(report,f,indent=2)
    print("Status:",report["status"],"Teams:",len(report["teams"]))
    for team, data in report["teams"].items():
        print("Team",team,"accepted",len(data["games"]),"issues",len(data["issues"]))
    if report["status"]=="COLLECTION_ERROR": raise SystemExit(1)

if __name__=="__main__": main()
