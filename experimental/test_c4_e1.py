import unittest
from c4_e1 import plan
def fixture():
    e={"id":"synthetic-1","origin":"synthetic","sport":"nba","participants":["A","B"],"competition":"fixture","category":"fixture","venue":"fixture","format":"fixture","status":"scheduled","kickoff":"2026-01-03T00:00:00Z"}
    c="2026-01-02T00:00:00Z"
    r={"id":"r1","topic":"identity","event_id":e["id"],"source":"synthetic_fixture","available_at":"2026-01-01T00:00:00Z","captured_at":c,"status":"Contrôlée","opened":True,"scope_checked":True,"coherence_checked":True,"excerpt":"synthetic content"}
    return e,c,r
class E1Tests(unittest.TestCase):
    def test_lots(self):
        e,c,r=fixture();o=plan(e,c,[r]);self.assertEqual(set(o["lots"]),{"A","B","C"});self.assertEqual(o["lots"]["B"]["production"][0]["status"],"Non recherchée");self.assertFalse(o["official_identity_verified"])
    def test_unopened(self):
        e,c,r=fixture();r["opened"]=False
        with self.assertRaises(ValueError):plan(e,c,[r])
    def test_scope(self):
        e,c,r=fixture();r["event_id"]="other"
        with self.assertRaises(ValueError):plan(e,c,[r])
    def test_cutoff(self):
        e,c,r=fixture();r["captured_at"]=e["kickoff"]
        with self.assertRaises(ValueError):plan(e,c,[r])
    def test_real(self):
        e,c,r=fixture();e["origin"]="real"
        with self.assertRaises(ValueError):plan(e,c,[r])
    def test_duplicate(self):
        e,c,r=fixture()
        with self.assertRaises(ValueError):plan(e,c,[r,r])
