import unittest,copy
from nba_history import summarize
from nba_independent_audit import audit_history,audit_batch
class IndependentTests(unittest.TestCase):
    def setUp(self):
        self.rows=[{"id":i,"datetime":"2026-01-01T12:00:00Z","home":True,"pf":100,"pa":96,"periods":{"status":"CONSISTENT","pf":[25]*4,"pa":[24]*4}} for i in range(5)]
        self.h={"status":"COLLECTED","games":self.rows,"stats":summarize(self.rows)}
        self.cutoff="2026-01-03T12:00:00Z"
    def test_clean(self):
        r=audit_history(self.h,self.cutoff);self.assertEqual(r["issues"],[]);self.assertEqual(r["checks"],150)
    def test_tamper(self):
        self.h["stats"]["L5"]["pf"]=99
        self.assertIn("L5:pf",audit_history(self.h,self.cutoff)["issues"])
    def test_cutoff(self):
        self.rows[0]["datetime"]=self.cutoff
        self.assertIn("cutoff",audit_history(self.h,self.cutoff)["issues"])
    def test_duplicate(self):
        self.rows[1]["id"]=self.rows[0]["id"]
        self.assertIn("duplicate",audit_history(self.h,self.cutoff)["issues"])
    def test_coverage(self):
        self.rows[0]["periods"]={"status":"MISSING"}
        self.h["stats"]=summarize(self.rows)
        self.assertFalse(audit_history(self.h,self.cutoff)["coverage"]["L5"]["experimental_sample_gate"])
    def test_lock(self):
        r=audit_batch({"cutoff":self.cutoff,"engine_access":True,"publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","histories":{},"dossiers":[]})
        self.assertEqual(r["status"],"FAIL")
