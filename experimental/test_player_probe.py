import unittest
from player_probe import candidate
B={"first_name":"Jayson","last_name":"Tatum","team":{"id":2},"jersey_number":"0"}
P={"name":"Jayson Tatum","team_id":"bos","jersey_number":"0"}
M={"2":{"team_id":"bos"}}
class ProbeTests(unittest.TestCase):
    def test_jersey(self):self.assertTrue(candidate(B,P,M))
    def test_missing(self):self.assertFalse(candidate(B,dict(P,jersey_number=None),M))
    def test_conflict(self):self.assertFalse(candidate(B,dict(P,jersey_number="1"),M))
    def test_team(self):self.assertFalse(candidate(B,dict(P,team_id="dal"),M))
    def test_birth_conflict(self):self.assertFalse(candidate(dict(B,birth_date="1998-03-03"),dict(P,birth_date="1998-03-04"),M))

    def test_real_alias_zero(self):self.assertTrue(candidate(B,{"name":"Jayson Tatum","team_id":"bos","jersey":0},M))
    def test_alias_conflict(self):
        with self.assertRaises(ValueError):candidate(B,dict(P,jersey=1),M)
    def test_boolean_invalid(self):self.assertFalse(candidate(B,dict(P,jersey_number=False),M))
    def test_double_zero_distinct(self):self.assertFalse(candidate(B,dict(P,jersey_number="00"),M))
    def test_blank(self):self.assertFalse(candidate(B,dict(P,jersey_number=" "),M))
