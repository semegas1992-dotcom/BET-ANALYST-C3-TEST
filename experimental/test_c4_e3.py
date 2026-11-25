import unittest
from fractions import Fraction
from c4_e2_quality import assess
from c4_e3 import review
from test_kraft_synthetic_adapters import fixture_other
class E3Tests(unittest.TestCase):
    def test_independent_ratio(self):
        d=fixture_other("tennis");o=d["observations"][0];d["observations"].append(dict(o,id="extra",stats={"service_points_won":1,"service_points_played":2}))
        v=assess(d,2,"fixture",{},2,1,{"extra":"atypical"})["sensitivity"]["A"]["all"]["service_rate"]
        self.assertEqual(v["full"],float(Fraction(31,52)))
        self.assertEqual(v["without_declared_atypical"],float(Fraction(30,50)))
        self.assertFalse(v["reduced_sample_gate"])
    def test_review(self):
        d=fixture_other("nba")
        m={"id":"m","support":["A","all","points_for"],"opposition":["B","all","points_against"],"interpretation":"hypothesis","opponent_effect":"conditional effect","objection":"uncertain"}
        s={"id":"s","mechanism_ids":["m"],"condition":"if","course":"course","trigger":"trigger","consequence":"effect","objection":"limit"}
        args=(d,2,"fixture",{},2,1,{})
        r=review(*args,[m],[s])
        self.assertIn("insufficient sample",r["scenarios"][0]["limitations"])
        self.assertFalse(r["automatic_reasoning"])
        self.assertFalse(r["engine_access"])
        with self.assertRaises(ValueError):review(*args,[m],[dict(s,mechanism_ids=["missing"])])
    def test_empty(self):
        r=review(fixture_other("nba"),2,"fixture",{},1,1,{},[],[])
        self.assertEqual(r["scenarios"],[])
