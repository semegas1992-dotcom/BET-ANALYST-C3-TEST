import unittest
from c4_e3_competing import generate,check
from c4_e2_dispersion_audit import audit
from c4_e2_quality import assess
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
class CompetingTests(unittest.TestCase):
    def test_dispersion(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            d["observations"][0]["context"]={"venue":"home"}
            r=assess(d,2,"fixture",{"venue":"home"},1,1,{})
            a=audit(d,r);self.assertTrue(a["passed"],a["issues"])
    def test_tamper(self):
        d=fixture();r=assess(d,2,"fixture",{},1,1,{})
        r["metrics"]["home"]["shots_for"]["all"]["population_sd"]=99
        self.assertFalse(audit(d,r)["passed"])
    def test_branches(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            r=generate(d,2,"fixture",{},1,1,{})
            self.assertEqual(len(r["scenarios"]),8);self.assertTrue(check(r))
    def test_block(self):
        r=generate(fixture(),2,"fixture",{},6,1,{})
        self.assertTrue(all(s["status"]=="BLOCKED" for s in r["scenarios"]))
    def test_incomplete(self):
        r=generate(fixture(),2,"fixture",{},1,1,{})
        r["scenarios"].pop()
        with self.assertRaises(ValueError):check(r)
    def test_context(self):
        r=generate(fixture(),2,"fixture",{"venue":"unknown"},1,1,{})
        self.assertTrue(all(s["status"]=="BLOCKED" for s in r["scenarios"]))
