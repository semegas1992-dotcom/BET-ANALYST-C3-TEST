import os,json,time,hashlib
from collections import Counter
from football_enrichment import enrich
from datetime import datetime,timezone,timedelta
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

BASE="https://api.football-data.org/v4/"
LEAGUES={"PL","PD","BL1","SA","FL1"}
def stamp(s):
    d=datetime.fromisoformat(s.replace("Z","+00:00"))
    if d.tzinfo is None:raise ValueError("timezone required")
    return d.astimezone(timezone.utc)

def fetch(path,params,key,trace):
    if not key:raise ValueError("missing token")
    url=BASE+path+"?"+urlencode(params)
    time.sleep(7)
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={"X-Auth-Token":key}),timeout=30) as response:
                data=json.load(response)
            break
        except HTTPError as e:
            code=e.code;e.close()
            if code not in (429,500,502,503,504) or attempt==2:raise
            time.sleep(60 if code==429 else 10*(attempt+1))
    trace.append({"path":path,"params":params,"observed":datetime.now(timezone.utc).isoformat(),"sha256":hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()})
    return data

def matches(data):
    rows=data["matches"]
    if not isinstance(rows,list) or data["resultSet"]["count"]!=len(rows):raise ValueError("count mismatch")
    if len({m["id"] for m in rows})!=len(rows):raise ValueError("duplicate match")
    return rows

def upcoming(rows,now,end):
    return [m for m in rows if m["status"]=="TIMED" and now<stamp(m["utcDate"])<=end and m["competition"]["code"] in LEAGUES and m["homeTeam"]["id"]!=m["awayTeam"]["id"]]

def history(rows,event,team,cutoff,multi=False):
    out=[]
    for m in rows:
        if m["status"]!="FINISHED" or m["id"]==event["id"]:continue
        if m["competition"]["id"]!=event["competition"]["id"] or (not multi and m["season"]["id"]!=event["season"]["id"]):continue
        if stamp(m["utcDate"]).date()>=cutoff.date():continue
        if not m.get("lastUpdated") or stamp(m["lastUpdated"])>cutoff:continue
        h,a=m["homeTeam"]["id"],m["awayTeam"]["id"]
        if h==a or team not in (h,a):continue
        s=m["score"]
        if s["duration"]!="REGULAR":continue
        x,y=s["fullTime"]["home"],s["fullTime"]["away"]
        if any(type(v) is not int or v<0 for v in (x,y)):continue
        ht=s.get("halfTime") or {}
        hx,hy=ht.get("home"),ht.get("away")
        valid=type(hx) is int and type(hy) is int and 0<=hx<=x and 0<=hy<=y
        out.append({"id":m["id"],"date":m["utcDate"],"home":team==h,"opponent":a if team==h else h,"gf":x if team==h else y,"ga":y if team==h else x,"ht_gf":(hx if team==h else hy) if valid else None,"ht_ga":(hy if team==h else hx) if valid else None})
    return sorted(out,key=lambda x:stamp(x["date"]),reverse=True)

def stats(rows):
    n=len(rows)
    return {"n":n,"wins":sum(r["gf"]>r["ga"] for r in rows),"draws":sum(r["gf"]==r["ga"] for r in rows),"losses":sum(r["gf"]<r["ga"] for r in rows),"gf_mean":sum(r["gf"] for r in rows)/n if n else None,"ga_mean":sum(r["ga"] for r in rows)/n if n else None}

