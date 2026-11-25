"""Descriptive opposition envelope, never an event prediction."""
from d0_contract import digest
from copy import deepcopy
def build(documented,e2,e3,e4):
    if documented["scope"]!="EXACT_SYNTHETIC_DOCUMENTARY_STRATA":raise ValueError("scope")
    groups={}
    for s in documented["result"]["strata"]:
        groups.setdefault(s["stratum"][1],[]).append(s)
    metrics={}
    for metric,ss in groups.items():
        eligible=[s for s in ss if s["contrast"] is not None]
        vals=[v for s in eligible for v in (s["contrast"],s["stability"]["minimum"],s["stability"]["maximum"])]
        complete=len(eligible)==len(ss) and documented["coverage"]["included"]==documented["coverage"]["supplied"]
        metrics[metric]={"envelope":[min(vals),max(vals)] if vals else [None,None],"complete":complete,"strata":deepcopy(ss),"direction":"POSITIVE" if complete and vals and min(vals)>0 else "NEGATIVE" if complete and vals and max(vals)<0 else "UNRESOLVED"}
    routes={k:sorted({fact["ref"][2] for fact in m["facts"]} & set(metrics)) for k,m in e3["mechanisms"].items()}
    scenarios={s["id"]:{"metrics":sorted({f for k in s["mechanism_ids"] for f in routes[k]}),"status":s["status"],"predictive_effect":None} for s in e3["scenarios"]}
    return {"documented_sha256":digest(documented),"e2_sha256":digest(e2),"e3_sha256":digest(e3),"e4_sha256":digest(e4),"metrics":metrics,"mechanism_metric_candidates":routes,"scenario_context":scenarios,"forecast":None,"market_decision":"NOT_EVALUATED","qualification":"BLOCKED"}
