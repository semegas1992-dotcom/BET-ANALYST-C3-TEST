import unittest
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_report import render
class SpecificTests(unittest.TestCase):
    def test_scoped(self):
        for sport in ("football","nba","tennis"):
            d,e,r,essential,x=dossier(sport)
            def replay():return run(d,e,r,essential,[1],"fixture",{},1,1,{},[],x)
            result=replay()
            self.assertEqual(len(render(result)["sections"]),7)
            self.assertTrue(all(not m["issues"] for m in result["stages"]["specific_dependencies"]["mechanisms"].values()))
            x["configurations"][0]["availability"]="uncertain"
            ms=replay()["stages"]["specific_dependencies"]["mechanisms"].values()
            self.assertTrue(any(m["issues"] for m in ms))
            self.assertTrue(any(not m["issues"] for m in ms))
            x["indicators"][0]["odds"]=2
            with self.assertRaises(ValueError):replay()
