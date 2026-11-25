import unittest
from kraft_report import build_report,STATUSES
from test_d0_pipeline_demo import fixture
class ReportTests(unittest.TestCase):
    def test_sections(self):
        r=build_report(fixture());self.assertEqual(len(r["sections"]),7)
        self.assertEqual(r["sections"][-1]["decision"],"ABSTENTION")
        self.assertFalse(r["engine_access"])
    def test_trace(self):
        d=fixture();r=build_report(d);ids={o["id"] for o in d["observations"]}
        self.assertEqual(len(r["evidence"]),16)
        for e in r["evidence"].values():
            self.assertIn(e["status"],STATUSES)
            self.assertEqual(len(e["observation_ids"]),e["metric"]["n"])
            self.assertTrue(set(e["observation_ids"])<=ids)
        for s in r["sections"]:self.assertTrue(set(s["evidence_ids"])<=r["evidence"].keys())
    def test_replay(self):
        self.assertEqual(build_report(fixture()),build_report(fixture()))
    def test_reject(self):
        d=fixture();d["observations"][0]["stats"]["shots_for"]=None
        r=build_report(d);self.assertFalse(r["sections"][0]["p2_pass"]);self.assertTrue(r["p2_rejections"])
    def test_quarantine(self):
        d=fixture();d["origin"]="real"
        with self.assertRaises(ValueError):build_report(d)
