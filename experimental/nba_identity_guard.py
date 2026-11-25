"""Strict cross-provider identity matching; no fuzzy or name-only player join."""
def match_teams(primary,secondary):
    aliases={"NY":"NYK","GS":"GSW","NO":"NOP","SA":"SAS","UTAH":"UTA","WSH":"WAS","PHO":"PHX"}
    def key(row):
        a=row["abbreviation"].upper()
        return aliases.get(a,a)
    out={};issues=[]
    for p in primary:
        candidates=[s for s in secondary if key(p)==key(s)]
        if len(candidates)!=1:issues.append({"id":p["id"],"reason":"missing_or_ambiguous"});continue
        out[str(p["id"])]=str(candidates[0]["id"])
    if len(set(out.values()))!=len(out):issues.append({"reason":"non_unique_mapping"})
    return {"mapping":out,"issues":issues,"external_verified":False}
def match_player(primary,secondary):
    fields=("first_name","last_name","birth_date")
    if any(not primary.get(f) for f in fields):return None
    matches=[s for s in secondary if all(s.get(f)==primary[f] for f in fields)]
    return matches[0]["id"] if len(matches)==1 else None
