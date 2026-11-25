import unittest
from c4_e2_quality import assess
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
class E2QualityTests(unittest.TestCase):
    def test_weighted(self):
        d=fixture_other("tennis");o=d["observations"][0];d["observations"].append(dict(o,id="extra",stats={"service_points_won":1,"service_points_played":2}))
        m=assess(d,2,"fixture",{},2,1,{})["sensitivity"]["A"]["all"]["service_rate"]
        self.assertEqual(m["full"],31/52);self.assertEqual(m["denominator"],52)
    def test_sensitivity(self):
        d=fixture();o=d["observations"][0];o["stats"]["shots_for"]=30
        m=assess(d,5,"fixture",{},2,1,{o["id"]:"declared atypical"})["sensitivity"]["home"]["all"]["shots_for"]
        self.assertEqual(m["full"],14);self.assertEqual(m["without_declared_atypical"],10)
    def test_missing(self):
        m=assess(fixture_other("nba"),2,"fixture",{},2,1,{})["sensitivity"]["A"]["all"]["rebounds"]
        self.assertFalse(m["sample_gate"]);self.assertIsNone(m["full"])
    def test_zero_denominator(self):
        d=fixture_other("tennis");d["observations"][0]["stats"].update(service_points_won=0,service_points_played=0)
        m=assess(d,2,"fixture",{},1,1,{})["sensitivity"]["A"]["all"]["service_rate"]
        self.assertIsNone(m["full"]);self.assertEqual(m["n"],0)
    def test_unknown_exclusion(self):
        with self.assertRaises(ValueError):assess(fixture(),2,"fixture",{},1,1,{"unknown":"reason"})
    def test_policy(self):
        with self.assertRaises(ValueError):assess(fixture(),2,"fixture",{},0,1,{})
