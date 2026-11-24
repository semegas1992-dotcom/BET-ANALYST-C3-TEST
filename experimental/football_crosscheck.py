import json,hashlib,unicodedata,re
from urllib.request import urlopen
from datetime import datetime,timezone
FILES={"PL":"en.1","BL1":"de.1","FL1":"fr.1","PD":"es.1","SA":"it.1"}
def name(v):
    if isinstance(v,dict):v=v.get("name")
    if not isinstance(v,str):return None
    return " ".join(unicodedata.normalize("NFKC",v).casefold().split())
def compare(primary,secondary,details=None):
    # Exact oriented names and civil date only; no fuzzy identity.
    idx={}
    for m in secondary:
        if not isinstance(m,dict):raise ValueError("invalid secondary row")
        k=(m.get("date"),name(m.get("team1")),name(m.get("team2")))
        idx.setdefault(k,[]).append(m)
    counts=dict(matched=0,conflicting=0,unmatched=0,ambiguous=0)
    for m in primary:
        k=(m["utcDate"][:10],name(m["homeTeam"]["name"]),name(m["awayTeam"]["name"]))
        rows=idx.get(k,[])
        if len(rows)>1:
            counts["ambiguous"]+=1
            if details is not None:details.append({"id":m.get("id"),"key":k,"reason":"AMBIGUOUS"})
            continue
        score=(rows[0].get("score") or {}) if rows else {}
        ft=score.get("ft") if isinstance(score,dict) else None
        if not isinstance(ft,list) or len(ft)!=2 or any(type(x) is not int or x<0 for x in ft):
            counts["unmatched"]+=1
            if details is not None:
                same_pair=[x[0] for x in idx if x[1:]==k[1:]]
                same_date=[x[1:] for x in idx if x[0]==k[0]]
                details.append({"id":m.get("id"),"key":k,"reason":"INVALID_OR_MISSING_SCORE" if rows else ("PAIR_OTHER_DATE" if same_pair else "IDENTITY_OR_COVERAGE"),"pair_dates":same_pair,"date_candidates":same_date})
            continue
        s=m["score"]["fullTime"]
        status="matched" if ft==[s["home"],s["away"]] else "conflicting"
        counts[status]+=1
        if details is not None and status=="conflicting":details.append({"id":m.get("id"),"key":k,"reason":"SCORE_CONFLICT","primary":[s["home"],s["away"]],"secondary":ft})
    return counts
def load(code,season):
    url="https://raw.githubusercontent.com/openfootball/football.json/master/"+str(season)+"-"+str(season+1)[-2:]+"/"+FILES[code]+".json"
    with urlopen(url,timeout=30) as f:raw=f.read(3000000)
    data=json.loads(raw)
    return data["matches"],{"url":url,"sha256":hashlib.sha256(raw).hexdigest(),"observed":datetime.now(timezone.utc).isoformat()}
def main():
    import os
    from football_collect import fetch,matches
    report={"engine_access":False,"external_verification":"NOT_VERIFIED","comparisons":{}}
    trace=[]
    for code in FILES:
        try:
            secondary,meta=load(code,2025)
            primary=matches(fetch("competitions/"+code+"/matches",{"season":2025,"status":"FINISHED"},os.environ["FOOTBALL_DATA_TOKEN"],trace))
            details=[]
            counts=compare(primary,secondary,details)
            report["comparisons"][code]={"counts":counts,"source":meta,"exceptions":details,"accounting_ok":sum(counts.values())==len(primary) and len(details)==len(primary)-counts["matched"]}
        except Exception as e:report["comparisons"][code]={"error":type(e).__name__,"http_code":getattr(e,"code",None),"detail":str(e)[:200]}
    report["trace"]=trace
    if any(v.get("counts",{}).get("matched",0) for v in report["comparisons"].values()):report["external_verification"]="PARTIAL"
    with open("football-crosscheck.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps({**report,"comparisons":{k:{a:b for a,b in v.items() if a!="exceptions"} for k,v in report["comparisons"].items()}}))
    return int(any("error" in v or v["counts"]["conflicting"] or not v["counts"]["matched"] for v in report["comparisons"].values()))
if __name__=="__main__":raise SystemExit(main())
