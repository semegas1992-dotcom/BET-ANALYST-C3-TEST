import csv,io,json,hashlib
from datetime import datetime,timezone,date
from urllib.request import urlopen
from collections import Counter
from open_matchday_audit import FOLDERS,integer
from football_crosscheck import name
def qualify(row):
    out={}
    for side in ("home","away"):
        for stat in ("shots","target","corners","corners_1h","corners_2h","fouls","yellow","red"):
            k=side+"_"+stat
            try:v=integer(row.get(k))
            except ValueError:v=None
            out[k]={"value":v,"status":"INTERNAL_ONLY" if v is not None else "UNAVAILABLE"}
        def reject(keys):
            for k in keys:out[k]={"value":None,"status":"QUARANTINED_CONFLICT"}
        a,b=[out[side+"_"+s]["value"] for s in ("shots","target")]
        if a is not None and b is not None and b>a:reject([side+"_shots",side+"_target"])
        keys=[side+"_"+s for s in ("corners","corners_1h","corners_2h")]
        a,b,c=[out[k]["value"] for k in keys]
        if None not in (a,b,c) and a!=b+c:reject(keys)
    return out
def preview(primary,secondary,cutoff):
    idx={}
    for row in secondary:
        k=(row.get("date"),name(row.get("home")),name(row.get("away")))
        idx.setdefault(k,[]).append(row)
    counts=Counter();fields=Counter();exceptions=[]
    for m in primary:
        k=(m["utcDate"][:10],name(m["homeTeam"]["name"]),name(m["awayTeam"]["name"]))
        if date.fromisoformat(k[0])>=cutoff:counts["cutoff"]+=1;continue
        rows=idx.get(k,[])
        if len(rows)!=1:counts["unmatched" if not rows else "ambiguous"]+=1;continue
        row=rows[0]
        s=m["score"]["fullTime"]
        try:score=[integer(row.get("ft_home")),integer(row.get("ft_away"))]
        except ValueError:score=[]
        if score!=[s["home"],s["away"]]:counts["score_conflict"]+=1;continue
        counts["anchored"]+=1
        for key,v in qualify(row).items():
            fields[key+":"+v["status"]]+=1
            if v["status"]=="QUARANTINED_CONFLICT":exceptions.append({"id":m["id"],"field":key})
    return {"counts":dict(counts),"fields":dict(fields),"exceptions":exceptions,"accounting_ok":sum(counts.values())==len(primary),"goal_minutes":"QUARANTINED_PENDING_FORMAT","engine_access":False}
def main():
    import os
    from football_collect import fetch,matches
    now=datetime.now(timezone.utc);trace=[]
    report={"schema":"D0_PREVIEW_V1","engine_access":False,"publication":"BLOCKED_UPSTREAM_RIGHTS_NOT_CONFIRMED","cutoff":now.isoformat(),"leagues":{}}
    for code,folder in FOLDERS.items():
        url=f"https://raw.githubusercontent.com/oladeeayo/open-matchday/master/data/{folder}/results_2627.csv"
        try:
            with urlopen(url,timeout=25) as f:raw=f.read(5000001)
            if len(raw)>5000000:raise ValueError("size")
            rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
            primary=matches(fetch("competitions/"+code+"/matches",{"season":2026,"status":"FINISHED"},os.environ["FOOTBALL_DATA_TOKEN"],trace))
            report["leagues"][code]={**preview(primary,rows,now.date()),"sha256":hashlib.sha256(raw).hexdigest(),"source":url}
        except Exception as e:report["leagues"][code]={"error":type(e).__name__}
    report["trace"]=trace
    with open("football-d0-preview.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps(report))
    return int(any("error" in v or not v.get("accounting_ok") or not v.get("counts",{}).get("anchored") or v.get("counts",{}).get("score_conflict") for v in report["leagues"].values()))
if __name__=="__main__":raise SystemExit(main())
