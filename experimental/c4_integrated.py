"""Integrated synthetic replay, not a completed sporting analysis."""
from c4_scoped_uncertainty import build as scoped_uncertainty
from c4_matched_opposition import contrast, linked_contrast
from c4_trajectory_prompts import build as trajectory_prompts
from c4_availability_routing import route as availability_route
from c4_availability_review import review as availability_review
from c4_interactions import build as interactions, audit as interaction_audit
from c4_market_independent import audit as independent_market_audit
from c4_market_scope import evaluate as market_scope, audit as market_audit
from c4_trajectories import build as trajectories, audit as trajectory_audit
from c4_event_contract import compare as event_compare, audit as event_audit
from c4_dependency_audit import audit as dependency_audit
from c4_specific_dependencies import evaluate as specific
from c4_context_analysis import enrich
from c4_context_contract import build as context_contract
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
def run(d,event,records,essential,windows,reason,context,min_n,min_coverage,atypical,requests,extra=None,event_requests=(),market_requests=(),matched_rows=()):
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
    if matched_rows and extra is None:
        if any(row["sport"]!=d["sport"] for row in matched_rows):raise ValueError("matched sport")
        stages["matched_opposition"]={"input_sha256":digest(matched_rows),"result":contrast(matched_rows),"provenance":"SUPPLIED_UNVERIFIED"}
    stages["E5"]["event_contracts"]=[]
    for request in event_requests:
        c=event_compare(event,request["contract"],request["thresholds"])
        audits.append(event_audit(event,c))
        stages["E5"]["event_contracts"].append(c)
    if extra is not None:
        stages["context"]=context_contract(d,event,records,extra,hypotheses)
        if matched_rows:
            stages["matched_opposition"]=linked_contrast(matched_rows,d,event,extra,records)
        stages["specific_dependencies"]=specific(d,event,extra,doc,hypotheses)
        stages["dependency_audit"]=dependency_audit(d,event,extra,doc,hypotheses,stages["specific_dependencies"])
        audits.append(stages["dependency_audit"])
        stages["trajectories"]=trajectories(stages["specific_dependencies"])
        audits.append(trajectory_audit(stages["specific_dependencies"],stages["trajectories"]))
        stages["scoped_uncertainty"]=scoped_uncertainty(stages["specific_dependencies"],stages["trajectories"])
        stages["trajectory_prompts"]=trajectory_prompts(d["sport"],stages["trajectories"])
        stages["interactions"]=interactions(d["sport"],stages["specific_dependencies"],stages["trajectories"])
        audits.append(interaction_audit(stages["specific_dependencies"],stages["trajectories"],stages["interactions"]))
        stages["context_analysis"]=enrich(d,event,extra,stages["context"],doc,hypotheses)
        stages["availability_review"]=availability_review(d["sport"],extra["configurations"],stages["context_analysis"]["summary"])
    if market_requests and extra is None:raise ValueError("context required")
    stages["E5"]["market_scopes"]=[]
    for request in market_requests:
        m=market_scope(event,extra,stages["trajectories"],request["contract"],request["thresholds"])
        audits.append(market_audit(event,extra,stages["trajectories"],m))
        audits.append(independent_market_audit(event,extra,stages["trajectories"],m))
        stages["E5"]["market_scopes"].append(m)
    if extra is not None:
        stages["availability_routing"]=availability_route(event,stages["availability_review"],stages["trajectories"],stages["E5"]["market_scopes"])
    return {"schema":"C4_INTEGRATED_SYNTHETIC_V1","input_sha256":fingerprint,"event_sha256":digest(event),"stage_sha256":{k:digest(v) for k,v in stages.items()},"stages":stages,"audits":audits+[review],"documentary_gate":doc["synthetic_documentary_gate"],"limitations":["Event identity only matched to synthetic labels and kickoff","Documentary records not authenticated or linked to individual observations","No verified tactical or sequence projection","No event market evaluation"],"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED","sporting_analysis_complete":False}
