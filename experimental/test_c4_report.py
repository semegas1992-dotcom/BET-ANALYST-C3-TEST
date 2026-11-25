import unittest
from c4_report import render
from c4_context_analysis import summarize,audit
from c4_integrated import run
from test_c4_integrated import IntegratedTests
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
class ReportTests(unittest.TestCase):
    def test_reports(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            e=IntegratedTests().case(d)
            x={k:[] for k in ("observations","configurations","comparables","indicators","sequences")}
            r=run(d,e,[],["identity"],[1],"fixture",{},1,1,{},[],x)
            self.assertEqual([s["number"] for s in render(r)["sections"]],list(range(1,8)))
            r["stages"]["E1"]["missing_or_unresolved"]=[]
            with self.assertRaises(ValueError):render(r)
    def test_missing_metric(self):
        d=fixture_other("nba");e=IntegratedTests().case(d);x={"indicators":[]}
        s=summarize(d,e,x);del s["A"]["points_per_possession"]
        with self.assertRaises(ValueError):audit(d,e,x,s)
    def test_decimal(self):
        d=fixture();e=IntegratedTests().case(d)
        x={"indicators":[dict(observation_id=o["id"],metric="xg",value=.1 if j%2 else .2) for j,o in enumerate(d["observations"])]}
        self.assertGreater(audit(d,e,x,summarize(d,e,x)),0)
