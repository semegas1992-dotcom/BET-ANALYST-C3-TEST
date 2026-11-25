import unittest
from c4_e3_conditional import generate
from c4_e2_independent import audit
from c4_e2_quality import assess
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
class ConditionalTests(unittest.TestCase):
    def test_catalog(self):
        for d,n in ((fixture(),4),(fixture_other("nba"),2),(fixture_other("tennis"),2)):
            r=generate(d,5,"fixture",{},1,1,{})
            self.assertEqual(len(r["scenarios"]),n)
            self.assertFalse(r["engine_access"])
            self.assertTrue(all(s["mechanism_ids"][0] in r["mechanisms"] for s in r["scenarios"]))
    def test_propagation(self):
        r=generate(fixture(),5,"fixture",{},6,1,{})
        self.assertTrue(all(s["status"]=="BLOCKED" for s in r["scenarios"]))
    def test_missing_return(self):
        r=generate(fixture_other("tennis"),5,"fixture",{},1,1,{})
        self.assertTrue(all("MISSING_MEASUREMENT" in s["issues"] for s in r["scenarios"]))
    def test_audit(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            a=audit(d,assess(d,2,"fixture",{},1,1,{d["observations"][0]["id"]:"test"}))
            self.assertTrue(a["passed"],a["issues"])
            self.assertGreater(a["checks"],0)
    def test_tampering(self):
        d=fixture();r=assess(d,2,"fixture",{},1,1,{})
        r["sensitivity"]["home"]["all"]["shots_for"]["full"]+=1
        self.assertFalse(audit(d,r)["passed"])
