"""Synthetic-only integration boundary; not a sporting engine."""
from d0_contract import validate,digest
from kraft_report import build_report
from kraft_synthetic_adapters import build as build_other
from kraft_phase_guard import FORBIDDEN
from copy import deepcopy
from pathlib import Path
import hashlib

def run(d):
    def guard(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k.lower() in FORBIDDEN or (k=="engine_access" and v is not False) or (k=="publication" and v!="BLOCKED"):
                    raise ValueError("phase or quarantine")
                guard(v)
        elif isinstance(x,list):
            for v in x: guard(v)
    guard(d)
    snapshot=deepcopy(d)
    fingerprint=validate(snapshot)
    sport=snapshot["sport"]
    report=build_report(snapshot) if sport=="football" else build_other(snapshot)
    if report is not None:
        guard(report)
        if report["input_sha256"]!=fingerprint or len(report["sections"])!=7:
            raise ValueError("report contract")
        if any(not set(s["evidence_ids"])<=report["evidence"].keys() for s in report["sections"]):
            raise ValueError("evidence link")
    if digest(snapshot)!=fingerprint:raise ValueError("input mutation")
    result={"schema":"KRAFT_INTEGRATION_V1","sport":sport,"origin":"synthetic","input_sha256":fingerprint,
        "reference_sha256":hashlib.sha256(Path(__file__).with_name("KRAFT_V3_REFERENCE.txt").read_bytes()).hexdigest(),
        "engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED",
        "status":"DESCRIPTIVE_PROTOTYPE" if report is not None else "ADAPTER_NOT_IMPLEMENTED",
        "report":report,"sporting_analysis_complete":False}
    guard(result)
    return result
