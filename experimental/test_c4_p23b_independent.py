import json
import unittest
from pathlib import Path
from test_d0_pipeline_demo import fixture
from test_kraft_synthetic_adapters import fixture_other
from d0_contract import digest
from c4_e5_descriptive import compare

class P23BIndependentTests(unittest.TestCase):
    def test_frozen_expectations(self):
        oracle=json.loads(Path(__file__).with_name("p23b_expected.json").read_text())
        for sport, case in oracle.items():
            with self.subTest(sport=sport):
                d=fixture() if sport=="football" else fixture_other(sport)
                c=dict(input_sha256=digest(d),sport=sport,participant=case["participant"],metric=case["metric"],unit=case["unit"],period="historical_observation")
                r=compare(d,[1],"fixture",{},1,1,{},c,case["thresholds"])
                actual=[x["state"] for x in r["rows"]]
                print("P23B",sport,"expected",case["expected"],"actual",actual,"digest",digest(d),flush=True)
                self.assertEqual(actual,case["expected"])
                self.assertFalse(r["engine_access"])
                self.assertEqual(r["qualification"],"BLOCKED")
                self.assertEqual(r["publication"],"BLOCKED")
