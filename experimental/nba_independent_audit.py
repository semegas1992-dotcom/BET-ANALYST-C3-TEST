"""Independent descriptive checks; never promotes quarantined data."""
from datetime import datetime,timezone
import hashlib,json
def stamp(s):
    d=datetime.fromisoformat(s.replace("Z","+00:00"))
    if d.tzinfo is None: raise ValueError("timezone required")
    return d.astimezone(timezone.utc)
def audit_history(h,cutoff):
    issues=[]; checks=0; coverage={}
    rows=h["games"]
    if any(stamp(a["datetime"])<stamp(b["datetime"]) for a,b in zip(rows,rows[1:])):issues.append("chronology")
    if not rows:issues.append("empty_history")
    for g in rows:
        p=g.get("periods",{})
        if p.get("status")=="CONSISTENT":
            x,y=p["pf"],p["pa"]
            if len(x)!=len(y) or len(x)<4 or any(type(v) is not int or v<0 for v in x+y) or sum(x)!=g["pf"] or sum(y)!=g["pa"]:issues.append("period_score:"+str(g["id"]))
    if len({g["id"] for g in rows})!=len(rows):issues.append("duplicate")
    if any(stamp(g["datetime"]).date()>=stamp(cutoff).date() for g in rows):issues.append("cutoff")
    if any(type(g[k]) is not int or g[k]<=0 for g in rows for k in ("pf","pa")):issues.append("score")
    if any(g["pf"]==g["pa"] for g in rows):issues.append("tie")
    for name,rr in (("season",rows),("L5",rows[:5]),("L10",rows[:10]),("L15",rows[:15]),("home",[g for g in rows if g["home"]]),("away",[g for g in rows if not g["home"]])):
        n=len(rr); valid=[g for g in rr if g.get("periods",{}).get("status")=="CONSISTENT"]
        expected={"n":n,"wins":sum(g["pf"]>g["pa"] for g in rr),"losses":sum(g["pf"]<g["pa"] for g in rr),"game_ids":[g["id"] for g in rr]}
        for k in ("pf","pa","total","margin"):
            expected[k]=(sum(g["pf"] if k=="pf" else g["pa"] if k=="pa" else g["pf"]+g["pa"] if k=="total" else g["pf"]-g["pa"] for g in rr)/n if n else None)
        actual=h["stats"][name]
        for k,v in expected.items():
            checks+=1
            if actual.get(k)!=v:issues.append(name+":"+k)
        p=actual["period_stats"]
        for k,v in {"n":len(valid),"eligible":n,"coverage":len(valid)/n if n else None}.items():
            checks+=1
            if p.get(k)!=v:issues.append(name+":period:"+k)
        for label,ix in (("Q1",[0]),("Q2",[1]),("Q3",[2]),("Q4",[3]),("H1",[0,1]),("H2",[2,3]),("REG",[0,1,2,3])):
            for k in ("pf","pa"):
                checks+=1
                v=sum(sum(g["periods"][k][i] for i in ix) for g in valid)/len(valid) if valid else None
                if p[label][k]!=v:issues.append(name+":"+label+":"+k)
        coverage[name]={"n":n,"period_n":len(valid),"period_coverage":len(valid)/n if n else None,"experimental_sample_gate":n>=5 and len(valid)>=5 and len(valid)*5>=n*4}
    return {"checks":checks,"issues":issues,"coverage":coverage}
def audit_batch(report):
    issues=[]; histories={}
    if report.get("engine_access") is not False or report.get("publication")!="BLOCKED_RIGHTS_NOT_CONFIRMED":issues.append("quarantine")
    for ref,h in report["histories"].items():
        if h["status"]!="COLLECTED":issues.append(ref+":incomplete");continue
        try: histories[ref]=audit_history(h,report["cutoff"])
        except (KeyError,TypeError,ValueError,IndexError) as e:issues.append(ref+":malformed:"+type(e).__name__)
    for ref,h in histories.items():issues.extend(ref+":"+i for i in h["issues"])
    dossiers=[]
    for d in report["dossiers"]:
        e=d["event"]; refs=d["history_refs"]
        if d.get("engine_access") is not False or stamp(e["tipoff"])<=stamp(report["cutoff"]):issues.append("dossier lock/time")
        expected=[f'{e["season"]}:{e[k]}' for k in ("home_id","away_id")]
        if refs!=expected or len(set(refs))!=2 or any(r not in histories or not report["histories"][r]["games"] for r in refs):issues.append("dossier history identity")
        reasons=["external_verification_missing","rights_unconfirmed","availability_timestamps_unverified"]
        if any(r not in histories or not histories[r]["coverage"]["L5"]["experimental_sample_gate"] for r in refs):reasons.append("sample_coverage")
        dossier={"schema":"D0_NBA_QUARANTINE_V1","sport":"nba","event":e,"cutoff":report["cutoff"],"history_refs":refs,"engine_access":False,"qualification":"BLOCKED","reasons":reasons}
        dossier["history_sha256"]={r:hashlib.sha256(json.dumps(report["histories"][r],sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest() for r in refs if r in report["histories"]}
        dossier["sha256"]=hashlib.sha256(json.dumps(dossier,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
        dossiers.append(dossier)
    return {"schema":"NBA_INDEPENDENT_AUDIT_V1","status":"FAIL" if issues else "PASS","issues":issues,"checks":sum(h["checks"] for h in histories.values()),"histories":histories,"dossiers":dossiers,"engine_access":False,"input_sha256":hashlib.sha256(json.dumps(report,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()}
if __name__=="__main__":
    from pathlib import Path
    r=audit_batch(json.loads(Path("nba-batch-quarantine.json").read_text()))
    Path("nba-independent-audit.json").write_text(json.dumps(r,indent=2,sort_keys=True))
    print("Independent checks:",r["checks"],"status:",r["status"])
    if r["status"]!="PASS":raise SystemExit(1)
