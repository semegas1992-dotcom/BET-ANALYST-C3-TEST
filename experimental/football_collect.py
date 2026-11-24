import os,json,time,hashlib
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
    if trace:time.sleep(7)
    with urlopen(Request(url,headers={"X-Auth-Token":key}),timeout=30) as response:
        data=json.load(response)
    trace.append({"path":path,"params":params,"observed":datetime.now(timezone.utc).isoformat(),"sha256":hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()})
    return data

def matches(data):
    rows=data["matches"]
    if not isinstance(rows,list) or data["resultSet"]["count"]!=len(rows):raise ValueError("count mismatch")
    if len({m["id"] for m in rows})!=len(rows):raise ValueError("duplicate match")
    return rows

def upcoming(rows,now,end):
    return [m for m in rows if m["status"]=="TIMED" and now<stamp(m["utcDate"])<=end and m["competition"]["code"] in LEAGUES and m["homeTeam"]["id"]!=m["awayTeam"]["id"]]

def history(rows,event,team,cutoff):
    out=[]
    for m in rows:
        if m["status"]!="FINISHED" or m["id"]==event["id"]:continue
        if m["competition"]["id"]!=event["competition"]["id"] or m["season"]["id"]!=event["season"]["id"]:continue
        if stamp(m["utcDate"]).date()>=cutoff.date():continue
        if not m.get("lastUpdated") or stamp(m["lastUpdated"])>cutoff:continue
        h,a=m["homeTeam"]["id"],m["awayTeam"]["id"]
        if h==a or team not in (h,a):continue
        s=m["score"]
        if s["duration"]!="REGULAR":continue
        x,y=s["fullTime"]["home"],s["fullTime"]["away"]
        if any(type(v) is not int or v<0 for v in (x,y)):continue
        out.append({"id":m["id"],"date":m["utcDate"],"home":team==h,"gf":x if team==h else y,"ga":y if team==h else x})
    return sorted(out,key=lambda x:stamp(x["date"]),reverse=True)

def stats(rows):
    n=len(rows)
    return {"n":n,"wins":sum(r["gf"]>r["ga"] for r in rows),"draws":sum(r["gf"]==r["ga"] for r in rows),"losses":sum(r["gf"]<r["ga"] for r in rows),"gf_mean":sum(r["gf"] for r in rows)/n if n else None,"ga_mean":sum(r["ga"] for r in rows)/n if n else None}

def main():
    now=datetime.now(timezone.utc);end=now+timedelta(hours=72)
    report={"source":"football-data.org","engine_access":False,"publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","status":"PARTIAL","trace":[],"dossiers":[]}
    try:
        key=os.environ.get("FOOTBALL_DATA_TOKEN")
        rows=matches(fetch("matches",{"dateFrom":now.date().isoformat(),"dateTo":end.date().isoformat()},key,report["trace"]))
        events=upcoming(rows,now,end)
        report["calendar_count"]=len(events)
        cache={}
        for e in sorted(events,key=lambda m:stamp(m["utcDate"]))[:8]:
            code=e["competition"]["code"];season=int(e["season"]["startDate"][:4]);k=(code,season)
            if k not in cache:cache[k]=matches(fetch("competitions/"+code+"/matches",{"season":season,"status":"FINISHED"},key,report["trace"]))
            sides={}
            for side in ("home","away"):
                hist=history(cache[k],e,e[side+"Team"]["id"],now)
                sides[side]={"season":stats(hist),"last5":stats(hist[:5]),"last10":stats(hist[:10]),"home":stats([r for r in hist if r["home"]]),"away":stats([r for r in hist if not r["home"]])}
            if datetime.now(timezone.utc)>=stamp(e["utcDate"]):continue
            report["dossiers"].append({"id":e["id"],"competition":code,"kickoff":e["utcDate"],"teams":[e["homeTeam"]["id"],e["awayTeam"]["id"]],"stats":sides,"engine_access":False})
        if report["dossiers"] and all(s["season"]["n"] for d in report["dossiers"] for s in d["stats"].values()):report["status"]="QUARANTINE_UNVERIFIED"
    except Exception as e:report.update(error_type=type(e).__name__,http_code=getattr(e,"code",None))
    with open("football-quarantine.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps({k:v for k,v in report.items() if k!="dossiers"}));print("Dossiers:",len(report["dossiers"]))
    return int(report["status"]!="QUARANTINE_UNVERIFIED")
if __name__=="__main__":raise SystemExit(main())
