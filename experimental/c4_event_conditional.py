"""Isolated synthetic conditional bounds; never a forecast or admission."""
from math import isfinite
from d0_contract import digest, validate
from c4_trajectories import audit as trajectory_audit
from c4_e4 import generate
from c4_market_scope import evaluate, audit as scope_audit

def _compare(d,event,dependencies,trajectories,contract,packet,expected_hash,threshold,strict=False):
    def result(state):
        return dict(state=state,engine_access=False,publication="BLOCKED",qualification="BLOCKED",predictive_validity_verified=False)
    if not dependencies.get("mechanisms") or trajectories.get("engine_access") is not False or trajectories.get("publication")!="BLOCKED" or trajectories.get("qualification")!="BLOCKED":
        return result("REJECT")
    if d.get("origin")!="synthetic" or event.get("origin")!="synthetic" or d.get("sport") not in ("nba","football","tennis") or event.get("sport")!=d.get("sport") or (not strict and d.get("sport")!="nba"):
        return result("REJECT")
    if packet.get("input_sha256")!=digest(d) or packet.get("event_sha256")!=digest(event) or packet.get("trajectory_sha256")!=digest(trajectories) or digest(packet)!=expected_hash:
        return result("REJECT")
    sport=d["sport"]
    participants=["home","away"] if sport=="football" else d.get("participants")
    if strict:
        validate(d)
        if packet.get("contract_sha256")!=digest(contract) or packet.get("threshold")!=threshold or event.get("cutoff")!=d["cutoff"] or event.get("kickoff")!=d["kickoff"] or event.get("input_sha256")!=digest(d):
            return result("REJECT")
    if contract.get("family")!="team_total" or contract.get("direction")!="over":
        return result("REJECT")
    try:
        trajectory_audit(dependencies,trajectories)
        scope=evaluate(event,{"configurations":[]},trajectories,contract,[threshold,threshold+1])
        scope_audit(event,{"configurations":[]},trajectories,scope)
    except (ValueError,KeyError,TypeError,OverflowError):
        return result("REJECT")
    if event.get("participants")!=participants or any(row["issues"] for row in trajectories["trajectories"]):
        return result("ABSTENTION")
    e4=generate(d,[1],"fixture",{},1,1,{},{})
    if packet.get("e4_sha256")!=digest(e4):
        return result("REJECT")
    field={"nba":"points_for","football":"shots_for","tennis":"service_points_played"}[sport]
    metric=e4["metrics"][contract["subject"]][field]
    refs=packet.get("evidence_ids",[])
    valid={o["id"] for o in d["observations"] if o["side" if sport=="football" else "participant"]==contract["subject"] and field in o["stats"]}
    if not metric["complete"] or not refs or not set(refs)<=valid or packet.get("basis")!="explicit_fictional_assumptions":
        return result("ABSTENTION")
    scenarios=packet.get("scenarios",[])
    if len(scenarios)!=len(trajectories["trajectories"]):
        return result("ABSTENTION")
    states=[]
    for row,s in zip(trajectories["trajectories"],scenarios):
        if s.get("assignment")!=row["assignment"] or not isinstance(s.get("assumption"),str) or not s["assumption"].strip():
            return result("ABSTENTION")
        bounds=s.get("bounds")
        if not isinstance(bounds,list) or len(bounds)!=2 or any(type(v) is not int or v<0 for v in bounds) or bounds[0]>bounds[1]:
            return result("REJECT")
        lo,hi=bounds
        states.append("ABOVE" if lo>threshold else "BELOW" if hi<threshold else "UNRESOLVED")
    return result(states[0] if len(set(states))==1 and states else "UNRESOLVED")


def compare(d,event,dependencies,trajectories,contract,packet,expected_hash,threshold):
    """Fail closed on malformed experimental inputs; never grant access."""
    try:
        return _compare(d,event,dependencies,trajectories,contract,packet,expected_hash,threshold)
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError,IndexError):
        return dict(state="REJECT",engine_access=False,publication="BLOCKED",qualification="BLOCKED",predictive_validity_verified=False)


def compare_bound(d,event,dependencies,trajectories,contract,packet,expected_hash,threshold):
    """Strict experimental entry point. Hash must be supplied from a trusted frozen packet."""
    try:
        return _compare(d,event,dependencies,trajectories,contract,packet,expected_hash,threshold,strict=True)
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError,IndexError):
        return dict(state="REJECT",engine_access=False,publication="BLOCKED",qualification="BLOCKED",predictive_validity_verified=False)
