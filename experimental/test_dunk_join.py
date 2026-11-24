import unittest
from dunk_join import mapping,injury_counts,assemble,audit_join
B=[{"id":8,"full_name":"Denver Nuggets","abbreviation":"DEN"}]
D=[{"team_id":"x","name":"Nuggets","display_name":"Denver Nuggets","abbrev":"DEN"}]
class JoinTests(unittest.TestCase):
    def test_full(self):self.assertEqual(mapping(B,D)["8"]["team_id"],"x")
    def test_conflict(self):self.assertEqual(mapping(B,[dict(D[0],abbrev="DAL")]),{})
    def test_duplicate(self):self.assertEqual(mapping(B,D+D),{})
    def test_injury(self):
        c,u=injury_counts([{"team":"DEN","status":"Out"},{"team":"unknown"}],mapping(B,D))
        self.assertEqual((c["8"]["Out"],u),(1,1))
    def test_lock(self):
        with self.assertRaises(ValueError):assemble({"engine_access":True},{},{},0,"2026-11-24T12:00:00Z","2026-11-24")
    def test_incomplete(self):
        self.assertEqual(audit_join({"dossiers":[]},[],{}, {},0,0)["status"],"FAIL")
    def test_expired(self):
        r={"engine_access":False,"dossiers":[{"event":{"tipoff":"2026-11-24T11:00:00Z"}}]}
        self.assertEqual(assemble(r,{},{},0,"2026-11-24T12:00:00Z","2026-11-24"),[])
