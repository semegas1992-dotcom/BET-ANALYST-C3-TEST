"""Conditional interaction review, without inferred causal coefficients."""
from d0_contract import digest
PAIRS={"football":("volume","target"),"nba":("scoring","rebounds"),"tennis":("serve","return")}
def build(sport,dependencies,trajectories):
    a,b=PAIRS[sport];rows=[]
    for t in trajectories["trajectories"]:
        s=t["assignment"];interactions=[]
        for i in (0,1):
            j=1-i
            keys=[f"{i}:{a}",f"{i}:{b}",f"{j}:{b}"]
            states=[s[k] for k in keys]
            # Joint states are not contradictions: mechanisms describe different quantities.
            interactions.append({"mechanisms":keys,"states":states,"pattern":"JOINT_MAINTENANCE" if all(v=="holds" for v in states) else "MIXED_OR_REVISION","record_ids":sorted({v for k in keys for v in dependencies["mechanisms"][k]["record_ids"]}),"turning_points":sorted({x["turning_point"] for x in dependencies["sequences"] if x["scenario_id"].rsplit(":",1)[0] in keys and s[x["scenario_id"].rsplit(":",1)[0]]==x["branch"]})})
        rows.append({"assignment":s,"interactions":interactions,"issues":sorted(set(t["issues"]+["CAUSAL_EFFECT_UNCALIBRATED"])),"plausibility":"UNDETERMINED","estimate":None})
    return {"trajectory_sha256":digest(trajectories),"rows":rows,"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
def audit(dependencies,trajectories,report):
    if report["trajectory_sha256"]!=digest(trajectories) or len(report["rows"])!=len(trajectories["trajectories"]):raise ValueError("coverage")
    for t,r in zip(trajectories["trajectories"],report["rows"]):
        if t["assignment"]!=r["assignment"] or not set(t["issues"]).issubset(r["issues"]) or r["estimate"] is not None or r["plausibility"]!="UNDETERMINED":raise ValueError("unsupported conclusion")
        for x in r["interactions"]:
            if x["states"]!=[t["assignment"][k] for k in x["mechanisms"]]:raise ValueError("interaction states")
            if set(x["record_ids"])!={v for k in x["mechanisms"] for v in dependencies["mechanisms"][k]["record_ids"]}:raise ValueError("evidence")
    return {"passed":True,"checks":len(report["rows"]),"scope":"structural interaction audit"}
