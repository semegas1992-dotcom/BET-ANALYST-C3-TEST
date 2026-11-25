"""Synthetic descriptive sensitivity, never a predictive interval."""
from c4_e2_quality import assess
from c4_e2_independent import audit as sensitivity_audit
from c4_e2_dispersion_audit import audit as dispersion_audit
from d0_contract import digest
from math import isfinite
def generate(d,windows,reason,context,min_n,min_coverage,atypical_ids,thresholds):
    if not isinstance(windows,list) or not windows or any(type(w) is not int or w<1 for w in windows) or len(set(windows))!=len(windows):raise ValueError("windows")
    if not isinstance(thresholds,dict):raise ValueError("thresholds")
    reports=[assess(d,w,reason,context,min_n,min_coverage,atypical_ids) for w in windows]
    audits=[(sensitivity_audit(d,r),dispersion_audit(d,r)) for r in reports]
    if not all(a["passed"] and b["passed"] for a,b in audits):raise ValueError("audit failed")
    base=reports[0];out={}
    if not set(thresholds)<=set(base["sensitivity"]):raise ValueError("participant threshold")
    for p,groups in base["sensitivity"].items():
        policy=thresholds.get(p,{})
        if not isinstance(policy,dict) or not set(policy)<=set(groups["recent"]):raise ValueError("metric threshold")
        out[p]={}
        for f in groups["recent"]:
            t=policy.get(f)
            if f in policy and (type(t) not in (int,float) or not isfinite(t) or t<0 or (f.endswith("_rate") and t>1)):raise ValueError("threshold")
            variants=[]
            for r in reports:
                m=r["sensitivity"][p]["recent"][f]
                for mode,field,gate in (("full","full","sample_gate"),("reduced","without_declared_atypical","reduced_sample_gate")):
                    variants.append({"window":r["window"],"mode":mode,"value":m[field],"qualified":m[gate],"report_sha256":digest(r)})
                if context:
                    m=r["sensitivity"][p]["matched"][f]
                    variants.append({"window":r["window"],"mode":"matched","value":m["full"],"qualified":m["sample_gate"],"report_sha256":digest(r)})
            vals=[v["value"] for v in variants if v["qualified"] and v["value"] is not None]
            complete=len(vals)==len(variants)
            lo,hi=(min(vals),max(vals)) if vals else (None,None)
            state="NOT_REQUESTED" if t is None else "BLOCKED" if not complete else "ALL_AT_OR_ABOVE" if lo>=t else "ALL_BELOW" if hi<t else "SENSITIVE"
            out[p][f]={"variants":variants,"descriptive_envelope":[lo,hi],"complete":complete,"threshold":t,"threshold_state":state,"conditional_estimate":base["sensitivity"][p]["recent"][f]["full"] if complete else None,"estimate_assumption":"Historical recent mean or pooled ratio under unchanged descriptive conditions; not a forecast"}
    return {"schema":"C4_E4_SYNTHETIC_V1","input_sha256":base["input_sha256"],"metrics":out,"audit_checks":sum(a["checks"]+b["checks"] for a,b in audits),"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED","predictive_validity_verified":False}
