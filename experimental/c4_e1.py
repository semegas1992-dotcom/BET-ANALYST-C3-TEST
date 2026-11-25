"""Synthetic research planning and evidence gate, not a network collector."""
from d0_contract import stamp,digest
from kraft_phase_guard import validate_phase
LOTS={"A":("identity","baseline","recent_form","conditions","calendar","standings","stakes"),"B":("production","concession","efficiency","variation"),"C":("availability","configuration","roles","individual_metrics")}
def plan(event,cutoff,records):
    validate_phase({"engine_access":False,"event":event,"records":records})
    if event.get("origin")!="synthetic" or event.get("sport") not in ("football","nba","tennis"):raise ValueError("synthetic only")
    for key in ("id","competition","category","venue","format","status"):
        if not isinstance(event.get(key),str) or not event[key].strip():raise ValueError(key)
    ps=event["participants"]
    if not isinstance(ps,list) or len(ps)!=2 or any(not isinstance(v,str) or not v.strip() for v in ps) or len(set(ps))!=2:raise ValueError("participants")
    if event["status"]!="scheduled" or stamp(cutoff)>=stamp(event["kickoff"]):raise ValueError("not pre-match")
    slots={k:[] for fields in LOTS.values() for k in fields};seen=set()
    for rec in records:
        i=rec["id"]
        if not isinstance(i,str) or not i.strip() or i in seen:raise ValueError("record id")
        seen.add(i)
        if rec["topic"] not in slots or rec["event_id"]!=event["id"] or rec["source"]!="synthetic_fixture":raise ValueError("scope")
        if not stamp(rec["available_at"])<=stamp(rec["captured_at"])<=stamp(cutoff):raise ValueError("temporal")
        if rec["status"] not in ("Contrôlée","Provisoire","Accès bloqué","Accessible, non extraite","Périmètre inadéquat","Non trouvée après recherche","Contradictoire"):raise ValueError("status")
        if rec["status"]=="Contrôlée" and (rec.get("opened") is not True or rec.get("scope_checked") is not True or rec.get("coherence_checked") is not True or not isinstance(rec.get("excerpt"),str) or not rec["excerpt"].strip()):raise ValueError("unverified content")
        slots[rec["topic"]].append({"id":i,"status":rec["status"],"sha256":digest(rec)})
    lots={lot:{k:slots[k] or [{"status":"Non recherchée"}] for k in fields} for lot,fields in LOTS.items()}
    return {"schema":"C4_E1_SYNTHETIC_V1","event_sha256":digest(event),"cutoff":cutoff,"lots":lots,"official_identity_verified":False,"collection_complete":False,"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
