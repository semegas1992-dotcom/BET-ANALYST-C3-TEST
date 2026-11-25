import unittest
from copy import deepcopy
from kraft_integration import run
from test_d0_pipeline_demo import fixture
class IntegrationTests(unittest.TestCase):
    def test_football(self):
        d=fixture();before=deepcopy(d);r=run(d)
        self.assertEqual(d,before)
        self.assertEqual(r,run(d))
        self.assertEqual(len(r["report"]["sections"]),7)
        self.assertFalse(r["sporting_analysis_complete"])
        self.assertFalse(r["engine_access"])
        self.assertEqual(r["publication"],"BLOCKED")
        self.assertEqual(len(r["reference_sha256"]),64)
    def test_other_sports(self):
        for sport in ("nba","tennis"):
            from test_kraft_synthetic_adapters import fixture_other
            r=run(fixture_other(sport));self.assertEqual(len(r["report"]["sections"]),7)
            self.assertEqual(r["status"],"DESCRIPTIVE_PROTOTYPE")
    def test_reject(self):
        for key,val in (("origin","real"),("engine_access",True),("publication","OPEN"),("Odds",2)):
            d=fixture();d[key]=val
            with self.assertRaises(ValueError):run(d)
    def test_nested_lock(self):
        d=fixture();d["observations"][0]["engine_access"]=True
        with self.assertRaises(ValueError):run(d)
    def test_leakage(self):
        d=fixture();d["observations"][0]["captured_at"]="2099-01-01T00:00:00Z"
        with self.assertRaises(ValueError):run(d)
