import unittest
from tennis_independent_audit import audit
from tennis_stat_qualification import qualify
class TennisAuditTests(unittest.TestCase):
    def fixture(self):
        return {"id":"1","score":"6-4 6-4","best_of":3,"stats":{p+"_"+k:v for p in ("w","l") for k,v in zip(("svpt","1stIn","1stWon","2ndWon","ace","df","bpSaved","bpFaced"),(60,40,30,10,5,3,2,5))}}
    def test_audit(self):
        self.assertEqual(audit([self.fixture()],qualify)["checks"],8)
        self.assertEqual(audit([self.fixture()],qualify)["status"],"PASS")
    def test_tamper(self):
        def bad(r):
            q=qualify(r);q["return"]["w"]["won"]+=1;return q
        self.assertEqual(audit([self.fixture()],bad)["status"],"FAIL")
    def test_empty(self):
        self.assertEqual(audit([],qualify)["status"],"FAIL")
