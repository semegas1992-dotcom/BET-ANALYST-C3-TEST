import unittest
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_quick_summary import build
class QuickSummaryTests(unittest.TestCase):
    def test_summary(self):
        for sport in ("football","nba","tennis"):
            d,e,r,essential,x=dossier(sport)
            result=run(d,e,r,essential,[1],"fixture",{},1,1,{},[],x)
            q=build(result)
            self.assertIsNone(q["dominant_trajectory"])
            self.assertEqual(q["decision"],"NOT_ESTABLISHED")
            self.assertFalse(q["engine_access"])
            result["stages"]["E5"]["market_scopes"].append({})
            with self.assertRaises(ValueError):build(result)
