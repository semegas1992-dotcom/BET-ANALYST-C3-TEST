import unittest
from c4_integrated import run
from d0_contract import digest
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
class IntegratedTests(unittest.TestCase):
    def case(self,d):
        event=dict(id="synthetic-event",origin="synthetic",sport=d["sport"],participants=["home","away"] if d["sport"]=="football" else d["participants"],kickoff=d["kickoff"],competition="fixture",category="fixture",venue="fixture",format="fixture",status="scheduled")
        return event
    def test_multisport(self):
        for d in (fixture(),fixture_other("nba"),fixture_other("tennis")):
            r=run(d,self.case(d),[],["identity"],[1,2],"fixture",{},1,1,{},[])
            self.assertEqual(set(r["stages"]),{"E1","E2","E3","E4","E5"})
            self.assertFalse(r["documentary_gate"])
            self.assertFalse(r["sporting_analysis_complete"])
            self.assertTrue(all(a["passed"] for a in r["audits"]))
            self.assertEqual(r["stage_sha256"],{k:digest(v) for k,v in r["stages"].items()})
    def test_comparison(self):
        d=fixture();c=dict(input_sha256=digest(d),sport="football",participant="home",metric="shots_for",period="historical_observation",unit="shots")
        r=run(d,self.case(d),[],["identity"],[1,2],"fixture",{},1,1,{},[dict(contract=c,thresholds=[9,10,11])])
        self.assertEqual(r["stages"]["E5"]["comparisons"][0]["envelope_report_sha256"],r["stage_sha256"]["E4"])
    def test_identity(self):
        d=fixture();e=self.case(d);e["participants"].reverse()
        with self.assertRaises(ValueError):run(d,e,[],["identity"],[1],"fixture",{},1,1,{},[])
