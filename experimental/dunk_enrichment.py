import unicodedata,math
from datetime import date,datetime,timezone
from statistics import mean

def namekey(s):
    if not isinstance(s,str) or not s.strip():raise ValueError("missing name")
    return " ".join(unicodedata.normalize("NFKC",s).casefold().split())

def team_mapping(bdl,dunk):
    index={}
    for t in dunk:
        index.setdefault(namekey(t["name"]),[]).append(t)
    result={}
    for t in bdl:
        matches=index.get(namekey(t["full_name"]),[])
        if len(matches)==1:
            d=matches[0]
            result[str(t["id"])]={"dunk_id":str(d["team_id"]),"status":"NAME_MATCH_UNVERIFIED"}
    return result

def player_summary(data,player_id,cutoff,season):
    p=data["player"]
    if str(p["player_id"])!=str(player_id):raise ValueError("identity mismatch")
    if cutoff.tzinfo is None:raise ValueError("timezone required")
    day=cutoff.astimezone(timezone.utc).date()
    rows=[];seen=set();excluded=0
    for g in data["recent_games"]:
        if date.fromisoformat(g["date"])>=day or g["season"]!=season:
            excluded+=1;continue
        i=str(g["game_id"])
        if i in seen:raise ValueError("duplicate game")
        seen.add(i)
        for k in ("pts","reb","ast","minutes"):
            v=g[k]
            if type(v) not in (int,float) or not math.isfinite(v) or v<0:raise ValueError("invalid statistic")
        rows.append(g)
    rows.sort(key=lambda g:g["date"],reverse=True)
    return {"n":len(rows),"excluded":excluded,"means":{k:mean(g[k] for g in rows) if rows else None for k in ("pts","reb","ast","minutes")},"season_aggregates_used":False,"identity":"PROVIDER_ID_ONLY","temporal_status":"DATES_ONLY_UNVERIFIED","engine_access":False}

def injury_shape(data):
    rows=data["injuries"]
    if not isinstance(rows,list) or len(rows)!=data["count"] or any(not isinstance(x,dict) for x in rows):raise ValueError("invalid report")
    return {"count":len(rows),"fields":sorted({k for x in rows for k in x}),"unlisted_availability":"UNKNOWN","publication_time":"UNKNOWN"}

def attach(dossier,home,away,player_metadata):
    if dossier.get("engine_access") is not False:raise ValueError("engine lock")
    return {**dossier,"dunkapi":{"home":home,"away":away,"player_metadata":player_metadata,"status":"QUARANTINE_UNVERIFIED","engine_access":False}}
