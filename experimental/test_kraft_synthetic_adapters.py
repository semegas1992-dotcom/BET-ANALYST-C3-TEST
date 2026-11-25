import unittest
from kraft_integration import run
def fixture_other(sport):
    stats={"points_for":100,"points_against":90} if sport=="nba" else {"service_points_won":30,"service_points_played":50}
    return {"schema":"D0_EXPERIMENTAL_V1","sport":sport,"origin":"synthetic","engine_access":False,"participants":["A","B"],"cutoff":"2026-01-02T00:00:00Z","kickoff":"2026-01-03T00:00:00Z","observations":[{"id":p,"participant":p,"source":"synthetic_fixture","event_end":"2026-01-01T00:00:00Z","available_at":"2026-01-01T01:00:00Z","captured_at":"2026-01-01T02:00:00Z","stats":dict(stats)} for p in ("A","B")]}
class AdapterTests(unittest.TestCase):
    def test_nba(self):
        r=run(fixture_other("nba"))["report"]["evidence"]
        self.assertEqual(r["A:all:points_for"]["metric"]["mean"],100)
        self.assertIsNone(r["A:all:rebounds"]["metric"]["mean"])
    def test_tennis(self):
        r=run(fixture_other("tennis"))["report"]["evidence"]
        self.assertEqual(r["A:all:service_rate"]["metric"]["ratio"],0.6)
        self.assertIsNone(r["A:all:return_rate"]["metric"]["ratio"])
    def test_invalid(self):
        d=fixture_other("tennis");d["observations"][0]["stats"]["service_points_won"]=51
        with self.assertRaises(ValueError):run(d)
    def test_negative(self):
        d=fixture_other("nba");d["observations"][0]["stats"]["points_for"]=-1
        with self.assertRaises(ValueError):run(d)
    def test_weighted(self):
        d=fixture_other("tennis");o=dict(d["observations"][0],id="C",stats={"service_points_won":1,"service_points_played":2});d["observations"].append(o)
        self.assertEqual(run(d)["report"]["evidence"]["A:all:service_rate"]["metric"]["ratio"],31/52)
    def test_replay(self):
        for sport in ("nba","tennis"):
            d=fixture_other(sport);self.assertEqual(run(d),run(d));self.assertFalse(run(d)["sporting_analysis_complete"])
