"""Isolated synthetic conditional bounds; never a forecast or admission."""
from math import isfinite
from d0_contract import digest
from c4_trajectories import audit as trajectory_audit
from c4_e4 import generate
from c4_market_scope import evaluate, audit as scope_audit

def compare(d,event,dependencies,trajectories,contract,packet,expected_hash,threshold):
    def result(state):
        return dict(state=state,engine_access=False,publication="BLOCKED",qualification="BLOCKED",predictive_validity_verified=False)
    if d.get("origin")!="synthetic" or event.get("origin")!="synthetic" or d.get("sport")!="nba" or event.get("sport")!="nba":
        return result("REJECT")
    if packet.get("input_sha256")!=digest(d) or packet.get("event_sha256")!=digest(event) or packet.get("trajectory_sha256")!=digest(trajectories) or digest(packet)!=expected_hash:
        return result("REJECT")
    if contract.get("family")!="team_total" or contract.get("direction")!="over":
        return result("REJECT")
    try:
        trajectory_audit(dependencies,trajectories)
        scope=evaluate(event,{"configurations":[]},trajectories,contract,[threshold,threshold+1])
        scope_audit(event,{"configurations":[]},trajectories,scope)
    except (ValueError,KeyError,TypeError,OverflowError):
        return result("REJECT")
    if event.get("participants")!=d.get("participants") or any(row["issues"] for row in trajectories["trajectories"]):
        return result("ABSTENTION")
    e4=generate(d,[1],"fixture",{},1,1,{},{})
    if packet.get("e4_sha256")!=digest(e4):
        return result("REJECT")
    metric=e4["metrics"][contract["subject"]]["points_for"]
    refs=packet.get("evidence_ids",[])
    valid={o["id"] for o in d["observations"] if o["participant"]==contract["subject"] and "points_for" in o["stats"]}
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
