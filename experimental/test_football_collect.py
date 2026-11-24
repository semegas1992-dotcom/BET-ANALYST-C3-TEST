import unittest
from datetime import timedelta
from football_collect import stamp,upcoming,history,stats,matches
NOW=stamp("2026-11-24T15:00:00Z")
E={"id":1,"utcDate":"2026-11-25T20:00:00Z","status":"TIMED","competition":{"id":1,"code":"PL"},"season":{"id":2},"homeTeam":{"id":3},"awayTeam":{"id":4}}
H=dict(E,id=2,utcDate="2026-11-22T20:00:00Z",lastUpdated="2026-11-23T00:00:00Z",status="FINISHED",score={"duration":"REGULAR","fullTime":{"home":2,"away":1}})
class FootballTests(unittest.TestCase):
    def test_calendar(self):self.assertEqual(upcoming([E],NOW,NOW+timedelta(days=3)),[E])
    def test_postponed(self):self.assertEqual(upcoming([dict(E,status="POSTPONED")],NOW,NOW+timedelta(days=3)),[])
    def test_history(self):self.assertEqual(history([H],E,3,NOW)[0]["gf"],2)
    def test_away(self):self.assertEqual(history([H],E,4,NOW)[0]["gf"],1)
    def test_future(self):self.assertEqual(history([dict(H,utcDate=E["utcDate"])],E,3,NOW),[])
    def test_updated(self):self.assertEqual(history([dict(H,lastUpdated=E["utcDate"])],E,3,NOW),[])
    def test_empty(self):self.assertIsNone(stats([])["gf_mean"])
    def test_accounting(self):self.assertEqual(stats(history([H],E,3,NOW))["wins"],1)
    def test_duplicate(self):
        with self.assertRaises(ValueError):matches({"matches":[H,H],"resultSet":{"count":2}})
    def test_count(self):
        with self.assertRaises(ValueError):matches({"matches":[H],"resultSet":{"count":2}})

    def test_audit(self):
        from football_collect import audit
        h=history([H],E,3,NOW)
        s={"history":h,"season":stats(h),"last5":stats(h),"last10":stats(h),"home":stats(h),"away":stats([])}
        from football_enrichment import enrich
        s["enrichment"]=enrich(h,4)
        a=dict(s,enrichment=enrich(h,3))
        d={"id":1,"kickoff":E["utcDate"],"engine_access":False,"teams":[3,4],"stats":{"home":s,"away":a}}
        self.assertEqual(audit({"dossiers":[d]})["status"],"PASS")
        self.assertEqual(audit({"dossiers":[dict(d,stats={"home":s})]})["status"],"FAIL")
        self.assertEqual(audit({"dossiers":[dict(d,stats={"home":dict(s,enrichment=None),"away":a})]})["status"],"FAIL")
        s["last5"]=stats([])
        self.assertEqual(audit({"dossiers":[d]})["status"],"FAIL")
    def test_empty_audit(self):
        from football_collect import audit
        self.assertEqual(audit({"dossiers":[]})["status"],"FAIL")
    def test_same_day(self):self.assertEqual(history([dict(H,utcDate="2026-11-24T10:00:00Z")],E,3,NOW),[])

    def test_previous_season(self):
        old=dict(H,season={"id":9},utcDate="2025-11-22T20:00:00Z")
        self.assertEqual(history([old],E,3,NOW),[])
        self.assertEqual(len(history([old],E,3,NOW,multi=True)),1)
