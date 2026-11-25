"""Conservative statistical qualification of quarantined tennis rows."""
import re
def score_valid(score,best):
    if best not in (3,5): return False
    need=best//2+1; wins=[0,0]
    for token in score.split():
        if max(wins)>=need:return False
        m=re.fullmatch(r"(\d+)-(\d+)(?:\((\d+)\))?",token)
        if not m:return False
        a,b=map(int,m.group(1,2)); hi,lo=max(a,b),min(a,b)
        if not ((hi==6 and lo<=4) or (hi==7 and lo in (5,6))):return False
        if m.group(3) is not None and (hi,lo)!=(7,6):return False
        wins[int(b>a)]+=1
    return wins[0]==need and wins[1]<need
def service(stats,side):
    fields=("svpt","1stIn","1stWon","2ndWon","ace","df","bpSaved","bpFaced")
    vals=[stats.get(side+"_"+f) for f in fields]
    if any(x is None for x in vals):return {"status":"MISSING","won":None,"total":None}
    if any(type(x) is not int or x<0 for x in vals):return {"status":"INVALID","won":None,"total":None}
    n,i,w1,w2,a,d,s,f=vals
    if not (n>0 and w1<=i<=n and w2<=n-i and a<=w1+w2 and d<=n-i-w2 and s<=f<=n and f-s<=n-w1-w2):
        return {"status":"INVALID","won":None,"total":None}
    return {"status":"OK","won":w1+w2,"total":n}
def qualify(row):
    valid=score_valid(row["score"],row["best_of"])
    sides={s:service(row["stats"],s) for s in ("w","l")}
    return {"score_valid":valid,"service":sides,"return":{s:{"won":sides[o]["total"]-sides[o]["won"],"total":sides[o]["total"]} if sides[o]["status"]=="OK" else None for s,o in (("w","l"),("l","w"))},"engine_access":False}
def surface_sample(rows,player,surface):
    eligible=[r for r in rows if r["surface"]==surface and player in (r["winner_id"],r["loser_id"])]
    seen=set(); usable=[]; rejected=[]
    for r in eligible:
        if r["id"] in seen: rejected.append("duplicate");continue
        seen.add(r["id"])
        q=qualify(r)
        if not q["score_valid"] or any(s["status"]!="OK" for s in q["service"].values()):rejected.append("score_or_stats");continue
        usable.append(r["id"])
    n=len(eligible); k=len(usable)
    return {"eligible":n,"usable":k,"coverage":k/n if n else None,"sample_gate":k>=5 and k*5>=n*4 and "duplicate" not in rejected,"rejected":rejected,"engine_access":False}
