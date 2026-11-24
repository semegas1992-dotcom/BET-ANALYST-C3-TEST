import os,json,time,urllib.parse
from datetime import datetime,timezone,timedelta
from nba_history import BASE,stamp,request_json,collect,normalize,summarize

def select(rows,now,end):
    games,issues,seen=[],[],set()
    for g in rows:
        try:
            i=g["id"]
            if type(i) is not int or i<=0 or i in seen: raise ValueError("invalid or duplicate event")
            seen.add(i)
            tip=stamp(g["datetime"])
            if not now<tip<=end: continue
            if g.get("status") in ("Final","Postponed","Canceled","Cancelled"): continue
            if g.get("home_team_score",0) or g.get("visitor_team_score",0): continue
            h,a=g["home_team"]["id"],g["visitor_team"]["id"]
            season=g["season"]
            if any(type(v) is not int or v<=0 for v in (h,a,season)) or h==a: raise ValueError("invalid teams or season")
            games.append({"id":i,"tipoff":tip.isoformat(),"season":season,"home_id":h,"away_id":a,"home":g["home_team"]["full_name"],"away":g["visitor_team"]["full_name"],"postseason":g.get("postseason")})
        except (KeyError,TypeError,ValueError,AttributeError) as e:
            issues.append({"reason":str(e)})
    return sorted(games,key=lambda g:g["tipoff"]),issues

def discover(now,end,key,errors):
    rows,seen,cursor=[],set(),None
    for _ in range(30):
        q={"start_date":(now-timedelta(days=1)).date().isoformat(),"end_date":end.date().isoformat(),"per_page":100}
        if cursor is not None:q["cursor"]=cursor
        p=request_json(BASE+"?"+urllib.parse.urlencode(q),key,errors)
        if not isinstance(p.get("data"),list) or not isinstance(p.get("meta"),dict): raise ValueError("invalid calendar page")
        rows.extend(p["data"])
        cursor=p["meta"].get("next_cursor")
        time.sleep(13)
        if cursor is None:return rows
        if cursor in seen:raise ValueError("calendar cursor loop")
        seen.add(cursor)
    raise ValueError("calendar pagination incomplete")

def build(events,now,key,report,clock=lambda:datetime.now(timezone.utc)):
    cache=report["histories"]
    for event in events:
        if clock()>=stamp(event["tipoff"]):
            report["skipped"].append({"id":event["id"],"reason":"tipoff passed"});continue
        refs=[]
        for team in (event["home_id"],event["away_id"]):
            season=event["season"]
            ref=f"{season}:{team}"
            refs.append(ref)
            if ref in cache:continue
            trace,excluded=[],[]
            try:
                raw=collect(team,season,now,key,trace,report["request_errors"])
                rows,issues=normalize(raw,team,now,excluded,season)
                cache[ref]={"status":"COLLECTED","games":rows,"stats":summarize(rows),"issues":issues,"exclusions":excluded,"pages":trace,"received":len(raw),"accounting_ok":len(raw)==len(rows)+len(issues)+len(excluded),"external_completeness":"NOT_VERIFIED"}
            except Exception as e:
                cache[ref]={"status":"COLLECTION_ERROR","error_type":type(e).__name__,"http_code":getattr(e,"code",None),"pages":trace}
        if clock()>=stamp(event["tipoff"]):
            report["skipped"].append({"id":event["id"],"reason":"tipoff passed during collection"});continue
        ready=all(cache[r]["status"]=="COLLECTED" and cache[r]["accounting_ok"] and cache[r]["games"] and not cache[r]["issues"] for r in refs)
        report["dossiers"].append({"event":event,"history_refs":refs,"status":"QUARANTINE_UNVERIFIED" if ready else "INCOMPLETE","engine_access":False})

def main():
    now=datetime.now(timezone.utc)
    report={"schema":"BET_ANALYST_NBA_BATCH_V1","cutoff":now.isoformat(),"status":"QUARANTINE_UNVERIFIED","publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","engine_access":False,"histories":{},"dossiers":[],"skipped":[],"request_errors":[],"limitations":["Same UTC day excluded","Regular season history only","No external verification","No individual data"]}
    try:
        key=os.environ["BDL_KEY"]
        if not key:raise ValueError("missing secret")
        hours=int(os.getenv("WINDOW_HOURS","24"))
        if not 1<=hours<=48:raise ValueError("invalid window")
        end=now+timedelta(hours=hours)
        report["window_end"]=end.isoformat()
        events,issues=select(discover(now,end,key,report["request_errors"]),now,end)
        report["calendar_issues"]=issues
        report["selected_count"]=len(events)
        build(events,now,key,report)
        if issues or report["skipped"] or any(d["status"]=="INCOMPLETE" for d in report["dossiers"]):report["status"]="PARTIAL"
        elif not events:report["status"]="NO_UPCOMING_GAMES"
    except Exception as e:
        report["status"]="COLLECTION_ERROR"
        report["error_type"]=type(e).__name__
        report["http_code"]=getattr(e,"code",None)
    with open("nba-batch-quarantine.json","w") as f:json.dump(report,f,indent=2)
    print("Status:",report["status"],"Dossiers:",len(report["dossiers"]),"Histories:",len(report["histories"]))
    if report["status"] in ("PARTIAL","COLLECTION_ERROR"):raise SystemExit(1)

if __name__=="__main__":main()
