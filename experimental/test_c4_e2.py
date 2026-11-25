import unittest
from c4_e2 import describe
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
from test_c4_e1_quality import QualityTests
from c4_e1_quality import assess
class E2Tests(unittest.TestCase):
    def test_multisport(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            r=describe(d,2,"fixture window",{});self.assertFalse(r["engine_access"]);self.assertEqual(len(r["metrics"]),2)
    def test_dispersion(self):
        d=fixture();d["observations"][0]["stats"]["shots_for"]=14
        m=describe(d,2,"fixture",{})["metrics"]["home"]["shots_for"]
        self.assertAlmostEqual(m["all"]["population_sd"],1.6)
        self.assertAlmostEqual(m["recent_minus_prior"],-4/3)
    def test_context(self):
        d=fixture();d["observations"][0]["context"]={"venue":"home"}
        m=describe(d,2,"fixture",{"venue":"home"})["metrics"]["home"]["shots_for"]
        self.assertEqual(m["matched"]["n"],1)
    def test_missing(self):
        d=fixture_other("nba");m=describe(d,2,"fixture",{})["metrics"]["A"]["rebounds"]
        self.assertIsNone(m["all"]["mean"]);self.assertEqual(m["all"]["missing"],1)
    def test_window(self):
        with self.assertRaises(ValueError):describe(fixture(),0,"",{})
    def test_replacement_time(self):
        e,c,r=QualityTests().rows();bad=dict(r,id="bad",status="Accès bloqué");r=dict(r,replaces="bad",captured_at="2026-01-01T12:00:00Z")
        with self.assertRaises(ValueError):assess(e,c,[bad,r],["identity"])
