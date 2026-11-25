import unittest
from c4_matched_opposition import contrast
class TestMatchedOpposition(unittest.TestCase):
    def rows(self,sport):
        return [dict(sport=sport,metric="fictional",context="same",opponent="X",side=s,observation_id=str(i),value=i+(2 if s=="A" else 0)) for s in ("A","B") for i in range(3)]
    def test_multisport(self):
        for sport in ("football","nba","tennis"):
            r=contrast(self.rows(sport))
            self.assertEqual(r["strata"][0]["contrast"],2)
            self.assertIsNone(r["forecast"])
    def test_insufficient(self):
        self.assertIsNone(contrast(self.rows("nba")[:-1])["strata"][0]["contrast"])
    def test_duplicate(self):
        rows=self.rows("tennis")
        with self.assertRaises(ValueError): contrast(rows+[rows[0]])
