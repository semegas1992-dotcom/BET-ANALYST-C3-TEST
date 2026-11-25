"""Joint conditional trajectories, not predicted outcomes."""
from itertools import product
from d0_contract import digest
def build(dependencies):
    ms=dependencies["mechanisms"];keys=sorted(ms)
    rows=[]
    for states in product(("holds","fails"),repeat=len(keys)):
        assignment=dict(zip(keys,states))
        issues=sorted({i for m in ms.values() for i in m["issues"]})
        sequences=[x for x in dependencies["sequences"] if assignment.get(x["scenario_id"].rsplit(":",1)[0])==x["branch"]]
        rows.append({"assignment":assignment,"sequence_refs":[[x["scenario_id"],x["phase"]] for x in sequences],"issues":issues,"status":"BLOCKED" if issues else "UNVERIFIED_HYPOTHESIS"})
    return {"dependency_sha256":digest(dependencies),"trajectories":rows,"scope":"logical combinations only; feasibility and dominance not established","engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
def audit(dependencies,report):
    keys=sorted(dependencies["mechanisms"]);seen=set()
    if report["dependency_sha256"]!=digest(dependencies):raise ValueError("dependency hash")
    for row in report["trajectories"]:
        a=row["assignment"]
        if set(a)!=set(keys) or any(v not in ("holds","fails") for v in a.values()):raise ValueError("assignment")
        k=tuple(a[x] for x in keys)
        if k in seen:raise ValueError("duplicate trajectory")
        seen.add(k)
        expected=[[x["scenario_id"],x["phase"]] for x in dependencies["sequences"] if a[x["scenario_id"].rsplit(":",1)[0]]==x["branch"]]
        issues=sorted({i for m in dependencies["mechanisms"].values() for i in m["issues"]})
        if row["sequence_refs"]!=expected or row["issues"]!=issues or row["status"]!=("BLOCKED" if issues else "UNVERIFIED_HYPOTHESIS"):raise ValueError("trajectory audit")
    if len(seen)!=2**len(keys):raise ValueError("coverage")
    return {"passed":True,"checks":len(seen)}
