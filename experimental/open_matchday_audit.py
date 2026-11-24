import csv,io,json,hashlib
from collections import Counter
from datetime import datetime,timezone,date
from urllib.request import urlopen
FOLDERS={"PL":"ENG_1_premier-league","PD":"ESP_1_la-liga","BL1":"GER_1_bundesliga","SA":"ITA_1_serie-a","FL1":"FRA_1_ligue-1"}
def integer(v):
    if v is None or not v.strip():return None
    if not v.isascii() or not v.isdecimal():raise ValueError("invalid integer")
    return int(v)
def audit(raw,cutoff):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    rows=list(reader);issues=Counter();valid=Counter();seen=set()
    for r in rows:
        try:
            day=date.fromisoformat(r["date"])
            if day>=cutoff:issues["cutoff_excluded"]+=1;continue
            k=(day,r["home"],r["away"])
            if k in seen:issues["duplicate"]+=1;continue
            seen.add(k)
            if not k[1] or not k[2] or k[1]==k[2]:raise ValueError("team")
            x,y=integer(r["ft_home"]),integer(r["ft_away"])
            if x is None or y is None or r["ft_result"]!=("H" if x>y else "A" if x<y else "D"):raise ValueError("score")
            valid["score"]+=1
            for side,ft in (("home",x),("away",y)):
                ht=integer(r["ht_"+side])
                if ht is not None:
                    if ht>ft:issues["halftime_conflict"]+=1
                    else:valid["halftime_side"]+=1
                for stat in ("shots","target","fouls","corners","yellow","red"):
                    v=integer(r[side+"_"+stat])
                    if v is not None:valid[stat+"_side"]+=1
                sh,ta=integer(r[side+"_shots"]),integer(r[side+"_target"])
                if sh is not None and ta is not None and ta>sh:issues["target_gt_shots"]+=1
                a,b,c=[integer(r[side+"_corners"+s]) for s in ("","_1h","_2h")]
                if None not in (a,b,c):
                    if a!=b+c:issues["corner_split_conflict"]+=1
                    else:valid["corner_split_side"]+=1
            mins=r.get("goal_minutes","").strip()
            if not mins and x+y==0:valid["goalless_empty"]+=1
            elif not mins:issues["goal_minutes_missing"]+=1
            elif len(mins.split(","))!=x+y:issues["goal_minutes_count"]+=1
            else:valid["goal_minutes_count"]+=1
        except (ValueError,KeyError,TypeError):issues["invalid_row"]+=1
    return {"rows":len(rows),"valid":dict(valid),"issues":dict(issues)}
def main():
    now=datetime.now(timezone.utc)
    report={"engine_access":False,"publication":"BLOCKED_UPSTREAM_RIGHTS_NOT_CONFIRMED","cutoff":now.isoformat(),"leagues":{}}
    for code,folder in FOLDERS.items():
        url=f"https://raw.githubusercontent.com/oladeeayo/open-matchday/master/data/{folder}/results_2627.csv"
        try:
            with urlopen(url,timeout=25) as f:raw=f.read(5000001)
            if len(raw)>5000000:raise ValueError("size")
            report["leagues"][code]={**audit(raw,now.date()),"url":url,"sha256":hashlib.sha256(raw).hexdigest()}
        except Exception as e:report["leagues"][code]={"error":type(e).__name__}
    with open("open-matchday-audit.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps(report))
    return int(any("error" in v or not v.get("valid",{}).get("score") for v in report["leagues"].values()))
if __name__=="__main__":raise SystemExit(main())
