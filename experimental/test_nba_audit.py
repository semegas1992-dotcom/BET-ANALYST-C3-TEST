import unittest
from unittest.mock import patch
from datetime import timedelta
from nba_batch import select,discover,audit
from nba_history import collect,stamp
from test_nba_batch import NOW,event

class AuditTests(unittest.TestCase):
    def test_postponed(self):
        g=event();g["postponed"]=True
        self.assertEqual(select([g],NOW,NOW+timedelta(days=1)),([],[]))
    @patch("nba_history.time.sleep")
    @patch("nba_history.request_json")
    def test_partial_history(self,request,sleep):
        request.side_effect=[{"data":[{"id":1}],"meta":{"next_cursor":2}},ValueError("failure")]
        partial=[];trace=[]
        with self.assertRaises(ValueError):collect(1,2026,NOW,"test",trace,[],partial)
        self.assertEqual(partial,[{"id":1}])
        self.assertEqual(len(trace),1)
    @patch("nba_batch.time.sleep")
    @patch("nba_batch.request_json")
    def test_calendar_trace(self,request,sleep):
        request.return_value={"data":[event()],"meta":{}}
        trace=[]
        self.assertEqual(len(discover(NOW,NOW+timedelta(days=1),"test",[],trace)),1)
        self.assertEqual(len(trace[0]["sha256"]),64)
    def base(self):
        return {"cutoff":NOW.isoformat(),"histories":{},"dossiers":[],"skipped":[],"engine_access":False,"selected_count":0,"calendar_pages":[{"count":0,"next_cursor":None}],"calendar_received":0}
    def test_audit_pass(self):
        self.assertEqual(audit(self.base())["status"],"PASS")
    def test_audit_count(self):
        r=self.base();r["selected_count"]=1
        self.assertIn("event accounting",audit(r)["issues"])
    def test_audit_reference(self):
        r=self.base();r["selected_count"]=1
        r["dossiers"]=[{"event":{"id":1,"season":2026,"home_id":1,"away_id":2},"history_refs":["2026:1","2026:2"],"engine_access":False}]
        self.assertIn("invalid history reference",audit(r)["issues"])
    def test_audit_lock(self):
        r=self.base();r["engine_access"]=True
        self.assertIn("engine access",audit(r)["issues"])
