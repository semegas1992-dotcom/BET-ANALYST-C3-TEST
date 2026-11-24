import os, json, time, hashlib, urllib.request, urllib.parse
from datetime import datetime, timezone
from statistics import mean
from urllib.error import HTTPError, URLError
from email.utils import parsedate_to_datetime

BASE = "https://api.balldontlie.io/v1/games"

def stamp(s):
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("timezone required")
    return d.astimezone(timezone.utc)

def request_json(url, key, events=None):
    for attempt in range(1, 4):
        try:
            req=urllib.request.Request(url, headers={"Authorization":key,"Accept":"application/json"})
            with urllib.request.urlopen(req, timeout=30) as res:
                return json.load(res)
        except (HTTPError, URLError, TimeoutError) as exc:
            code=exc.code if isinstance(exc, HTTPError) else None
            retryable=code is None or code in (429,500,502,503,504)
            delay=(60 if code==429 else 15)*2**(attempt-1)
            header=exc.headers.get("Retry-After") if isinstance(exc,HTTPError) and exc.headers else None
            if header:
                try:
                    delay=max(delay,float(header))
                except ValueError:
                    try: delay=max(delay,(parsedate_to_datetime(header)-datetime.now(timezone.utc)).total_seconds())
                    except (ValueError,TypeError,OverflowError): pass
            retry=retryable and attempt<3 and delay<=120
            if events is not None:
                events.append({"attempt":attempt,"http_code":code,"error_type":type(exc).__name__,"retry":retry,"delay_seconds":delay if retry else None,"at":datetime.now(timezone.utc).isoformat()})
            if not retry: raise
            time.sleep(delay)

def collect(team, season, cutoff, key, trace=None, events=None):
    rows, cursors, cursor = [], set(), None
    for _ in range(30):
        q = {"team_ids[]": team, "seasons[]": season, "end_date": cutoff.date().isoformat(), "per_page": 100}
        if cursor is not None: q["cursor"] = cursor
        url = BASE + "?" + urllib.parse.urlencode(q)
        payload = request_json(url,key,events)
        if not isinstance(payload.get("data"), list) or not isinstance(payload.get("meta"), dict): raise ValueError("invalid page structure")
        if trace is not None:
            trace.append({"query":q.copy(),"received_at":datetime.now(timezone.utc).isoformat(),"count":len(payload["data"]),"next_cursor":payload["meta"].get("next_cursor"),"sha256":hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()})
        rows.extend(payload["data"])
        cursor = payload.get("meta", {}).get("next_cursor")
        time.sleep(13)
        if cursor is None: return rows
        if cursor in cursors: raise ValueError("pagination loop")
        cursors.add(cursor)
    raise ValueError("pagination incomplete")

def normalize(rows, team, cutoff, exclusions=None, season=None):
    def exclude(g, reason):
        if exclusions is not None: exclusions.append({"id":g.get("id"),"reason":reason})
    accepted, seen, issues = [], set(), []
    for g in rows:
        try:
            i = g["id"]
            if type(i) is not int or i <= 0: raise ValueError("invalid id")
            if i in seen: raise ValueError("duplicate id")
            seen.add(i)
            h, a = g["home_team"]["id"], g["visitor_team"]["id"]
            if h == a or team not in (h,a): raise ValueError("team mismatch")
            if season is not None and g.get("season") != season: raise ValueError("season mismatch")
            if g.get("status") != "Final":
                exclude(g,"not_final"); continue
            if g.get("postseason") is True:
                exclude(g,"postseason"); continue
            d = stamp(g["datetime"])
            if d >= cutoff:
                exclude(g,"at_or_after_cutoff"); continue
            # Same UTC day excluded: final status alone cannot prove completion before cutoff.
            if d.date() >= cutoff.date():
                exclude(g,"same_utc_day"); continue
            x,y = g["home_team_score"],g["visitor_team_score"]
            if any(type(v) is not int or v <= 0 for v in (x,y)) or x == y: raise ValueError("invalid final score")
            accepted.append({"id":i,"datetime":d.isoformat(),"home":h==team,"opponent_id":a if h==team else h,"opponent_name":(g["visitor_team"] if h==team else g["home_team"]).get("full_name"),"pf":x if h==team else y,"pa":y if h==team else x})
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            issues.append({"id":g.get("id") if isinstance(g,dict) else None,"reason":str(e)})
    return sorted(accepted,key=lambda g:g["datetime"],reverse=True),issues

