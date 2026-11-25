import unittest
from c4_matched_opposition import contrast
class MultiMetricTests(unittest.TestCase):
    def rows(self,sport):
        return [dict(sport=sport,metric=m,context='same',opponent='X',side=s,observation_id=str(i),value=i+(delta if s=='A' else 0)) for m,delta in [('m1',2),('m2',5)] for s in ('A','B') for i in range(3)]
    def test_distinct_metrics(self):
        for sport in ('football','nba','tennis'):
            with self.subTest(sport=sport):
                r=contrast(self.rows(sport))
                self.assertEqual([x['contrast'] for x in r['strata']],[2,5])
                self.assertIsNone(r['forecast'])
    def test_duplicate_relabelled_context(self):
        rows=self.rows('football')
        with self.assertRaises(ValueError): contrast(rows+[{**rows[0],'context':'different'}])
