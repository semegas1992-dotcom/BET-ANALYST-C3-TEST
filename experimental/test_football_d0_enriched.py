import unittest
from football_d0_enriched import aggregate,join
from datetime import datetime,timezone
class EnrichedTests(unittest.TestCase):
    def test_empty(self):self.assertIsNone(aggregate([], {})["shots_for"]["mean"])
    def test_missing(self):self.assertEqual(aggregate([{"id":1,"home":True}],{})["shots_for"]["n"],0)
    def test_zero(self):self.assertEqual(aggregate([{"id":1,"home":True}],{1:{"home_shots":{"status":"INTERNAL_ONLY","value":0}}})["shots_for"]["mean"],0)
    def test_quarantine(self):self.assertEqual(aggregate([{"id":1,"home":True}],{1:{"home_shots":{"status":"QUARANTINED_CONFLICT","value":2}}})["shots_for"]["n"],0)
    def test_empty_join(self):self.assertEqual(join([],[],datetime.now(timezone.utc)),({}, {}, []))
