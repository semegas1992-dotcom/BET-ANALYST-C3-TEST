import json
import unittest
from pathlib import Path
from d0_contract import digest
from c4_trajectories import build
from c4_e4 import generate
from c4_event_conditional import compare_bound
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other

class P26Tests(unittest.TestCase):
    def test_frozen(self):
        oracle=json.loads(Path(__file__).with_name("p26_expected.json").read_text())
        for sport in ("football","nba","tennis"):
            o=oracle[sport]
            for i,t in enumerate(o["thresholds"]):
                for mutation in (["none"]+list(oracle["mutations"]) if i==0 else ["none"]):
                    with self.subTest(sport=sport,t=t,mutation=mutation):
                        d=fixture() if sport=="football" else fixture_other(sport)
                        e=dict(sport=sport,origin="synthetic",participants=["home","away"] if sport=="football" else d["participants"],cutoff=d["cutoff"],kickoff=d["kickoff"],input_sha256=digest(d))
                        dep=dict(mechanisms={"pace":{"issues":[]}},sequences=[])
                        tr=build(dep)
                        c=dict(event_sha256=digest(e),sport=sport,family="team_total",unit=o["unit"],period=o["period"],subject=o["subject"],direction="over")
                        p=dict(input_sha256=digest(d),event_sha256=digest(e),trajectory_sha256=digest(tr),e4_sha256=digest(generate(d,[1],"fixture",{},1,1,{},{})),contract_sha256=digest(c),threshold=t,evidence_ids=["home4" if sport=="football" else "A"],basis="explicit_fictional_assumptions",scenarios=[dict(assignment=r["assignment"],assumption="Fictional event bounds, not derived from descriptive evidence",bounds=o["bounds"]) for r in tr["trajectories"]])
                        h=digest(p)
                        if mutation=="contract": c["subject"]="away" if sport=="football" else "B"
                        if mutation=="threshold": t+=1
                        if mutation=="time":
                            e["kickoff"]="2027-01-01T00:00:00Z"
                            c["event_sha256"]=digest(e)
                            p.update(event_sha256=digest(e),contract_sha256=digest(c))
                            h=digest(p)
                        if mutation=="hash": h="0"*64
                        if mutation=="missing":
                            del p["contract_sha256"]
                            h=digest(p)
                        r=compare_bound(d,e,dep,tr,c,p,h,t)
                        expected=oracle["expected"][i] if mutation=="none" else oracle["mutations"][mutation]
                        print("P26",sport,i,mutation,expected,r["state"],flush=True)
                        self.assertEqual(r["state"],expected)
                        self.assertIs(r["engine_access"],False)
                        self.assertIs(r["predictive_validity_verified"],False)
                        self.assertEqual(r["publication"],"BLOCKED")
                        self.assertEqual(r["qualification"],"BLOCKED")