def stats(rows):
    n=len(rows)
    return {"n":n,"wins":sum(g["pf"]>g["pa"] for g in rows),"losses":sum(g["pf"]<g["pa"] for g in rows),
            "pf":mean(g["pf"] for g in rows) if n else None,"pa":mean(g["pa"] for g in rows) if n else None,
            "total":mean(g["pf"]+g["pa"] for g in rows) if n else None,
            "margin":mean(g["pf"]-g["pa"] for g in rows) if n else None,
            "game_ids":[g["id"] for g in rows]}

def summarize(rows):
    return {"season":stats(rows),"L5":stats(rows[:5]),"L10":stats(rows[:10]),"L15":stats(rows[:15]),
            "home":stats([g for g in rows if g["home"]]),"away":stats([g for g in rows if not g["home"]])}

def main():
    cutoff=stamp(os.environ["CUTOFF"])
    now=datetime.now(timezone.utc)
    if cutoff > now: cutoff=now
    report={"schema":"BET_ANALYST_NBA_PREMATCH_V2","source":BASE,"cutoff":cutoff.isoformat(),"collected_at":now.isoformat(),
            "status":"QUARANTINE_UNVERIFIED","publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","engine_access":False,"teams":{},"request_errors":[],
            "limitations":["Same UTC day excluded conservatively","No independent verification","No injuries or individual statistics","Historical completeness not independently verified"]}
    try:
        key=os.environ["BDL_KEY"]
        if not key: raise ValueError("missing secret")
        event_id=int(os.environ["EVENT_ID"])
        report["stage"]="event"
        event=request_json(BASE+"/"+str(event_id),key,report["request_errors"])["data"]
        if event["id"]!=event_id or event["home_team"]["full_name"]!="Denver Nuggets" or event["visitor_team"]["full_name"]!="Dallas Mavericks": raise ValueError("event mismatch")
        tip=stamp(event["datetime"])
        if tip!=stamp(os.environ["CUTOFF"]) or now>=tip: raise ValueError("event time mismatch or expired")
        if event["season"]!=int(os.environ["SEASON"]): raise ValueError("season mismatch")
        report["event"]={"id":event_id,"tipoff":tip.isoformat(),"home":event["home_team"]["full_name"],"away":event["visitor_team"]["full_name"]}
        time.sleep(13)
        for team in (event["home_team"]["id"],event["visitor_team"]["id"]):
            report["stage"]="team:"+str(team)
            trace, exclusions = [], []
            raw=collect(team,int(os.environ["SEASON"]),cutoff,key,trace,report["request_errors"])
            rows,issues=normalize(raw,team,cutoff,exclusions,int(os.environ["SEASON"]))
            report["teams"][str(team)]={"games":rows,"issues":issues,"exclusions":exclusions,"stats":summarize(rows),"pages":trace,"received":len(raw),"pagination_complete":True,"external_completeness":"NOT_VERIFIED","accounting_ok":len(raw)==len(rows)+len(issues)+len(exclusions)}
    except Exception as e:
        report["status"]="COLLECTION_ERROR"
        report["error_type"]=type(e).__name__
        report["http_code"]=e.code if isinstance(e,HTTPError) else None
    with open("nba-history-quarantine.json","w") as f: json.dump(report,f,indent=2)
    print("Status:",report["status"],"Teams:",len(report["teams"]))
    for team, data in report["teams"].items():
        print("Team",team,"accepted",len(data["games"]),"issues",len(data["issues"]))
    if report["status"]=="COLLECTION_ERROR": raise SystemExit(1)

if __name__=="__main__": main()
