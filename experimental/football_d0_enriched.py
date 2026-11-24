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
    accepted={};missing=[];counts=Counter();used=set()
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
        if id(row) in used:counts["ambiguous"]+=1;continue
        used.add(id(row))
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
            out[stat+"_"+direction]={"n":len(values),"eligible":len(hist),"sum":sum(values),"mean":sum(values)/len(values) if values else None,"status":"INTERNAL_ONLY" if values else "UNAVAILABLE"}
    return out

def audit_dossier(d):
    issues=[]
    if not d:return {"pass":False,"issues":["no dossier"]}
    if d.get("engine_access") is not False:issues.append("engine lock")
    if set(d["sides"])!={"home","away"}:issues.append("sides")
    for side,s in d["sides"].items():
        if s.get("independent_check",{}).get("checks")!=32 or s.get("independent_check",{}).get("issues")!=[]:issues.append("observation audit")
        for period in ("advanced_season","advanced_last5"):
            for k,v in s[period].items():
                n=v["n"];eligible=v["eligible"]
                if not 0<=n<=eligible:issues.append(side+":"+period+":"+k+":count")
                if eligible!=(s["basic"]["n"] if period=="advanced_season" else min(5,s["basic"]["n"])):issues.append("denominator")
                if v["mean"]!=(v["sum"]/n if n else None):issues.append("mean")
                if n==0 and v["sum"]!=0:issues.append("empty sum")
    return {"pass":not issues,"issues":issues,"scope":"aggregate arithmetic only; source observations not independently verified"}
def independent_check(hist,accepted,aggregates):
    from statistics import mean
    issues=[];checks=0;bias={}
    for period,rows in (("advanced_season",hist),("advanced_last5",hist[:5])):
        for field,v in aggregates[period].items():
            stat,direction=field.rsplit("_",1)
            observations=[]
            for row in rows:
                side=("home" if row["home"] else "away") if direction=="for" else ("away" if row["home"] else "home")
                entry=accepted.get(row["id"],{}).get(side+"_"+stat,{})
                if entry.get("status")=="INTERNAL_ONLY":observations.append(entry["value"])
            checks+=1
            if (len(observations),len(rows),sum(observations),mean(observations) if observations else None)!=(v["n"],v["eligible"],v["sum"],v["mean"]):issues.append(period+":"+field)
        covered=[r for r in rows if accepted.get(r["id"],{}).get(("home" if r["home"] else "away")+"_shots",{}).get("status")=="INTERNAL_ONLY"]
        ids={r["id"] for r in covered}
        absent=[r for r in rows if r["id"] not in ids]
        def profile(rs):
            return {"n":len(rs),"home_share":mean([int(r["home"]) for r in rs]) if rs else None,"gf_mean":mean([r["gf"] for r in rs]) if rs else None,"ga_mean":mean([r["ga"] for r in rs]) if rs else None,"win_share":mean([int(r["gf"]>r["ga"]) for r in rs]) if rs else None}
        bias[period]={"covered":profile(covered),"missing":profile(absent),"representativeness":"NOT_ESTABLISHED"}
    return {"checks":checks,"issues":issues,"bias":bias,"scope":"in-memory observation recomputation; no raw export"}
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
                for side in ("home","away"):
                    h=history(primary,e,e[side+"Team"]["id"],now)
                    sides[side]["independent_check"]=independent_check(h,accepted,sides[side])
                if all(s["advanced_season"]["shots_for"]["n"]>=5 for s in sides.values()):
                    report["dossier"]={"id":e["id"],"kickoff":e["utcDate"],"competition":code,"sides":sides,"source_hash":report["leagues"][code]["sha256"],"engine_access":False,"limitations":["advanced statistics not externally verified","historical publication timestamps unknown","no injuries or lineups","goal minutes excluded","descriptive means not probabilities"]}
                    break
    except Exception as e:report["error"]=type(e).__name__
    report["trace"]=trace
    report["audit"]=audit_dossier(report["dossier"])
    if report["dossier"] and stamp(report["dossier"]["kickoff"])<=datetime.now(timezone.utc):report["dossier"]=None
    with open("football-d0-enriched.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps({**report,"leagues":{k:{a:b for a,b in v.items() if a!="missing"} for k,v in report["leagues"].items()}}))
    return int("error" in report or not report["audit"]["pass"] or not report["dossier"] or not all(v["accounting_ok"] for v in report["leagues"].values()))
if __name__=="__main__":raise SystemExit(main())
