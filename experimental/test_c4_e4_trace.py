import unittest
from c4_e4 import generate
from c4_e4_trace import audit
from c4_e5_inventory import inventory
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
class TraceTests(unittest.TestCase):
    def test_replay(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            args=([1,2],"fixture",{},1,1,{}, {})
            a=audit(d,generate(d,*args),*args)
            self.assertTrue(a["passed"],a["issues"])
    def test_tamper(self):
        d=fixture();args=([1,2],"fixture",{},1,1,{},{"home":{"shots_for":10}})
        r=generate(d,*args);r["metrics"]["home"]["shots_for"]["threshold_state"]="SENSITIVE"
        self.assertFalse(audit(d,r,*args)["passed"])
    def test_inventory(self):
        for sport in ("football","nba","tennis"):
            r=inventory(sport);self.assertTrue(all(f["status"]=="NOT_EVALUATED" for f in r["families"]))
        self.assertNotIn("corners",[f["family"] for f in inventory("football")["families"]])
