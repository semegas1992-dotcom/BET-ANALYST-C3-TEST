"""Compare descriptive thresholds only; no event forecasts or market selection."""
from c4_e4 import generate
from c4_e4_trace import audit
from d0_contract import digest
from math import isfinite
UNITS={"football":{"shots_for":"shots","shots_against":"shots","target_for":"shots_on_target","target_against":"shots_on_target","target_rate":"fraction"},"nba":{"points_for":"points","points_against":"points","rebounds":"rebounds","assists":"assists"},"tennis":{"service_rate":"fraction","return_rate":"fraction","service_points_won":"points","service_points_played":"points","return_points_won":"points","return_points_played":"points"}}
def compare(d,windows,reason,context,min_n,min_coverage,atypical_ids,contract,thresholds):
    args=(windows,reason,context,min_n,min_coverage,atypical_ids,{})
    report=generate(d,*args)
    review=audit(d,report,*args)
    if not review["passed"]:raise ValueError("envelope audit")
    if set(contract)!={"input_sha256","sport","participant","metric","period","unit"}:raise ValueError("contract fields")
    p,f=contract["participant"],contract["metric"]
    if contract["input_sha256"]!=digest(d) or contract["sport"]!=d["sport"] or contract["period"]!="historical_observation" or f not in UNITS[d["sport"]] or contract["unit"]!=UNITS[d["sport"]][f] or p not in report["metrics"] or f not in report["metrics"][p]:raise ValueError("incompatible contract")
    if not isinstance(thresholds,list) or not thresholds or any(type(t) not in (int,float) or not isfinite(t) or t<0 or (contract["unit"]=="fraction" and t>1) for t in thresholds) or len(set(thresholds))!=len(thresholds):raise ValueError("thresholds")
    m=report["metrics"][p][f];rows=[]
    for t in sorted(thresholds):
        states=[None if not v["qualified"] or v["value"] is None else v["value"]>=t for v in m["variants"]]
        state="BLOCKED" if None in states else "ALL_AT_OR_ABOVE" if all(states) else "ALL_BELOW" if not any(states) else "SENSITIVE"
        rows.append({"threshold":t,"state":state,"variant_comparisons":states})
    return {"schema":"C4_E5_DESCRIPTIVE_V1","contract":dict(contract),"envelope_report_sha256":digest(report),"variants":m["variants"],"rows":rows,"audit_checks":review["checks"],"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED","scope":"historical descriptive only; observation period not verified as match or regulation"}
