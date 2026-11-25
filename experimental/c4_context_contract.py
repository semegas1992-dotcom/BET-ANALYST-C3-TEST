"""Synthetic evidence-linked context contracts. No automatic tactical inference."""
from d0_contract import digest,stamp
from kraft_phase_guard import validate_phase
from math import isfinite
METRICS={"football":{"goals_for":"goals","goals_against":"goals","xg":"expected_goals","xga":"expected_goals"},"nba":{"possessions":"possessions","turnovers":"turnovers","points_for":"points","points_against":"points"},"tennis":{"first_serve_won":"points","first_serve_played":"points","second_serve_won":"points","second_serve_played":"points","break_points_won":"points","break_points_played":"points"}}
SEQUENCES={"football":("opening","middle","ending"),"nba":("starting_five","rotations","adjustments","ending"),"tennis":("installation","set_evolution","set_ending","following_sets")}
def build(d,event,records,extra,hypotheses):
    validate_phase({"engine_access":False,"extra":extra})
    if set(extra)!={"observations","configurations","comparables","indicators","sequences"}:raise ValueError("context fields")
    ps=set(event["participants"]);cut=stamp(d["cutoff"])
    obs={o["id"]:o for o in d["observations"]}
    rec={r["id"]:r for r in records if r["status"]=="Contrôlée"}
    def words(x):return isinstance(x,str) and bool(x.strip())
    def evidence(ids,topic):
        if not isinstance(ids,list) or not ids or len(set(ids))!=len(ids) or any(i not in rec or rec[i]["topic"]!=topic for i in ids):raise ValueError("evidence scope")
    links={};seen=set()
    for x in extra["observations"]:
        i=x["observation_id"];p=x["participant"];e=x["historical_event_id"]
        if i not in obs or i in links or p not in ps or p!=obs[i].get("side",obs[i].get("participant")) or not words(e) or (e,p) in seen:raise ValueError("observation identity")
        evidence(x["record_ids"],"production")
        if any(stamp(rec[j]["available_at"])<stamp(obs[i]["event_end"]) for j in x["record_ids"]):raise ValueError("observation evidence chronology")
        seen.add((e,p));links[i]=x
    people=set()
    for x in extra["configurations"]:
        k=(x["participant"],x["person_id"])
        if k in people:raise ValueError("duplicate configuration")
        people.add(k)
        if x["participant"] not in ps or not words(x["person_id"]) or x["availability"] not in ("available","uncertain","absent","unknown") or not words(x["role"]):raise ValueError("configuration")
        evidence(x["record_ids"],"availability")
        if x["availability"]=="absent" and x.get("projected_minutes") is not None:raise ValueError("absent projection")
        if x.get("projected_minutes") is not None:raise ValueError("minutes model unavailable")
    for x in extra["comparables"]:
        if x["observation_id"] not in links or any(not words(x.get(k)) for k in ("similarity","difference","lesson","counterexample")):raise ValueError("comparable")
        evidence(x["record_ids"],"baseline")
    measures=set()
    for x in extra["indicators"]:
        k=(x["observation_id"],x["metric"])
        if k in measures:raise ValueError("duplicate indicator")
        measures.add(k)
        f=x["metric"];v=x["value"]
        if x["observation_id"] not in links or f not in METRICS[d["sport"]] or x["unit"]!=METRICS[d["sport"]][f] or type(v) not in (int,float) or not isfinite(v) or v<0:raise ValueError("indicator")
        evidence(x["record_ids"],"production")
    sequences=[];seen=set()
    scenarios={s["id"]:s for s in hypotheses["scenarios"]}
    for x in extra["sequences"]:
        k=(x["scenario_id"],x["phase"])
        if k in seen or k[0] not in scenarios or k[1] not in SEQUENCES[d["sport"]] or any(not words(x.get(f)) for f in ("starting_state","expected_behavior","opponent_response","turning_point","uncertainty")):raise ValueError("sequence")
        seen.add(k);s=scenarios[k[0]]
        sequences.append({**x,"issues":s["issues"],"status":"BLOCKED" if s["issues"] else "UNVERIFIED_HYPOTHESIS"})
    return {"input_sha256":digest(d),"context_sha256":digest(extra),"linked_observations":len(links),"unlinked_observations":sorted(set(obs)-set(links)),"configurations":extra["configurations"],"comparables":extra["comparables"],"indicators":extra["indicators"],"sequences":sequences,"scope":"synthetic supplied assertions, not authenticated or inferred","engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
