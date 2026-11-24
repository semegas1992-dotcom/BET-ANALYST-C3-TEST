import unittest
from unittest.mock import patch
from datetime import timedelta
from nba_history import stamp,periods
from nba_batch import select,build

NOW=stamp("2026-11-24T12:00:00Z")
def event(i=1,h=1,a=2,tip="2026-11-25T01:00:00Z",status="Scheduled"):
    return {"id":i,"datetime":tip,"status":status,"season":2026,"home_team":{"id":h,"full_name":str(h)},"visitor_team":{"id":a,"full_name":str(a)}}
def report():
    return {"histories":{},"dossiers":[],"skipped":[],"request_errors":[]}
class BatchTests(unittest.TestCase):
    def test_window(self):
        games,issues=select([event(),event(2,tip="2026-11-24T11:00:00Z"),event(3,status="Final"),event(4,tip="2026-11-26T01:00:00Z")],NOW,NOW+timedelta(hours=24))
        self.assertEqual([g["id"] for g in games],[1])
        self.assertFalse(issues)
    def test_duplicate(self):
        games,issues=select([event(),event()],NOW,NOW+timedelta(days=1))
        self.assertEqual((len(games),len(issues)),(1,1))
    @patch("nba_batch.collect",return_value=[])
    def test_cache(self,collect):
        games,_=select([event(),event(2,1,3)],NOW,NOW+timedelta(days=1))
        r=report();build(games,NOW,"test",r,lambda:NOW)
        self.assertEqual(collect.call_count,3)
        self.assertEqual(len(r["dossiers"]),2)
        self.assertTrue(all(d["status"]=="INCOMPLETE" for d in r["dossiers"]))
    @patch("nba_batch.collect",side_effect=ValueError("failure"))
    def test_partial(self,collect):
        games,_=select([event()],NOW,NOW+timedelta(days=1))
        r=report();build(games,NOW,"test",r,lambda:NOW)
        self.assertEqual(r["dossiers"][0]["status"],"INCOMPLETE")
    @patch("nba_batch.collect")
    def test_expired(self,collect):
        games,_=select([event()],NOW,NOW+timedelta(days=1))
        r=report();build(games,NOW,"test",r,lambda:NOW+timedelta(days=1))
        collect.assert_not_called()
        self.assertEqual(len(r["skipped"]),1)
    def test_hidden_overtime(self):
        g={"period":4,"home_team_score":110,"visitor_team_score":105,"home_ot1":10,"visitor_ot1":5}
        for i in range(1,5):g[f"home_q{i}"]=g[f"visitor_q{i}"]=25
        self.assertEqual(periods(g,True)["overtime_count"],1)
    def test_missing_overtime(self):
        g={"period":4,"home_team_score":110,"visitor_team_score":105,"home_ot1":10}
        for i in range(1,5):g[f"home_q{i}"]=g[f"visitor_q{i}"]=25
        self.assertEqual(periods(g,True)["status"],"MISSING")
