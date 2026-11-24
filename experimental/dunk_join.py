from collections import Counter
from dunk_enrichment import namekey
from nba_history import stamp

def code(s):
    return {"gs":"gsw","no":"nop","ny":"nyk","sa":"sas","utah":"uta","wsh":"was","nor":"nop","pho":"phx","bkn":"bkn"}.get(namekey(s),namekey(s))

def full(s):
    return namekey(s).replace("los angeles clippers","la clippers")

def mapping(bdl,dunk):
    result={}; used=set()
    for b in bdl:
        matches=[d for d in dunk if full(d.get("display_name") or d["name"])==full(b["full_name"]) and code(d["abbrev"])==code(b["abbreviation"])]
        if len(matches)==1:
            d=matches[0]; i=str(d["team_id"])
            if i in used:raise ValueError("duplicate mapped ID")
            used.add(i);result[str(b["id"])]=d
    return result

def injury_counts(rows,mapped):
    aliases={}
    for bid,t in mapped.items():
        for a in (t["display_name"],t["abbrev"],t["team_id"]):
            k=namekey(str(a));aliases.setdefault(k,set()).add(bid)
    counts={k:Counter() for k in mapped};unknown=0
    for row in rows:
        t=row.get("team")
        if isinstance(t,dict):t=t.get("team_id") or t.get("display_name") or t.get("abbrev")
        matches=aliases.get(namekey(str(t)),set())
        if len(matches)!=1:unknown+=1;continue
        status=row.get("status")
        if not isinstance(status,str) or not status.strip():status="UNKNOWN"
        counts[next(iter(matches))][status]+=1
    return counts,unknown

def assemble(report,mapped,counts,unknown,observed,snapshot):
    if report.get("engine_access") is not False:raise ValueError("engine lock")
    dossiers=[]
    for d in report["dossiers"]:
        e=d["event"]
        if stamp(observed)>=stamp(e["tipoff"]):continue
        sides={}
        for side in ("home","away"):
            k=str(e[side+"_id"])
            sides[side]={"mapped":k in mapped,"injury_counts":dict(counts[k]) if k in mapped else None,"availability":"UNKNOWN"}
        dossiers.append({"event_id":e["id"],"history_refs":d["history_refs"],"collective_status":d["status"],"sides":sides,"snapshot_date":snapshot,"observed_at":observed,"unmapped_injury_rows":unknown,"individual_status":"NOT_LINKED","engine_access":False})
    return dossiers

def audit_join(report,dossiers,mapped,counts,unknown,total):
    issues=[]
    if len(mapped)!=30:issues.append("league mapping incomplete")
    if unknown:issues.append("unmapped injury rows")
    if sum(sum(c.values()) for c in counts.values())+unknown!=total:issues.append("injury accounting")
    if len(dossiers)!=len(report["dossiers"]):issues.append("dossier accounting")
    for d in dossiers:
        if d["engine_access"] is not False or any(not s["mapped"] for s in d["sides"].values()):issues.append("dossier mapping or lock")
        if d["collective_status"]!="QUARANTINE_UNVERIFIED":issues.append("collective incomplete")
    return {"status":"PASS" if not issues else "FAIL","issues":issues,"external_verification":"NOT_VERIFIED"}
