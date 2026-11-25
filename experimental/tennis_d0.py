"""Tennis D0 synthetic contract; real archive is never pre-match evidence."""
from d0_contract import validate,digest
from kraft_phase_guard import validate_phase
from tennis_csv_adapter import identity
def valid_id(tour,p):
    return isinstance(p,str) and p.startswith(tour+':') and identity(tour,p.split(':',1)[1])==p
from tennis_stat_qualification import qualify,surface_sample
from tennis_independent_audit import audit
def build(d):
    validate_phase(d)
    sha=validate(d)
    if d["sport"]!="tennis":raise ValueError("sport")
    event=d["event"]; tour=event["tour"]; players=event["players"]; surface=event["surface"]
    if tour not in ("ATP","WTA") or len(players)!=2 or len(set(players))!=2 or any(not valid_id(tour,p) for p in players):raise ValueError("identity")
    if surface not in ("hard","clay","grass","carpet") or event["best_of"] not in (3,5):raise ValueError("event")
    rows=[]
    for o in d["observations"]:
        r=o["row"]
        if r["id"]!=o["id"] or r["tour"]!=tour or r["winner_id"]==r["loser_id"] or not set(players).intersection((r["winner_id"],r["loser_id"])) or any(not valid_id(tour,p) for p in (r["winner_id"],r["loser_id"])):raise ValueError("history identity")
        if r["surface"] not in ("hard","clay","grass","carpet") or not qualify(r)["score_valid"]:raise ValueError("history score/surface")
        rows.append(r)
    a=audit(rows,qualify)
    if a["status"]!="PASS":raise ValueError("audit")
    out={"schema":"D0_TENNIS_QUARANTINE_V1","origin":"synthetic","event":event,"cutoff":d["cutoff"],"input_sha256":sha,"evidence":[{"id":o["id"],"source":o["source"],"event_end":o["event_end"],"available_at":o["available_at"],"captured_at":o["captured_at"],"sha256":digest(o)} for o in d["observations"]],"samples":{p:surface_sample(rows,p,surface) for p in players},"audit":a,"qualification":"BLOCKED","reasons":["synthetic_only","real_availability_unverified","rights_unconfirmed"],"engine_access":False,"publication":"BLOCKED"}
    out["kickoff"]=d["kickoff"]
    validate_phase(out)
    out["sha256"]=digest(out)
    return out
