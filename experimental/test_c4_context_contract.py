import unittest
from c4_context_contract import build
from test_d0_pipeline_demo import fixture
from test_c4_integrated import IntegratedTests
from c4_e3_competing import generate
class ContextTests(unittest.TestCase):
    def setup_case(self):
        d=fixture();e=IntegratedTests().case(d);h=generate(d,1,"fixture",{},1,1,{})
        x={k:[] for k in ("observations","configurations","comparables","indicators","sequences")}
        return d,e,h,x
    def test_empty(self):
        d,e,h,x=self.setup_case();r=build(d,e,[],x,h)
        self.assertEqual(len(r["unlinked_observations"]),len(d["observations"]))
    def test_sequence(self):
        d,e,h,x=self.setup_case();x["sequences"]=[dict(scenario_id=h["scenarios"][0]["id"],phase="opening",starting_state="fixture",expected_behavior="hypothesis",opponent_response="possible",turning_point="conditional",uncertainty="unknown")]
        r=build(d,e,[],x,h);self.assertEqual(r["sequences"][0]["status"],"UNVERIFIED_HYPOTHESIS")
        x["sequences"][0]["phase"]="quarter"
        with self.assertRaises(ValueError):build(d,e,[],x,h)
    def test_unlinked_indicator(self):
        d,e,h,x=self.setup_case();x["indicators"]=[dict(observation_id="unknown",metric="xg",unit="expected_goals",value=1)]
        with self.assertRaises(ValueError):build(d,e,[],x,h)
    def test_unknown_evidence(self):
        d,e,h,x=self.setup_case();o=d["observations"][0];x["observations"]=[dict(observation_id=o["id"],participant=o["side"],historical_event_id="h",record_ids=["unknown"])]
        with self.assertRaises(ValueError):build(d,e,[],x,h)
