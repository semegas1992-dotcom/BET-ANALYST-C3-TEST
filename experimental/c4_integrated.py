"""Integrated synthetic replay, not a completed sporting analysis."""
from c4_e1_quality import assess as documentary
from c4_e2_quality import assess
from c4_e2_independent import audit as arithmetic
from c4_e2_dispersion_audit import audit as dispersion
from c4_e3_competing import generate as scenarios
from c4_e4 import generate as envelopes
from c4_e4_trace import audit as envelope_audit
from c4_e5_descriptive import compare
from c4_e5_inventory import inventory
from d0_contract import digest,stamp,validate
def run(d,event,records,essential,windows,reason,context,min_n,min_coverage,atypical,requests):
    fingerprint=validate(d)
    participants=["home","away"] if d["sport"]=="football" else d["participants"]
    if event["sport"]!=d["sport"] or event["participants"]!=participants or stamp(event["kickoff"])!=stamp(d["kickoff"]):raise ValueError("event mismatch")
    if not windows:raise ValueError("windows")
    doc=documentary(event,d["cutoff"],records,essential)
    stats=assess(d,windows[0],reason,context,min_n,min_coverage,atypical)
    audits=[arithmetic(d,stats),dispersion(d,stats)]
    if not all(a["passed"] for a in audits):raise ValueError("statistical audit")
    hypotheses=scenarios(d,windows[0],reason,context,min_n,min_coverage,atypical)
    args=(windows,reason,context,min_n,min_coverage,atypical,{})
    env=envelopes(d,*args);review=envelope_audit(d,env,*args)
    if not review["passed"]:raise ValueError("envelope audit")
    comparisons=[]
    for request in requests:
        c=compare(d,*args[:-1],request["contract"],request["thresholds"])
        if c["envelope_report_sha256"]!=digest(env):raise ValueError("envelope mismatch")
        comparisons.append(c)
    stages={"E1":doc,"E2":stats,"E3":hypotheses,"E4":env,"E5":{"inventory":inventory(d["sport"]),"comparisons":comparisons}}
    return {"schema":"C4_INTEGRATED_SYNTHETIC_V1","input_sha256":fingerprint,"event_sha256":digest(event),"stage_sha256":{k:digest(v) for k,v in stages.items()},"stages":stages,"audits":audits+[review],"documentary_gate":doc["synthetic_documentary_gate"],"limitations":["Event identity only matched to synthetic labels and kickoff","Documentary records not authenticated or linked to individual observations","No verified tactical or sequence projection","No event market evaluation"],"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED","sporting_analysis_complete":False}
