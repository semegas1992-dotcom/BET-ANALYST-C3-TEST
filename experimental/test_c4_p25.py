import unittest
from d0_contract import digest
from c4_trajectories import build
from c4_e4 import generate
from c4_event_conditional import compare
from test_kraft_synthetic_adapters import fixture_other

class P25Tests(unittest.TestCase):
    def fixture(self):
        d=fixture_other("nba")
        e=dict(sport="nba",origin="synthetic",participants=["A","B"])
        dep=dict(mechanisms={"pace":{"issues":[]}},sequences=[])
        tr=build(dep)
        c=dict(event_sha256=digest(e),sport="nba",family="team_total",unit="points",period="including_overtime",subject="A",direction="over")
        p=dict(input_sha256=digest(d),event_sha256=digest(e),trajectory_sha256=digest(tr),e4_sha256=digest(generate(d,[1],"fixture",{},1,1,{},{})),evidence_ids=["A"],basis="explicit_fictional_assumptions",scenarios=[dict(assignment=r["assignment"],assumption="fictional",bounds=[105,115]) for r in tr["trajectories"]])
        return d,e,dep,tr,c,p
    def test_adversarial(self):
        for case,expected in [("baseline","ABOVE"),("bad_origin","REJECT"),("bad_source","REJECT"),("gate","REJECT"),("missing_trajectory","REJECT"),("duplicate_trajectory","REJECT"),("empty_mechanisms","REJECT"),("bad_identity","ABSTENTION"),("conflicting","UNRESOLVED"),("bad_bounds","REJECT"),("null_packet","REJECT"),("bad_evidence","ABSTENTION"),("hash","REJECT")]:
            with self.subTest(case=case):
                d,e,dep,tr,c,p=self.fixture()
                if case=="bad_origin": e["origin"]="real"
                if case=="bad_source": d["observations"][0]["source"]="external"
                if case=="gate": tr["engine_access"]=True
                if case=="missing_trajectory": tr["trajectories"].pop()
                if case=="duplicate_trajectory": tr["trajectories"][1]=tr["trajectories"][0]
                if case=="empty_mechanisms":
                    dep["mechanisms"]={}
                    tr=build(dep)
                    p["scenarios"]=[dict(assignment={},assumption="fictional",bounds=[105,115])]
                if case=="bad_identity": e["participants"]=["A","C"]
                if case=="conflicting": p["scenarios"][1]["bounds"]=[90,95]
                if case=="bad_bounds": p["scenarios"][0]["bounds"]=[115,105]
                if case=="bad_evidence": p["evidence_ids"]=["B"]
                c["event_sha256"]=digest(e)
                p.update(input_sha256=digest(d),event_sha256=digest(e),trajectory_sha256=digest(tr))
                h=digest(p)
                if case=="hash": h="0"*64
                if case=="null_packet": p=None
                r=compare(d,e,dep,tr,c,p,h,100.5)
                print("P25",case,expected,r["state"],flush=True)
                self.assertEqual(r["state"],expected)
                self.assertIs(r["engine_access"],False)
                self.assertIs(r["predictive_validity_verified"],False)
                self.assertEqual(r["publication"],"BLOCKED")
                self.assertEqual(r["qualification"],"BLOCKED")
