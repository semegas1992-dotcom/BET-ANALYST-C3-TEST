import unittest
from copy import deepcopy
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_report import render
class PositiveFixturesTests(unittest.TestCase):
    def replay(self,d,e,r,essential,x):
        return run(d,e,r,essential,[1],"fictional fixture",{},1,1,{},[],x)
    def test_positive(self):
        for sport in ("football","nba","tennis"):
            with self.subTest(sport=sport):
                d,e,r,essential,x=dossier(sport)
                result=self.replay(d,e,r,essential,x)
                self.assertTrue(result["documentary_gate"])
                self.assertEqual(result["stages"]["context_analysis"]["issues"],[])
                self.assertGreater(result["stages"]["context_analysis"]["audit_checks"],0)
                self.assertEqual(len(render(result)["sections"]),7)
                self.assertFalse(result["engine_access"])
    def test_counterexamples(self):
        for sport in ("football","nba","tennis"):
            d,e,r,essential,x=dossier(sport)
            x["configurations"][0]["availability"]="uncertain"
            result=self.replay(d,e,r,essential,x)
            self.assertIn("CONFIGURATION_UNRESOLVED",result["stages"]["context_analysis"]["issues"])
            self.assertTrue(all(s["status"]=="BLOCKED" for s in result["stages"]["context_analysis"]["sequences"]))
            x["indicators"].append(deepcopy(x["indicators"][0]))
            with self.assertRaises(ValueError):self.replay(d,e,r,essential,x)
