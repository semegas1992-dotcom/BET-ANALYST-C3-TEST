"""Experimental multisport envelope. No promotion of real data."""
import hashlib,json
from datetime import datetime
def stamp(v):
    t=datetime.fromisoformat(v.replace("Z","+00:00"))
    if t.tzinfo is None:raise ValueError("timezone required")
    return t
def digest(d):
    return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def validate(d):
    if d["schema"]!="D0_EXPERIMENTAL_V1" or d["sport"] not in ("football","nba","tennis"):raise ValueError("schema/sport")
    if d["origin"]!="synthetic" or d["engine_access"] is not False:raise ValueError("quarantine")
    cutoff=stamp(d["cutoff"])
    if cutoff>=stamp(d["kickoff"]):raise ValueError("cutoff")
    if not d["observations"]:raise ValueError("empty")
    seen=set()
    for o in d["observations"]:
        if not isinstance(o["id"],str) or not o["id"].strip():raise ValueError("id")
        if o["id"] in seen:raise ValueError("duplicate")
        seen.add(o["id"])
        if not stamp(o["event_end"])<=stamp(o["available_at"])<=stamp(o["captured_at"])<=cutoff:raise ValueError("temporal leakage")
        if o["source"]!="synthetic_fixture":raise ValueError("source")
    return digest(d)
