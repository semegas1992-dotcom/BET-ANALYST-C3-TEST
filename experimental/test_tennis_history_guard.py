import unittest
from tennis_history_guard import validate
class TennisGuardTests(unittest.TestCase):
    def setUp(self):
        self.row=dict(tour="ATP",surface="hard",best_of=3,player_id=1,opponent_id=2,ended_at="2026-01-01T10:00:00Z",available_at="2026-01-01T11:00:00Z",status="completed")
        self.cutoff="2026-01-02T00:00:00Z"
    def test_valid(self):
        self.assertTrue(validate(self.row,self.cutoff))
    def test_rejections(self):
        for key,value in [("tour","unknown"),("surface","unknown"),("best_of",2),("opponent_id",1),("status","retired"),("available_at","2026-01-03T00:00:00Z")]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(dict(self.row,**{key:value}),self.cutoff)
