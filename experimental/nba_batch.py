import os,json,time,urllib.parse,hashlib
from datetime import datetime,timezone,timedelta
from nba_history import BASE,stamp,request_json,collect,normalize,summarize

from nba_enrichment import grouped,distribute,context

def select(rows,now,end):
    games,issues,seen=[],[],set()
    for g in rows:
        try:
            i=g["id"]
            if type(i) is not int or i<=0 or i in seen: raise ValueError("invalid or duplicate event")
            seen.add(i)
            tip=stamp(g["datetime"])
            if not now<tip<=end: continue
            if g.get("postponed") is True: continue
            if g.get("status") in ("Final","Postponed","Canceled","Cancelled"): continue
            if g.get("home_team_score",0) or g.get("visitor_team_score",0): continue
            h,a=g["home_team"]["id"],g["visitor_team"]["id"]
            season=g["season"]
            if any(type(v) is not int or v<=0 for v in (h,a,season)) or h==a: raise ValueError("invalid teams or season")
            games.append({"id":i,"tipoff":tip.isoformat(),"season":season,"home_id":h,"away_id":a,"home":g["home_team"]["full_name"],"away":g["visitor_team"]["full_name"],"postseason":g.get("postseason")})
        except (KeyError,TypeError,ValueError,AttributeError) as e:
            issues.append({"reason":str(e)})
    return sorted(games,key=lambda g:g["tipoff"]),issues

def discover(now,end,key,errors,trace=None,partial=None):
    rows,seen,cursor=([] if partial is None else partial),set(),None
    for _ in range(30):
        q={"start_date":(now-timedelta(days=1)).date().isoformat(),"end_date":end.date().isoformat(),"per_page":100}
        if cursor is not None:q["cursor"]=cursor
        p=request_json(BASE+"?"+urllib.parse.urlencode(q),key,errors)
        if not isinstance(p.get("data"),list) or not isinstance(p.get("meta"),dict): raise ValueError("invalid calendar page")
        if trace is not None: trace.append({"payload":p,"query":q.copy(),"count":len(p["data"]),"next_cursor":p["meta"].get("next_cursor"),"received_at":datetime.now(timezone.utc).isoformat(),"sha256":hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",",":")).encode()).hexdigest()})
        rows.extend(p["data"])
        cursor=p["meta"].get("next_cursor")
        time.sleep(16)
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
            trace,excluded,partial=[],[],[]
            try:
                raw=collect(team,season,now,key,trace,report["request_errors"],partial)
                rows,issues=normalize(raw,team,now,excluded,season)
                cache[ref]={"status":"COLLECTED","pagination_complete":True,"games":rows,"stats":summarize(rows),"issues":issues,"exclusions":excluded,"pages":trace,"received":len(raw),"accounting_ok":len(raw)==len(rows)+len(issues)+len(excluded),"external_completeness":"NOT_VERIFIED"}
            except Exception as e:
                cache[ref]={"status":"COLLECTION_ERROR","error_type":type(e).__name__,"http_code":getattr(e,"code",None),"pages":trace,"partial_rows":partial,"pagination_complete":False}
        if clock()>=stamp(event["tipoff"]):
            report["skipped"].append({"id":event["id"],"reason":"tipoff passed during collection"});continue
        ready=all(cache[r]["status"]=="COLLECTED" and cache[r]["accounting_ok"] and cache[r]["games"] and not cache[r]["issues"] for r in refs)
        report["dossiers"].append({"event":event,"history_refs":refs,"status":"QUARANTINE_UNVERIFIED" if ready else "INCOMPLETE","engine_access":False})

