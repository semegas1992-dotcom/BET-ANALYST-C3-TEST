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
    def test_chronology(self):
        self.rows[1]["datetime"]="2026-01-02T12:00:00Z"
        self.assertIn("chronology",audit_history(self.h,self.cutoff)["issues"])
    def test_period_score(self):
        self.rows[0]["periods"]["pf"][0]=26
        self.assertIn("period_score:0",audit_history(self.h,self.cutoff)["issues"])
    def test_empty_history(self):
        self.h["games"]=[]
        self.assertIn("empty_history",audit_history(self.h,self.cutoff)["issues"])
    def test_dossier_identity_and_digest(self):
        import hashlib,json
        e={"season":2025,"home_id":1,"away_id":2,"tipoff":"2026-01-04T12:00:00Z"}
        d={"event":e,"history_refs":["2025:1","2025:2"],"engine_access":False}
        b={"cutoff":self.cutoff,"engine_access":False,"publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","histories":{"2025:1":self.h,"2025:2":self.h},"dossiers":[d]}
        r=audit_batch(b)
        self.assertEqual(r["status"],"PASS")
        item=r["dossiers"][0];digest=item.pop("sha256")
        self.assertEqual(digest,hashlib.sha256(json.dumps(item,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest())
        d["history_refs"].reverse()
        self.assertIn("dossier history identity",audit_batch(b)["issues"])
        d["history_refs"]=[]
        self.assertIn("dossier history identity",audit_batch(b)["issues"])
