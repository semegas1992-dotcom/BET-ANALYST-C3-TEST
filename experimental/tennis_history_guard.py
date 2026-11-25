"""Experimental synthetic tennis history guard; no network."""
from datetime import datetime
def stamp(s):
    d=datetime.fromisoformat(s.replace("Z","+00:00"))
    if d.tzinfo is None: raise ValueError("timezone required")
    return d
def validate(row,cutoff):
    if row["tour"] not in ("ATP","WTA"): raise ValueError("tour")
    if row["surface"] not in ("hard","clay","grass","carpet"): raise ValueError("surface")
    if row["best_of"] not in (3,5): raise ValueError("format")
    if row["player_id"]==row["opponent_id"]: raise ValueError("identity")
    if not stamp(row["ended_at"])<=stamp(row["available_at"])<=stamp(cutoff): raise ValueError("cutoff")
    if row["status"]!="completed": raise ValueError("noncompleted")
    return True
