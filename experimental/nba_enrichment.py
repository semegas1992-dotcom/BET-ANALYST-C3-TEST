import hashlib,json,time,urllib.parse
from statistics import mean,median,stdev
from nba_history import BASE,request_json,stamp

def grouped(teams,season,cutoff,key,trace,errors,partial):
    cursor=None
    seen=set()
    for _ in range(30):
        q={"team_ids[]":sorted(teams),"seasons[]":season,"end_date":cutoff.date().isoformat(),"per_page":100}
        if cursor is not None:q["cursor"]=cursor
        p=request_json(BASE+"?"+urllib.parse.urlencode(q,doseq=True),key,errors)
        if not isinstance(p.get("data"),list) or not isinstance(p.get("meta"),dict):raise ValueError("invalid group page")
        cursor=p["meta"].get("next_cursor")
        trace.append({"payload":p,"query":q,"count":len(p["data"]),"next_cursor":cursor,"sha256":hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",",":")).encode()).hexdigest()})
        partial.extend(p["data"])
        time.sleep(16)
        if cursor is None:return partial
        if cursor in seen:raise ValueError("group cursor loop")
        seen.add(cursor)
    raise ValueError("group pagination incomplete")

def distribute(raw,teams):
    result={t:[] for t in teams}
    seen=set()
    for g in raw:
        i=g["id"]
        if i in seen:raise ValueError("duplicate grouped game")
        seen.add(i)
        members={g["home_team"]["id"],g["visitor_team"]["id"]}&set(teams)
        if not members:raise ValueError("unrelated grouped game")
        for t in members:result[t].append(g)
    return result

def dispersion(rows):
    result={"n":len(rows),"game_ids":[g["id"] for g in rows]}
    for name,values in (("pf",[g["pf"] for g in rows]),("pa",[g["pa"] for g in rows]),("margin",[g["pf"]-g["pa"] for g in rows]),("total",[g["pf"]+g["pa"] for g in rows])):
        result[name]={"median":median(values) if values else None,"min":min(values) if values else None,"max":max(values) if values else None,"sample_sd":stdev(values) if len(values)>1 else None}
    return result

def context(rows,tip,opponent):
    ordered=sorted(rows,key=lambda g:g["datetime"],reverse=True)
    gap=(stamp(tip)-stamp(ordered[0]["datetime"])).total_seconds()/3600 if ordered else None
    return {"hours_since_last_observed_tipoff":gap,"last_observed_game_id":ordered[0]["id"] if ordered else None,"rest_status":"NOT_VERIFIED","games_last_7_days":sum(0<(stamp(tip)-stamp(g["datetime"])).total_seconds()<=7*86400 for g in ordered),"h2h":dispersion([g for g in ordered if g["opponent_id"]==opponent]),"dispersion":{"season":dispersion(ordered),"L5":dispersion(ordered[:5]),"L10":dispersion(ordered[:10])}}
