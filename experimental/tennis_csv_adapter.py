"""Offline Sackmann-format adapter. No network or permission grant."""
import csv,io,hashlib,unicodedata
from datetime import datetime
def identity(tour, value):
    if tour not in ("ATP","WTA") or not str(value).isascii() or not str(value).isdigit() or int(value)<=0:
        raise ValueError("identity")
    return f"{tour}:{int(value)}"
def namekey(s):
    return " ".join(unicodedata.normalize("NFC",s).casefold().split())
def match_identity(player, candidates):
    fields=("first_name","last_name","birth_date")
    if any(not player.get(k) for k in fields): return None
    matches=[c for c in candidates if c.get("tour")==player.get("tour") and all(c.get(k) and (namekey(c[k])==namekey(player[k]) if k!="birth_date" else c[k]==player[k]) for k in fields)]
    return matches[0]["id"] if len(matches)==1 else None
def parse_csv(raw,tour):
    if tour not in ("ATP","WTA"): raise ValueError("tour")
    rows=[]; rejected=[]; seen=set()
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    required={"tourney_id","tourney_date","match_num","winner_id","loser_id","surface","best_of","score"}
    if not required.issubset(reader.fieldnames or []): raise ValueError("schema")
    for i,r in enumerate(reader,2):
        try:
            w,l=identity(tour,r["winner_id"]),identity(tour,r["loser_id"])
            if w==l: raise ValueError("same_player")
            day=datetime.strptime(r["tourney_date"],"%Y%m%d").date().isoformat()
            surface=r["surface"].lower()
            if surface not in ("hard","clay","grass","carpet"): raise ValueError("surface")
            best=int(r["best_of"])
            if best not in (3,5): raise ValueError("format")
            if not r["tourney_id"].strip() or not r["match_num"].isdigit(): raise ValueError("event_identity")
            key=f'{tour}:{r["tourney_id"]}:{int(r["match_num"])}'
            if key in seen: raise ValueError("duplicate")
            seen.add(key)
            score=r["score"].strip().upper()
            if not score or any(x in score for x in ("RET","W/O","DEF","ABD","WALK")): raise ValueError("noncompleted_or_unknown")
            stats={}
            for side in ("w","l"):
                for f in ("svpt","1stIn","1stWon","2ndWon","ace","df","bpSaved","bpFaced"):
                    v=r.get(f"{side}_{f}")
                    stats[f"{side}_{f}"]=None if v in (None,"") else int(v)
            if any(v is not None and v<0 for v in stats.values()): raise ValueError("negative_stat")
            rows.append({"id":key,"tour":tour,"winner_id":w,"loser_id":l,"tournament_start_date":day,"surface":surface,"best_of":best,"score":score,"stats":stats,"ended_at":None,"available_at":None,"qualification":"BLOCKED_TIME_AND_RIGHTS","engine_access":False})
        except (ValueError,TypeError,KeyError,AttributeError) as e: rejected.append({"row":i,"reason":str(e)})
    return {"rows":rows,"rejected":rejected,"input_sha256":hashlib.sha256(raw).hexdigest(),"engine_access":False}
