import json
import unittest
from pathlib import Path
from d0_contract import digest
from c4_trajectories import build
from c4_e4 import generate
from c4_event_conditional import compare
from test_kraft_synthetic_adapters import fixture_other

class P24Tests(unittest.TestCase):
    def test_frozen_cases(self):
        oracle=json.loads(Path(__file__).with_name("p24_expected.json").read_text())
        for case,t,expected in oracle["cases"]:
            with self.subTest(case=case):
                d=fixture_other("nba")
                e=dict(sport="nba",origin="synthetic",participants=["A","B"])
                dep=dict(mechanisms={"pace":{"issues":[]}},sequences=[])
                tr=build(dep)
                c=dict(event_sha256=digest(e),sport="nba",family="team_total",unit="points",period="including_overtime",subject="A",direction="over")
                if case=="P08":e["origin"]="real"
                e4=generate(d,[1],"fixture",{},1,1,[],{})
                packet=dict(input_sha256=digest(d),event_sha256=digest(e),trajectory_sha256=digest(tr),e4_sha256=digest(e4),evidence_ids=["A"],basis="explicit_fictional_assumptions",scenarios=[dict(assignment=r["assignment"],assumption="Fictional supplied bounds, not inferred from history",bounds=list(oracle["range"])) for r in tr["trajectories"]])
                if case=="P04":packet["evidence_ids"]=[]
                if case=="P05":packet["scenarios"][1]["bounds"]=[90,95]
                if case=="P06":c["period"]="regulation"
                if case=="P09":packet["basis"]="historical_mean"
                h=digest(packet)
                if case=="P07":packet["scenarios"][0]["bounds"]=[0,1]
                actual=compare(d,e,dep,tr,c,packet,h,t)
                print("P24",case,expected,actual["state"],flush=True)
                self.assertEqual(actual["state"],expected)
                self.assertFalse(actual["engine_access"])
                self.assertFalse(actual["predictive_validity_verified"])
                self.assertEqual(actual["qualification"],"BLOCKED")
                self.assertEqual(actual["publication"],"BLOCKED")
