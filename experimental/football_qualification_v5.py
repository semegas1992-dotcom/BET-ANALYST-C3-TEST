from collections import Counter, deque

def rejection_reasons(sides):
    reasons=[]
    for side in ("home","away"):
        data=sides[side]
        for period in ("advanced_season","advanced_last5"):
            for field in ("shots_for","shots_against","target_for","target_against"):
                v=data[period].get(field,{})
                n,e=v.get("n",0),v.get("eligible",0)
                if type(n) is not int or type(e) is not int or not 0<=n<=e:
                    reasons.append(f"{side}:{period}:{field}:invalid_count")
                elif n<5 or n*5<e*4:
                    reasons.append(f"{side}:{period}:{field}:insufficient_sample")
        check=data.get("independent_check",{})
        if check.get("checks")!=32 or check.get("issues")!=[]:
            reasons.append(f"{side}:observation_audit")
    return reasons

def select_diverse(candidates,limit=10):
    groups={}
    for d in sorted(candidates,key=lambda d:(d["kickoff"],d["id"])):
        groups.setdefault(d["competition"],deque()).append(d)
    selected=[]
    while groups and len(selected)<limit:
        for code in sorted(groups,key=lambda c:(groups[c][0]["kickoff"],c)):
            if len(selected)>=limit:break
            selected.append(groups[code].popleft())
            if not groups[code]:del groups[code]
    return sorted(selected,key=lambda d:(d["kickoff"],d["id"]))

def diversity_audit(candidates,selected,limit=10):
    available=Counter(d["competition"] for d in candidates)
    chosen=Counter(d["competition"] for d in selected)
    expected=select_diverse(candidates,limit)
    return {"available":dict(available),"selected":dict(chosen),
            "pass":selected==expected and len({d["id"] for d in selected})==len(selected)
            and len(chosen)==min(len(available),limit),
            "scope":"eligible candidates only; not evidence of representativeness"}
