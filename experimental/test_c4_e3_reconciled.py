import unittest
from fractions import Fraction
from c4_e3 import build
from c4_e2_quality import assess
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
def inputs():
    m={"id":"m","refs":[["home","all","shots_for"],["away","all","shots_against"]],"interpretation":"synthetic hypothesis","opponent_effect":"possible opposition","objection":"not contextualized"}
    s={"id":"s","mechanism_ids":["m"],"condition":"if hypothesis holds","course":"conditional sequence","trigger":"change","consequence":"review","objection":"uncertain"}
    return m,s
class E3ParallelTests(unittest.TestCase):
    def test_independent_ratio(self):
        d=fixture_other("tennis");d["observations"].append(dict(d["observations"][0],id="extra",stats={"service_points_won":1,"service_points_played":2}))
        v=assess(d,2,"fixture",{},1,1,{})["sensitivity"]["A"]["all"]["service_rate"]
        self.assertEqual(v["full"],float(Fraction(31,52)))
    def test_reduced_gate(self):
        d=fixture();m,s=inputs()
        r=build(d,5,"fixture",{},5,1,{"home0":"declared"},[m],[s])
        self.assertIn("REDUCED_SAMPLE_INSUFFICIENT",r["scenarios"][0]["issues"])
    def test_propagation(self):
        m,s=inputs();r=build(fixture(),5,"fixture",{},6,1,{},[m],[s])
        self.assertEqual(r["scenarios"][0]["status"],"BLOCKED")
    def test_hypothesis(self):
        m,s=inputs();r=build(fixture(),5,"fixture",{},2,1,{},[m],[s])
        self.assertEqual(r["scenarios"][0]["status"],"UNVERIFIED_HYPOTHESIS");self.assertFalse(r["sporting_analysis_complete"])
    def test_unknown(self):
        m,s=inputs();m["refs"][0][2]="unknown"
        with self.assertRaises(ValueError):build(fixture(),5,"fixture",{},2,1,{},[m],[s])
    def test_empty(self):
        r=build(fixture(),5,"fixture",{},2,1,{},[],[]);self.assertEqual(r["scenarios"],[])

class CatalogTests(unittest.TestCase):
    def test_three_sports(self):
        from c4_e3_catalog import prototype
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            r=prototype(d,5,"fixture",{},2,1,{})
            self.assertEqual(len(r["mechanisms"]),2)
            self.assertEqual(r["scenarios"],[])
            self.assertFalse(r["engine_access"])
    def test_missing_tennis(self):
        from c4_e3_catalog import prototype
        r=prototype(fixture_other("tennis"),5,"fixture",{},1,1,{})
        self.assertTrue(all(m["status"]=="BLOCKED" for m in r["mechanisms"].values()))
