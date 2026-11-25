"""Synthetic documentary quality gate; no external retrieval or verification."""
from c4_e1 import plan,LOTS
from d0_contract import digest
FAILED={"Accès bloqué","Périmètre inadéquat","Non trouvée après recherche","Accessible, non extraite"}
def assess(event,cutoff,records,essential):
    base=plan(event,cutoff,records)
    topics={k for v in LOTS.values() for k in v}
    if not isinstance(essential,list) or not essential or any(k not in topics for k in essential) or "identity" not in essential:raise ValueError("essential topics")
    seen={};groups={};replacements=[]
    for row in records:
        key=row["id"];provider=row.get("provider_group")
        if not isinstance(provider,str) or not provider.strip():raise ValueError("provider group")
        if "replaces" in row:
            prev=seen.get(row["replaces"])
            if not prev or prev["topic"]!=row["topic"] or prev["status"] not in FAILED:raise ValueError("replacement")
            replacements.append({"previous":prev["id"],"replacement":key,"status":row["status"]})
        seen[key]=row
        if row["status"]!="Contrôlée":continue
        claim=row.get("claim_key");measure=row.get("measurement")
        if not isinstance(claim,str) or not claim.strip() or not isinstance(measure,str) or not measure.strip():raise ValueError("comparable claim")
        # Claim key must explicitly encode participant, definition, period and unit.
        groups.setdefault((row["topic"],claim),[]).append(row)
    conflicts=[];dependencies=[];resolved=set()
    for (topic,claim),rows in sorted(groups.items()):
        providers=sorted({r["provider_group"] for r in rows})
        dependencies.append({"topic":topic,"claim_key":claim,"provider_groups":providers,"record_ids":[r["id"] for r in rows]})
        if len({r["measurement"] for r in rows})>1:
            conflicts.append({"topic":topic,"claim_key":claim,"record_ids":[r["id"] for r in rows]})
        else:resolved.add(topic)
    blocked={c["topic"] for c in conflicts}
    blocked.update(r["topic"] for r in records if r["status"]=="Contradictoire")
    missing=sorted(set(essential)-resolved| (set(essential)&blocked))
    base.update({"essential_topics":sorted(set(essential)),"missing_or_unresolved":missing,"contradictions":conflicts,"dependencies":dependencies,"replacements":replacements,"synthetic_documentary_gate":not missing,"record_set_sha256":digest(records),"essential_scope_sha256":digest(sorted(set(essential))),"collection_complete":False})
    return base
