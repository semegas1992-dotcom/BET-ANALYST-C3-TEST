import unittest
from kraft_integration import run
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
class CrossSportTests(unittest.TestCase):
    def test_blank_id(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            d["observations"][0]["id"]=""
            with self.assertRaises(ValueError):run(d)
    def test_football_side(self):
        d=fixture();d["observations"][0]["side"]="unknown"
        with self.assertRaises(ValueError):run(d)
    def test_football_impossible(self):
        d=fixture();d["observations"][0]["stats"]["target_for"]=11
        with self.assertRaises(ValueError):run(d)
    def test_locks_and_trace(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            r=run(d);self.assertFalse(r["engine_access"]);self.assertFalse(r["sporting_analysis_complete"])
            ids={o["id"] for o in d["observations"]}
            for e in r["report"]["evidence"].values():
                self.assertEqual(len(e["observation_ids"]),e["metric"]["n"])
                self.assertTrue(set(e["observation_ids"])<=ids)
    def test_offsets(self):
        d=fixture_other("nba");base=d["observations"][0]
        d["observations"]=[dict(base,id=str(i),event_end="2026-01-01T00:00:00Z") for i in range(5)]
        d["observations"].append(dict(base,id="latelexical",event_end="2026-01-01T01:00:00+02:00"))
        ids=run(d)["report"]["evidence"]["A:last5:points_for"]["observation_ids"]
        self.assertNotIn("latelexical",ids)
