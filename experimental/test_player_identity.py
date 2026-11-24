import unittest
from player_identity import identity,qualify
B={"id":1,"name":"Example Player","birth_date":"2000-01-01","team_id":8}
D={"id":"x","name":"Example Player","birth_date":"2000-01-01","team_id":"den"}
class IdentityTests(unittest.TestCase):
    def test_match(self):self.assertEqual(identity(B,[D],{"8":"den"})["status"],"CANDIDATE_MATCH")
    def test_birth(self):self.assertEqual(identity(B,[dict(D,birth_date="2001-01-01")],{"8":"den"})["status"],"UNRESOLVED")
    def test_missing(self):self.assertEqual(identity(B,[dict(D,birth_date=None)],{"8":"den"})["status"],"UNRESOLVED")
    def test_team(self):self.assertEqual(identity(B,[D],{"8":"dal"})["status"],"UNRESOLVED")
    def test_duplicate(self):self.assertEqual(identity(B,[D,D],{"8":"den"})["status"],"UNRESOLVED")
    def test_lock(self):self.assertFalse(qualify({},{"status":"UNRESOLVED"},None,None)["engine_access"])
