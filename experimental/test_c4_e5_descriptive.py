import unittest
from c4_e5_descriptive import compare
from d0_contract import digest
from test_d0_pipeline_demo import fixture
class DescriptiveTests(unittest.TestCase):
    def setup_case(self):
        d=fixture();d["observations"][0]["stats"]["shots_for"]=30
        c=dict(input_sha256=digest(d),sport="football",participant="home",metric="shots_for",period="historical_observation",unit="shots")
        return d,c
    def test_thresholds(self):
        d,c=self.setup_case()
        r=compare(d,[1,5],"fixture",{},1,1,{},c,[15,12,10])
        self.assertEqual([x["state"] for x in r["rows"]],["ALL_AT_OR_ABOVE","SENSITIVE","ALL_BELOW"])
    def test_incompatible(self):
        d,c=self.setup_case()
        for k,v in (("unit","goals"),("period","first_half"),("input_sha256","wrong"),("sport","nba")):
            with self.assertRaises(ValueError):compare(d,[1],"fixture",{},1,1,{},dict(c,**{k:v}),[10])
    def test_block(self):
        d,c=self.setup_case()
        r=compare(d,[1,5],"fixture",{},2,1,{},c,[10,12])
        self.assertTrue(all(x["state"]=="BLOCKED" for x in r["rows"]))
    def test_trace(self):
        d,c=self.setup_case()
        r=compare(d,[1,5],"fixture",{},1,1,{},c,[10])
        self.assertEqual(r["contract"]["input_sha256"],digest(d))
        self.assertEqual(len(r["envelope_report_sha256"]),64)
        self.assertFalse(r["engine_access"])