def build_grouped(events,now,key,report,clock=lambda:datetime.now(timezone.utc)):
    groups={}
    for e in events:groups.setdefault(e["season"],set()).update((e["home_id"],e["away_id"]))
    report["group_pages"]={}
    for season,teams in groups.items():
        trace,partial=[],[]
        group={"pages":trace,"teams":sorted(teams)}
        report["group_pages"][str(season)]=group
        try:
            raw=grouped(teams,season,now,key,trace,report["request_errors"],partial)
            split=distribute(raw,teams)
            group.update(status="COLLECTED",received=len(raw))
            for team,items in split.items():
                excluded=[]
                rows,issues=normalize(items,team,now,excluded,season)
                report["histories"][f"{season}:{team}"]={"status":"COLLECTED","pagination_complete":True,"games":rows,"stats":summarize(rows),"issues":issues,"exclusions":excluded,"received":len(items),"accounting_ok":len(items)==len(rows)+len(issues)+len(excluded),"group_ref":str(season),"external_completeness":"NOT_VERIFIED"}
        except Exception as e:
            group.update(status="COLLECTION_ERROR",partial_rows=partial,error_type=type(e).__name__)
            for team in teams:report["histories"].pop(f"{season}:{team}",None)
    build(events,now,key,report,clock)
    for d in report["dossiers"]:
        if d["status"]!="QUARANTINE_UNVERIFIED":continue
        e=d["event"]
        d["context"]={side:context(report["histories"][ref]["games"],e["tipoff"],e[other]) for side,ref,other in zip(("home","away"),d["history_refs"],("away_id","home_id"))}
    report["api_metrics"]={"successful_pages":len(report["calendar_pages"])+sum(len(g["pages"]) for g in report["group_pages"].values())+sum(len(h.get("pages",[])) for h in report["histories"].values()),"retry_events":len(report["request_errors"]),"http_429":sum(e["http_code"]==429 for e in report["request_errors"])}

def reciprocity(histories):
    issues=[]
    for ref,h in histories.items():
        if h["status"]!="COLLECTED":continue
        season,team=ref.split(":")
        for g in h["games"]:
            other=histories.get(f"{season}:{g.get('opponent_id')}")
            if not other or other["status"]!="COLLECTED":continue
            matches=[x for x in other["games"] if x["id"]==g["id"]]
            if len(matches)!=1:
                issues.append(ref+": missing reciprocal game "+str(g["id"]));continue
            x=matches[0]
            if (g["pf"],g["pa"],g["home"],g["datetime"],int(team))!=(x["pa"],x["pf"],not x["home"],x["datetime"],x.get("opponent_id")):issues.append(ref+": reciprocal mismatch "+str(g["id"]))
            p,q=g.get("periods",{}),x.get("periods",{})
            if p.get("status")!=q.get("status") or (p.get("status")=="CONSISTENT" and (p["pf"]!=q["pa"] or p["pa"]!=q["pf"])):issues.append(ref+": reciprocal periods "+str(g["id"]))
    return issues

def verify_pages(pages):
    return all("payload" in p and hashlib.sha256(json.dumps(p["payload"],sort_keys=True,separators=(",",":")).encode()).hexdigest()==p["sha256"] and len(p["payload"]["data"])==p["count"] and p["payload"]["meta"].get("next_cursor")==p["next_cursor"] for p in pages)

