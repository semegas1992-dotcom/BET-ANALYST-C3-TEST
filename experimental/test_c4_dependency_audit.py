import unittest
from copy import deepcopy
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_dependency_audit import audit
from c4_specific_dependencies import evaluate
from c4_e3_competing import generate
from c4_e1_quality import assess
from c4_report import render
class DependencyAuditTests(unittest.TestCase):
    def test_replay(self):
        for sport in ("football","nba","tennis"):
            d,e,r,essential,x=dossier(sport)
            result=run(d,e,r,essential,[1],"fixture",{},1,1,{},[],x)
            self.assertTrue(result["stages"]["dependency_audit"]["passed"])
            self.assertEqual(render(result)["stage_sha256"],result["stage_sha256"])
            h=generate(d,1,"fixture",{},1,1,{})
            doc=assess(e,d["cutoff"],r,essential)
            dep=evaluate(d,e,x,doc,h)
            dep["sequences"][0]["issues"]=["FAKE"]
            with self.assertRaises(ValueError):audit(d,e,x,doc,h,dep)