def audit(report):
    issues=[]
    seen=set()
    for d in report["dossiers"]:
        if d["id"] in seen:issues.append("duplicate dossier")
        seen.add(d["id"])
        if d["engine_access"] is not False:issues.append("engine lock")
        if set(d["stats"])!={"home","away"}:issues.append("missing side")
        if len(d.get("teams",[]))!=2 or len(set(d["teams"]))!=2:issues.append("invalid teams");continue
        for side,s in d["stats"].items():
            h=s["history"]
            if s.get("enrichment")!=enrich(h,d["teams"][1 if side=="home" else 0]):issues.append("enrichment mismatch")
            if not h:issues.append("empty history")
            if len({r["id"] for r in h})!=len(h):issues.append("duplicate history")
            if any(stamp(r["date"])>=stamp(d["kickoff"]) for r in h):issues.append("future history")
            for k,rows in (("season",h),("last5",h[:5]),("last10",h[:10]),("home",[r for r in h if r["home"]]),("away",[r for r in h if not r["home"]])):
                if s[k]!=stats(rows):issues.append("statistics mismatch:"+k)
    return {"status":"PASS" if not issues and seen else "FAIL","issues":issues,"external_verification":"NOT_VERIFIED"}

def main():
    now=datetime.now(timezone.utc);end=now+timedelta(days=7)
    report={"source":"football-data.org","engine_access":False,"publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","status":"PARTIAL","trace":[],"dossiers":[]}
    try:
        key=os.environ.get("FOOTBALL_DATA_TOKEN")
        rows=matches(fetch("matches",{"dateFrom":now.date().isoformat(),"dateTo":end.date().isoformat()},key,report["trace"]))
        report["calendar_diagnostic"]={"raw_count":len(rows),"statuses":dict(Counter(m["status"] for m in rows)),"competitions":dict(Counter(m["competition"]["code"] for m in rows))}
        events=upcoming(rows,now,end)
        report["calendar_count"]=len(events)
        report["selected_limit"]=8
        report["deferred_count"]=max(0,len(events)-8)
        if not events:report["status"]="NO_ELIGIBLE_FIXTURES"
        cache={}
        previous={}
        report["historical_access"]={}
        report["cutoff"]=now.isoformat()
        for e in sorted(events,key=lambda m:stamp(m["utcDate"]))[:8]:
            code=e["competition"]["code"];season=int(e["season"]["startDate"][:4]);k=(code,season)
            if k not in cache:cache[k]=matches(fetch("competitions/"+code+"/matches",{"season":season,"status":"FINISHED"},key,report["trace"]))
            if k not in previous:
                try:
                    previous[k]=matches(fetch("competitions/"+code+"/matches",{"season":season-1,"status":"FINISHED"},key,report["trace"]))
                    report["historical_access"][code]="AVAILABLE"
                except HTTPError as exc:
                    if exc.code not in (403,404):raise
                    previous[k]=[]
                    report["historical_access"][code]="UNAVAILABLE"
            sides={}
            for side in ("home","away"):
                hist=history(cache[k],e,e[side+"Team"]["id"],now)
                opponent=e[("away" if side=="home" else "home")+"Team"]["id"]
                older=history(previous[k],e,e[side+"Team"]["id"],now,multi=True)
                sides[side]={"previous_h2h":[r for r in older if r["opponent"]==opponent],"enrichment":enrich(hist,e[("away" if side=="home" else "home")+"Team"]["id"]),"history":hist,"season":stats(hist),"last5":stats(hist[:5]),"last10":stats(hist[:10]),"home":stats([r for r in hist if r["home"]]),"away":stats([r for r in hist if not r["home"]])}
            if datetime.now(timezone.utc)>=stamp(e["utcDate"]):continue
            report["dossiers"].append({"id":e["id"],"competition":code,"kickoff":e["utcDate"],"teams":[e["homeTeam"]["id"],e["awayTeam"]["id"]],"stats":sides,"engine_access":False})
        report["audit"]=audit(report)
        if report["dossiers"] and report["audit"]["status"]=="PASS":report["status"]="QUARANTINE_UNVERIFIED"
    except Exception as e:report.update(error_type=type(e).__name__,http_code=getattr(e,"code",None))
    with open("football-quarantine.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps({k:v for k,v in report.items() if k!="dossiers"}));print("Dossiers:",len(report["dossiers"]))
    return int(report["status"]!="QUARANTINE_UNVERIFIED")
if __name__=="__main__":raise SystemExit(main())
