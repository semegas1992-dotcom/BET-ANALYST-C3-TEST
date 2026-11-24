import csv,io,json,hashlib,os
from datetime import datetime,timezone,timedelta
from collections import Counter
from urllib.request import urlopen
from football_collect import fetch,matches,upcoming,history,stats,stamp
from football_d0_preview import qualify
from football_crosscheck import name
from open_matchday_audit import FOLDERS,integer

def join(primary,secondary,cutoff):
    idx={}
    for row in secondary:
        idx.setdefault((row.get("date"),name(row.get("home")),name(row.get("away"))),[]).append(row)
    accepted={};missing=[];counts=Counter()
    for m in primary:
        day=m["utcDate"][:10]
        if day>=cutoff.date().isoformat():counts["cutoff"]+=1;continue
        if not m.get("lastUpdated") or stamp(m["lastUpdated"])>cutoff:counts["cutoff"]+=1;continue
        h,a=m["homeTeam"],m["awayTeam"]
        keys={(day,name(h.get(hk)),name(a.get(ak))) for hk in ("name","shortName") for ak in ("name","shortName") if h.get(hk) and a.get(ak)}
        candidates={id(row):row for k in keys for row in idx.get(k,[])}
        if len(candidates)!=1:
            counts["ambiguous" if candidates else "unmatched"]+=1
            missing.append({"id":m["id"],"primary_names":[h.get("name"),h.get("shortName"),a.get("name"),a.get("shortName")],"same_date_names":[[r.get("home"),r.get("away")] for r in secondary if r.get("date")==day]})
            continue
        row=next(iter(candidates.values()))
        try:s=[integer(row.get("ft_home")),integer(row.get("ft_away"))]
        except ValueError:s=[]
        ft=m["score"]["fullTime"]
        if s!=[ft["home"],ft["away"]]:counts["conflict"]+=1;continue
        accepted[m["id"]]=qualify(row);counts["anchored"]+=1
    return accepted,dict(counts),missing

def aggregate(hist,accepted):
    out={}
    for stat in ("shots","target","corners","corners_1h","corners_2h","fouls","yellow","red"):
        for direction in ("for","against"):
            values=[]
            for h in hist:
                side="home" if h["home"]==(direction=="for") else "away"
                v=accepted.get(h["id"],{}).get(side+"_"+stat,{})
                if v.get("status")=="INTERNAL_ONLY":values.append(v["value"])
            out[stat+"_"+direction]={"n":len(values),"eligible":len(hist),"mean":sum(values)/len(values) if values else None,"status":"INTERNAL_ONLY" if values else "UNAVAILABLE"}
    return out

def main():
    now=datetime.now(timezone.utc);trace=[];key=os.environ["FOOTBALL_DATA_TOKEN"]
    report={"schema":"D0_ENRICHED_EXPERIMENTAL_V1","engine_access":False,"publication":"BLOCKED_UPSTREAM_RIGHTS_NOT_CONFIRMED","cutoff":now.isoformat(),"leagues":{},"dossier":None}
    try:
        events=upcoming(matches(fetch("matches",{"dateFrom":now.date().isoformat(),"dateTo":(now+timedelta(days=7)).date().isoformat()},key,trace)),now,now+timedelta(days=7))
        for code,folder in FOLDERS.items():
            url=f"https://raw.githubusercontent.com/oladeeayo/open-matchday/master/data/{folder}/results_2627.csv"
            with urlopen(url,timeout=25) as f:raw=f.read(5000001)
            if len(raw)>5000000:raise ValueError("size")
            secondary=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
            primary=matches(fetch("competitions/"+code+"/matches",{"season":2026,"status":"FINISHED"},key,trace))
            accepted,counts,missing=join(primary,secondary,now)
            report["leagues"][code]={"counts":counts,"missing":missing,"accounting_ok":sum(counts.values())==len(primary),"source":url,"sha256":hashlib.sha256(raw).hexdigest()}
            for e in sorted(events,key=lambda m:stamp(m["utcDate"])):
                if report["dossier"] or e["competition"]["code"]!=code or stamp(e["utcDate"])<=datetime.now(timezone.utc):continue
                sides={}
                for side in ("home","away"):
                    h=history(primary,e,e[side+"Team"]["id"],now)
                    sides[side]={"team_id":e[side+"Team"]["id"],"basic":stats(h),"advanced_season":aggregate(h,accepted),"advanced_last5":aggregate(h[:5],accepted)}
                if all(s["advanced_season"]["shots_for"]["n"]>=5 for s in sides.values()):
                    report["dossier"]={"id":e["id"],"kickoff":e["utcDate"],"competition":code,"sides":sides,"source_hash":report["leagues"][code]["sha256"],"engine_access":False,"limitations":["advanced statistics not externally verified","historical publication timestamps unknown","no injuries or lineups","goal minutes excluded","descriptive means not probabilities"]}
                    break
    except Exception as e:report["error"]=type(e).__name__
    report["trace"]=trace
    if report["dossier"] and stamp(report["dossier"]["kickoff"])<=datetime.now(timezone.utc):report["dossier"]=None
    with open("football-d0-enriched.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps({**report,"leagues":{k:{a:b for a,b in v.items() if a!="missing"} for k,v in report["leagues"].items()}}))
    return int("error" in report or not report["dossier"] or not all(v["accounting_ok"] for v in report["leagues"].values()))
if __name__=="__main__":raise SystemExit(main())
