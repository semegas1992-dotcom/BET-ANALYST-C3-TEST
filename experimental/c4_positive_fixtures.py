"""Deterministic fictional dossiers; never external evidence."""
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
from c4_e1 import LOTS
from d0_contract import digest
def dossier(sport):
    d=fixture() if sport=="football" else fixture_other(sport)
    ps=["home","away"] if sport=="football" else d["participants"]
    e=dict(id="fictional-"+sport,origin="synthetic",sport=sport,participants=ps,kickoff=d["kickoff"],competition="fictional league",category="fixture",venue="fictional venue",format="fixture",status="scheduled")
    records=[]
    def record(topic,key,measurement):
        i="r"+str(len(records))
        records.append(dict(id=i,topic=topic,event_id=e["id"],source="synthetic_fixture",available_at=d["cutoff"],captured_at=d["cutoff"],status="Contrôlée",opened=True,scope_checked=True,coherence_checked=True,excerpt=measurement,provider_group="fictional",claim_key=key,measurement=measurement))
        return i
    essential=[k for v in LOTS.values() for k in v]
    for k in essential:record(k,"event:"+k+":fixture:label","fictional "+k)
    x={k:[] for k in ("observations","configurations","comparables","indicators","sequences")}
    for o in d["observations"]:
        i=o["id"];p=o.get("side",o.get("participant"))
        a=record("production",i+":stats:historical:record",str(o["stats"]))
        x["observations"].append(dict(observation_id=i,participant=p,historical_event_id="historical-"+i,record_ids=[a]))
        b=record("baseline",i+":context:historical:label","fictional comparable with different opponent")
        x["comparables"].append(dict(observation_id=i,similarity="same fictional format",difference="different opponent",lesson="compare descriptive production only",counterexample="opponent may change production",record_ids=[b]))
        metrics={"football":{"goals_for":2,"goals_against":1,"xg":1.4,"xga":.8},"nba":{"points_for":100,"possessions":80,"turnovers":12},"tennis":{"first_serve_won":20,"first_serve_played":30,"second_serve_won":10,"second_serve_played":20,"break_points_won":2,"break_points_played":5}}[sport]
        for f,v in metrics.items():
            unit="expected_goals" if f in ("xg","xga") else "goals" if f.startswith("goals") else f if f in ("possessions","turnovers") else "points"
            a=record("production",i+":"+f+":historical:"+unit,str(v))
            x["indicators"].append(dict(observation_id=i,metric=f,value=v,unit=unit,record_ids=[a]))
    for p in ps:
        a=record("availability",p+":role:prematch:label","available fictional participant")
        x["configurations"].append(dict(participant=p,person_id=p+"-role",availability="available",role="fictional primary role",record_ids=[a]))
    return d,e,records,essential,x
