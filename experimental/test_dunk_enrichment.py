import unittest
from datetime import datetime,timezone
from dunk_enrichment import team_mapping,player_summary,injury_shape,attach
NOW=datetime(2026,11,24,tzinfo=timezone.utc)
def profile():
    return {"player":{"player_id":"a"},"recent_games":[{"game_id":"1","date":"2026-11-23","season":2027,"pts":20,"reb":5,"ast":4,"minutes":30}]}
class Enrichment(unittest.TestCase):
    def test_mapping(self):
        self.assertEqual(team_mapping([{"id":8,"full_name":"Denver Nuggets"}],[{"team_id":"7","name":"Denver Nuggets"}])["8"]["dunk_id"],"7")
    def test_ambiguous(self):
        t={"team_id":"7","name":"Denver Nuggets"}
        self.assertEqual(team_mapping([{"id":8,"full_name":"Denver Nuggets"}],[t,t]),{})
    def test_profile(self):
        self.assertEqual(player_summary(profile(),"a",NOW,2027)["means"]["pts"],20)
    def test_identity(self):
        with self.assertRaises(ValueError):player_summary(profile(),"b",NOW,2027)
    def test_cutoff(self):
        p=profile();p["recent_games"][0]["date"]="2026-11-24"
        self.assertEqual(player_summary(p,"a",NOW,2027)["n"],0)
    def test_duplicate(self):
        p=profile();p["recent_games"]*=2
        with self.assertRaises(ValueError):player_summary(p,"a",NOW,2027)
    def test_shape(self):
        self.assertEqual(injury_shape({"injuries":[{"status":"Out"}],"count":1})["fields"],["status"])
    def test_lock(self):
        with self.assertRaises(ValueError):attach({"engine_access":True},{},{},{})
    def test_attach(self):
        self.assertFalse(attach({"engine_access":False},{},{},{})["dunkapi"]["engine_access"])
