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
