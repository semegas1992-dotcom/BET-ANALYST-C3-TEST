import unittest
from c4_e4 import generate
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
class E4Tests(unittest.TestCase):
    def test_multisport(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            r=generate(d,[1,2],"fixture",{},1,1,{},{});self.assertGreater(r["audit_checks"],0);self.assertFalse(r["engine_access"])
    def test_sensitive(self):
        d=fixture();d["observations"][0]["stats"]["shots_for"]=30
        m=generate(d,[1,5],"fixture",{},1,1,{},{"home":{"shots_for":12}})["metrics"]["home"]["shots_for"]
        self.assertEqual(m["descriptive_envelope"],[10,14]);self.assertEqual(m["threshold_state"],"SENSITIVE")
    def test_block(self):
        m=generate(fixture(),[1,5],"fixture",{},2,1,{},{"home":{"shots_for":10}})["metrics"]["home"]["shots_for"]
        self.assertEqual(m["threshold_state"],"BLOCKED");self.assertIsNone(m["conditional_estimate"])
    def test_missing(self):
        m=generate(fixture_other("nba"),[1],"fixture",{},1,1,{},{"A":{"rebounds":5}})["metrics"]["A"]["rebounds"]
        self.assertEqual(m["descriptive_envelope"],[None,None])
    def test_equality(self):
        m=generate(fixture(),[1,2],"fixture",{},1,1,{},{"home":{"shots_for":10}})["metrics"]["home"]["shots_for"]
        self.assertEqual(m["threshold_state"],"ALL_AT_OR_ABOVE")
    def test_invalid(self):
        with self.assertRaises(ValueError):generate(fixture(),[1,1],"fixture",{},1,1,{}, {})