def audit(report):
    issues=[]
    cutoff=stamp(report["cutoff"])
    histories=report["histories"]
    for ref,h in histories.items():
        if h["status"]!="COLLECTED":continue
        rows=h["games"]
        if not h.get("accounting_ok") or h["received"]!=len(rows)+len(h["issues"])+len(h["exclusions"]):issues.append(ref+": accounting")
        if "group_ref" in h:
            group=report.get("group_pages",{}).get(h["group_ref"],{})
            pages=group.get("pages",[])
            if not pages or pages[-1]["next_cursor"] is not None or sum(p["count"] for p in pages)!=group.get("received") or int(ref.split(":")[1]) not in group.get("teams",[]):issues.append(ref+": group pagination")
        elif sum(p["count"] for p in h["pages"])!=h["received"] or not h["pages"] or h["pages"][-1]["next_cursor"] is not None:issues.append(ref+": pagination")
        if any(stamp(g["datetime"]).date()>=cutoff.date() for g in rows):issues.append(ref+": cutoff")
        if len({g["id"] for g in rows})!=len(rows):issues.append(ref+": duplicate")
        if summarize(rows)!=h["stats"]:issues.append(ref+": statistics")
    issues.extend(reciprocity(histories))
    ids=set()
    for d in report["dossiers"]:
        e=d["event"]
        expected=[f'{e["season"]}:{e[k]}' for k in ("home_id","away_id")]
        if d["history_refs"]!=expected or any(r not in histories for r in expected):issues.append("invalid history reference")
        if e["id"] in ids:issues.append("duplicate dossier")
        ids.add(e["id"])
        if d.get("engine_access") is not False:issues.append("engine access")
        if d.get("status")=="QUARANTINE_UNVERIFIED" and "context" not in d:issues.append("missing context")
        if "context" in d and all(r in histories and histories[r]["status"]=="COLLECTED" for r in expected):
            expected_context={side:context(histories[ref]["games"],e["tipoff"],e[other]) for side,ref,other in zip(("home","away"),expected,("away_id","home_id"))}
            if d["context"]!=expected_context:issues.append("context mismatch")
    if report.get("engine_access") is not False:issues.append("engine access")
    if report.get("selected_count")!=len(report["dossiers"])+len(report["skipped"]):issues.append("event accounting")
    pages=report.get("calendar_pages",[])
    if not pages or pages[-1]["next_cursor"] is not None or sum(p["count"] for p in pages)!=report.get("calendar_received"):issues.append("calendar pagination")
    if report.get("schema")=="BET_ANALYST_NBA_BATCH_V4":
        traces=[report.get("calendar_pages",[])]+[g["pages"] for g in report.get("group_pages",{}).values()]+[h.get("pages",[]) for h in histories.values()]
        if not all(verify_pages(p) for p in traces):issues.append("page integrity")
    return {"status":"PASS" if not issues else "FAIL","issues":issues,"external_verification":"NOT_VERIFIED"}

def main():
    now=datetime.now(timezone.utc)
    report={"schema":"BET_ANALYST_NBA_BATCH_V4","cutoff":now.isoformat(),"status":"QUARANTINE_UNVERIFIED","publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","engine_access":False,"histories":{},"dossiers":[],"skipped":[],"request_errors":[],"limitations":["Same UTC day excluded","Regular season history only","No external verification","No individual data"]}
    try:
        key=os.environ["BDL_KEY"]
        if not key:raise ValueError("missing secret")
        hours=int(os.getenv("WINDOW_HOURS","24"))
        if not 1<=hours<=48:raise ValueError("invalid window")
        end=now+timedelta(hours=hours)
        report["window_end"]=end.isoformat()
        report["calendar_pages"]=[]
        report["calendar_partial"]=[]
        raw=discover(now,end,key,report["request_errors"],report["calendar_pages"],report["calendar_partial"])
        report["calendar_received"]=len(raw)
        del report["calendar_partial"]
        events,issues=select(raw,now,end)
        report["calendar_issues"]=issues
        report["selected_count"]=len(events)
        build_grouped(events,now,key,report)
        if issues or report["skipped"] or any(d["status"]=="INCOMPLETE" for d in report["dossiers"]):report["status"]="PARTIAL"
        elif not events:report["status"]="NO_UPCOMING_GAMES"
        report["audit"]=audit(report)
        if report["audit"]["status"]=="FAIL":report["status"]="PARTIAL"
    except Exception as e:
        report["status"]="COLLECTION_ERROR"
        report["error_type"]=type(e).__name__
        report["http_code"]=getattr(e,"code",None)
    with open("nba-batch-quarantine.json","w") as f:json.dump(report,f,indent=2)
    print("Status:",report["status"],"Dossiers:",len(report["dossiers"]),"Histories:",len(report["histories"]))
    if report["status"] in ("PARTIAL","COLLECTION_ERROR"):raise SystemExit(1)

if __name__=="__main__":main()
