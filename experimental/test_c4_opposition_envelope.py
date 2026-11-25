import unittest
from c4_opposition_envelope import build
class OppositionEnvelopeTests(unittest.TestCase):
    def fixture(self,lo,hi,included=6):
        d={"scope":"EXACT_SYNTHETIC_DOCUMENTARY_STRATA","coverage":{"included":included,"supplied":6},"result":{"strata":[{"stratum":["nba","points_for","ctx","X"],"contrast":(lo+hi)/2,"stability":{"minimum":lo,"maximum":hi}}]}}
        e3={"mechanisms":{"m":{"facts":[{"ref":["A","recent","points_for"]}]},"n":{"facts":[{"ref":["B","recent","rebounds"]}]}},"scenarios":[{"id":"holds","mechanism_ids":["m"],"status":"UNVERIFIED_HYPOTHESIS"},{"id":"fails","mechanism_ids":["m"],"status":"BLOCKED"}]}
        return build(d,{},e3,{})
    def test_directions(self):
        for lo,hi,n,expected in [(1,3,6,"POSITIVE"),(-3,-1,6,"NEGATIVE"),(-1,3,6,"UNRESOLVED"),(1,3,5,"UNRESOLVED")]:
            with self.subTest(expected=expected):
                r=self.fixture(lo,hi,n)
                self.assertEqual(r["metrics"]["points_for"]["direction"],expected)
                self.assertEqual(r["metrics"]["points_for"]["envelope"],[lo,hi])
                self.assertIsNone(r["forecast"])
    def test_routes(self):
        r=self.fixture(1,3)
        self.assertEqual(r["mechanism_metric_candidates"],{"m":["points_for"],"n":[]})
        self.assertEqual(r["scenario_context"]["holds"]["metrics"],["points_for"])
        self.assertEqual(r["scenario_context"]["fails"]["metrics"],["points_for"])
        self.assertEqual(r["scenario_context"]["fails"]["status"],"BLOCKED")
        self.assertIsNone(r["scenario_context"]["holds"]["predictive_effect"])
        self.assertEqual(r["market_decision"],"NOT_EVALUATED")
