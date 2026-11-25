import unittest,copy
from d0_contract import validate
from football_pipeline_demo import analyze
def fixture():
    return {"schema":"D0_EXPERIMENTAL_V1","sport":"football","origin":"synthetic","engine_access":False,"cutoff":"2026-01-10T12:00:00Z","kickoff":"2026-01-10T15:00:00Z","observations":[{"id":f"{s}{i}","side":s,"source":"synthetic_fixture","event_end":f"2026-01-0{i+1}T12:00:00Z","available_at":f"2026-01-0{i+1}T13:00:00Z","captured_at":f"2026-01-0{i+1}T14:00:00Z","stats":{"shots_for":10,"shots_against":8,"target_for":4,"target_against":3}} for s in ("home","away") for i in range(5)]}
class ContractTests(unittest.TestCase):
    def test_replay(self):
        d=fixture()
        self.assertEqual(analyze(d),analyze(copy.deepcopy(d)))
        self.assertEqual(analyze(d)["decision"],"ABSTENTION")
    def test_leakage(self):
        d=fixture();d["observations"][0]["available_at"]=d["kickoff"]
        with self.assertRaises(ValueError):validate(d)
    def test_real_locked(self):
        d=fixture();d["origin"]="real"
        with self.assertRaises(ValueError):validate(d)
    def test_duplicate(self):
        d=fixture();d["observations"].append(d["observations"][0])
        with self.assertRaises(ValueError):validate(d)
    def test_missing_timezone(self):
        d=fixture();d["cutoff"]="2026-01-10T12:00:00"
        with self.assertRaises(ValueError):validate(d)
    def test_multisport(self):
        for s in ("nba","tennis"):
            d=fixture();d["sport"]=s;validate(d)
            with self.assertRaises(ValueError):analyze(d)
    def test_p2_not_bypassed(self):
        r=analyze(fixture())
        self.assertIn("home:observation_audit",r["p2_rejections"])
        self.assertFalse(r["engine_access"])
