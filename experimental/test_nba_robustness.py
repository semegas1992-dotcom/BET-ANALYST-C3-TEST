import unittest
from unittest.mock import patch
from datetime import timedelta
from nba_batch import build_grouped,select,verify_pages,reciprocity
from nba_enrichment import grouped,distribute
from nba_history import normalize
from test_nba_batch import NOW,event,report
from test_nba_history import game

class RobustnessTests(unittest.TestCase):
    @patch("nba_batch.grouped",side_effect=ValueError("group failure"))
    @patch("nba_batch.collect")
    def test_fallback(self,collect,group):
        g=game();g["season"]=2026
        collect.return_value=[g]
        events,_=select([event()],NOW,NOW+timedelta(days=1))
        r=report();r["calendar_pages"]=[]
        build_grouped(events,NOW,"test",r,lambda:NOW)
        self.assertEqual(collect.call_count,2)
        self.assertEqual(r["dossiers"][0]["status"],"QUARANTINE_UNVERIFIED")
    def test_reciprocity(self):
        g=game();g["season"]=2026
        h={}
        for t in (1,2):h[f"2026:{t}"]={"status":"COLLECTED","games":normalize([g],t,NOW,[],2026)[0]}
        self.assertEqual(reciprocity(h),[])
        h["2026:2"]["games"][0]["pf"]+=1
        self.assertTrue(reciprocity(h))
    def test_missing_reciprocal(self):
        g=game();g["season"]=2026
        h={"2026:1":{"status":"COLLECTED","games":normalize([g],1,NOW,[],2026)[0]},"2026:2":{"status":"COLLECTED","games":[]}}
        self.assertTrue(reciprocity(h))
    @patch("nba_enrichment.time.sleep")
    @patch("nba_enrichment.request_json")
    def test_page_integrity(self,request,sleep):
        request.return_value={"data":[game()],"meta":{}}
        trace=[]
        grouped({1,2},2026,NOW,"test",trace,[],[])
        self.assertTrue(verify_pages(trace))
        trace[0]["payload"]["data"][0]["id"]=999
        self.assertFalse(verify_pages(trace))
    def test_same_day(self):
        g=game();g["season"]=2026;g["datetime"]=(NOW-timedelta(hours=1)).isoformat()
        excluded=[]
        self.assertEqual(normalize([g],1,NOW,excluded,2026)[0],[])
        self.assertEqual(excluded[0]["reason"],"same_utc_day")
    @patch("nba_enrichment.time.sleep")
    @patch("nba_enrichment.request_json")
    def test_full_league(self,request,sleep):
        raw=[]
        for i in range(450):
            g=game();g["id"]=i+1
            g["home_team"]={"id":i%30+1}
            g["visitor_team"]={"id":(i+1)%30+1}
            raw.append(g)
        request.side_effect=[{"data":raw[i:i+100],"meta":{"next_cursor":i+100 if i+100<len(raw) else None}} for i in range(0,len(raw),100)]
        trace=[]
        rows=grouped(set(range(1,31)),2026,NOW,"test",trace,[],[])
        self.assertEqual(request.call_count,5)
        self.assertEqual(len(rows),450)
        self.assertEqual(sum(map(len,distribute(rows,set(range(1,31))).values())),900)
        self.assertTrue(verify_pages(trace))
    @patch("nba_enrichment.time.sleep")
    @patch("nba_enrichment.request_json")
    def test_cursor_loop(self,request,sleep):
        request.return_value={"data":[],"meta":{"next_cursor":1}}
        with self.assertRaises(ValueError):grouped({1,2},2026,NOW,"test",[],[],[])
