import unittest
from nba_identity_guard import match_teams,match_player
class IdentityTests(unittest.TestCase):
    def test_alias(self):
        self.assertEqual(match_teams([{"id":1,"abbreviation":"NYK"}],[{"id":9,"abbreviation":"NY"}])["mapping"],{"1":"9"})
    def test_ambiguity(self):
        self.assertTrue(match_teams([{"id":1,"abbreviation":"NYK"}],[{"id":9,"abbreviation":"NY"},{"id":8,"abbreviation":"NYK"}])["issues"])
    def test_player_missing_birth(self):
        self.assertIsNone(match_player({"first_name":"A","last_name":"B"},[]))
    def test_player_exact(self):
        p={"first_name":"A","last_name":"B","birth_date":"2000-01-01"}
        self.assertEqual(match_player(p,[dict(p,id=1)]),1)
    def test_player_duplicate(self):
        p={"first_name":"A","last_name":"B","birth_date":"2000-01-01"}
        self.assertIsNone(match_player(p,[dict(p,id=1),dict(p,id=2)]))
