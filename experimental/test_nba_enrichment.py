import unittest
from unittest.mock import patch
from datetime import timedelta
from urllib.parse import urlparse,parse_qs
from nba_enrichment import grouped,distribute,dispersion,context
from nba_batch import build_grouped,select
from test_nba_batch import NOW,event,report
from test_nba_history import game

class EnrichmentTests(unittest.TestCase):
    @patch("nba_enrichment.time.sleep")
    @patch("nba_enrichment.request_json")
    def test_group_query(self,request,sleep):
        request.return_value={"data":[game()],"meta":{}}
        trace=[]
        self.assertEqual(len(grouped({1,2},2026,NOW,"test",trace,[],[])),1)
        self.assertEqual(parse_qs(urlparse(request.call_args.args[0]).query)["team_ids[]"],["1","2"])
    def test_shared_game(self):
        g=game()
        self.assertEqual(distribute([g],{1,2}),{1:[g],2:[g]})
    def test_duplicate(self):
        with self.assertRaises(ValueError):distribute([game(),game()],{1,2})
    def test_unrelated(self):
        with self.assertRaises(ValueError):distribute([game()],{3})
    def test_dispersion(self):
        rows=[{"id":1,"pf":100,"pa":90},{"id":2,"pf":120,"pa":110}]
        d=dispersion(rows)
        self.assertEqual(d["pf"]["median"],110)
        self.assertAlmostEqual(d["pf"]["sample_sd"],14.1421356)
        self.assertIsNone(dispersion(rows[:1])["pf"]["sample_sd"])
    def test_context(self):
        rows=[{"id":1,"pf":100,"pa":90,"datetime":"2026-11-23T12:00:00+00:00","opponent_id":2}]
        c=context(rows,NOW.isoformat(),2)
        self.assertEqual(c["hours_since_last_observed_tipoff"],24)
        self.assertEqual(c["h2h"]["n"],1)
        self.assertEqual(c["rest_status"],"NOT_VERIFIED")
    @patch("nba_batch.grouped")
    def test_batch(self,fetch):
        g=game();g["season"]=2026
        fetch.return_value=[g]
        events,_=select([event()],NOW,NOW+timedelta(days=1))
        r=report();r["calendar_pages"]=[]
        build_grouped(events,NOW,"test",r,lambda:NOW)
        self.assertEqual(fetch.call_count,1)
        self.assertEqual(len(r["histories"]),2)
        self.assertEqual(r["dossiers"][0]["context"]["home"]["h2h"]["n"],1)
    @patch("nba_batch.grouped",side_effect=ValueError("failure"))
    def test_group_failure(self,fetch):
        events,_=select([event()],NOW,NOW+timedelta(days=1))
        r=report();r["calendar_pages"]=[]
        build_grouped(events,NOW,"test",r,lambda:NOW)
        self.assertEqual(r["dossiers"][0]["status"],"INCOMPLETE")
