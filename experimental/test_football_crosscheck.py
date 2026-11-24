import unittest
from football_crosscheck import compare
P={"utcDate":"2025-08-01T20:00:00Z","homeTeam":{"name":"A"},"awayTeam":{"name":"B"},"score":{"fullTime":{"home":2,"away":1}}}
S={"date":"2025-08-01","team1":"A","team2":"B","score":{"ft":[2,1]}}
class CrosscheckTests(unittest.TestCase):
    def test_match(self):self.assertEqual(compare([P],[S])["matched"],1)
    def test_conflict(self):self.assertEqual(compare([P],[dict(S,score={"ft":[0,1]})])["conflicting"],1)
    def test_missing(self):self.assertEqual(compare([P],[])["unmatched"],1)
    def test_ambiguous(self):self.assertEqual(compare([P],[S,S])["ambiguous"],1)
