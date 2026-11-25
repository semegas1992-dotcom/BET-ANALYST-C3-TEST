import unittest
from c4_context_analysis import summarize,audit
from c4_integrated import run
from test_c4_integrated import IntegratedTests
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
class ContextAnalysisTests(unittest.TestCase):
    def test_integrated_missing(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            e=IntegratedTests().case(d)
            x={k:[] for k in ("observations","configurations","comparables","indicators","sequences")}
            r=run(d,e,[],["identity"],[1],"fixture",{},1,1,{},[],x)
            a=r["stages"]["context_analysis"]
            self.assertIn("DOCUMENTARY_GATE",a["issues"])
            self.assertTrue(all(s["status"]=="BLOCKED" for s in a["sequences"]))
    def test_ratio(self):
        d=fixture_other("nba");e=IntegratedTests().case(d);i=d["observations"][0]["id"]
        x={"indicators":[dict(observation_id=i,metric="points_for",value=100),dict(observation_id=i,metric="possessions",value=80)]}
        s=summarize(d,e,x)
        self.assertEqual(s["A"]["points_per_possession"]["ratio"],1.25)
        self.assertGreater(audit(d,e,x,s),0)
        s["A"]["points_per_possession"]["ratio"]=2
        with self.assertRaises(ValueError):audit(d,e,x,s)
