"""Generate synthetic dossiers offline; never invoked by verification."""
import json
from pathlib import Path
from d0_contract import digest
from c4_trajectories import build
from c4_e4 import generate
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other

def freeze():
    root=Path(__file__).parent
    oracle=json.loads((root/"p26_expected.json").read_text())
    dossiers=[]
    for sport in ("football","nba","tennis"):
        o=oracle[sport]
        d=fixture() if sport=="football" else fixture_other(sport)
        e=dict(sport=sport,origin="synthetic",participants=["home","away"] if sport=="football" else d["participants"],cutoff=d["cutoff"],kickoff=d["kickoff"],input_sha256=digest(d))
        dep=dict(mechanisms={"pace":{"issues":[]}},sequences=[])
        tr=build(dep)
        c=dict(event_sha256=digest(e),sport=sport,family="team_total",unit=o["unit"],period=o["period"],subject=o["subject"],direction="over")
        t=o["thresholds"][0]
        packet=dict(input_sha256=digest(d),event_sha256=digest(e),trajectory_sha256=digest(tr),e4_sha256=digest(generate(d,[1],"fixture",{},1,1,{},{})),contract_sha256=digest(c),threshold=t,evidence_ids=["home4" if sport=="football" else "A"],basis="explicit_fictional_assumptions",scenarios=[dict(assignment=r["assignment"],assumption="Fictional event bounds, not derived from descriptive evidence",bounds=o["bounds"]) for r in tr["trajectories"]])
        dossiers.append(dict(id="P27C-"+sport,origin="synthetic",engine_access=False,payload=dict(d=d,event=e,dependencies=dep,trajectories=tr,contract=c,packet=packet,threshold=t)))
    registry=dict(schema="P27C_REGISTRY_V1",entries={x["id"]:digest(x) for x in dossiers})
    print("P27C_FREEZE",json.dumps(dict(dossiers=dossiers,registry=registry,pin=digest(registry)),sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__": freeze()
