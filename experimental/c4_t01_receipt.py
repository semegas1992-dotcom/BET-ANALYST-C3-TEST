"""Quarantine-only byte receipt; no schema conversion or admission."""
import hashlib,json
def receive(raw, expected_sha256):
    if not isinstance(raw,bytes) or not 0<len(raw)<=1048576: raise ValueError("size/type")
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=expected_sha256: raise ValueError("byte integrity")
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out: raise ValueError("duplicate key")
            out[k]=v
        return out
    def reject_constant(x): raise ValueError("nonfinite JSON")
    data=json.loads(raw.decode("utf-8"),object_pairs_hook=unique,parse_constant=reject_constant)
    if not isinstance(data,dict): raise ValueError("object required")
    return {"case":"T01","sha256":actual,"size":len(raw),"status":"QUARANTINE_UNMAPPED","engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
