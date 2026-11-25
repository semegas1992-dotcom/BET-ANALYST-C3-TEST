import unittest
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_dependency_audit import audit
from c4_specific_dependencies import evaluate
from c4_e1_quality import assess
from c4_e3_competing import generate
class DependencyAuditTests(unittest.TestCase):
    def test_replay(self):
        for sport in ("football","nba","tennis"):
            d,e,r,essential,x=dossier(sport)
            doc=assess(e,d["cutoff"],r,essential)
            h=generate(d,1,"fixture",{},1,1,{})
            a=evaluate(d,e,x,doc,h)
            self.assertTrue(audit(d,e,x,doc,h,a)["passed"])
            a["sequences"].pop()
            with self.assertRaises(ValueError):audit(d,e,x,doc,h,a)
            result=run(d,e,r,essential,[1],"fixture",{},1,1,{},[],x)
            self.assertTrue(all(a["passed"] for a in result["audits"]))
