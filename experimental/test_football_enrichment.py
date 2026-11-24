import unittest
from football_enrichment import distribution,halves,enrich
from football_collect import history
from test_football_collect import H,E,NOW
R=[{"gf":2,"ga":1,"ht_gf":1,"ht_ga":0,"opponent":4},{"gf":0,"ga":0,"ht_gf":None,"ht_ga":None,"opponent":5}]
class EnrichmentTests(unittest.TestCase):
    def test_btts(self):self.assertEqual(distribution(R)["btts"],1)
    def test_totals(self):self.assertEqual(distribution(R)["over_2_5"],1)
    def test_histogram(self):self.assertEqual(distribution(R)["total_histogram"],{"0":1,"3":1})
    def test_halves(self):self.assertEqual(halves(R)["second_half_ga"],1)
    def test_coverage(self):self.assertEqual(halves(R)["coverage"],0.5)
    def test_empty(self):self.assertIsNone(halves([])["coverage"])
    def test_h2h(self):self.assertEqual(len(enrich(R,4)["h2h"]["rows"]),1)
    def test_invalid_half(self):
        h=dict(H,score=dict(H["score"],halfTime={"home":3,"away":0}))
        self.assertIsNone(history([h],E,3,NOW)[0]["ht_gf"])
    def test_away_half(self):
        h=dict(H,score=dict(H["score"],halfTime={"home":1,"away":0}))
        self.assertEqual(history([h],E,4,NOW)[0]["ht_ga"],1)
