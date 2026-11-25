import unittest
from tennis_csv_adapter import parse_csv,identity,match_identity
class TennisAdapterTests(unittest.TestCase):
    header="tourney_id,tourney_date,match_num,winner_id,loser_id,surface,best_of,score,w_svpt\n"
    row="2025-1,20250101,1,12,13,Hard,3,6-4 6-4,"
    def parse(self,row=None,tour="ATP"):
        return parse_csv((self.header+(self.row if row is None else row)+"\n").encode(),tour)
    def test_tours(self):
        self.assertNotEqual(identity("ATP",12),identity("WTA",12))
        self.assertEqual(self.parse(tour="WTA")["rows"][0]["winner_id"],"WTA:12")
    def test_temporal_lock(self):
        r=self.parse()["rows"][0];self.assertIsNone(r["ended_at"]);self.assertIsNone(r["available_at"]);self.assertFalse(r["engine_access"])
    def test_missing_stat(self):
        self.assertIsNone(self.parse()["rows"][0]["stats"]["w_svpt"])
    def test_retirement(self):
        self.assertEqual(len(self.parse(self.row.replace("6-4 6-4","6-4 RET"))["rejected"]),1)
    def test_duplicate(self):
        self.assertEqual(len(self.parse(self.row+"\n"+self.row)["rejected"]),1)
    def test_identity_ambiguity(self):
        p=dict(tour="ATP",first_name="A",last_name="B",birth_date="2000-01-01",id=1)
        self.assertEqual(match_identity(p,[p]),1)
        self.assertIsNone(match_identity(p,[p,dict(p,id=2)]))
        self.assertIsNone(match_identity(p,[dict(p,tour="WTA")]))
    def test_bad_schema(self):
        with self.assertRaises(ValueError):parse_csv(b"bad\n1", "ATP")
