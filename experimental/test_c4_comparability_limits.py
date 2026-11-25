import unittest
from test_c4_linked_opposition import LinkedOppositionTests
from c4_matched_opposition import linked_contrast

class ComparabilityLimitsTests(unittest.TestCase):
    def test_unverified_context(self):
        for sport in ("football","nba","tennis"):
            with self.subTest(sport=sport):
                out=linked_contrast(*LinkedOppositionTests().fixture(sport))
                c=out["comparability"]
                self.assertEqual(c["status"],"NOT_ESTABLISHED")
                self.assertIsNone(c["sporting_estimate"])
                self.assertEqual(len(c["observations"]),6)
                for row in c["observations"]:
                    self.assertIn("OPPONENT_IDENTITY_UNVERIFIED",row["issues"])
                    self.assertIn("HISTORICAL_FORMAT_UNVERIFIED",row["issues"])
                    self.assertIn("REPRESENTATIVENESS_UNESTABLISHED",row["issues"])
                self.assertEqual(out["qualification"],"BLOCKED")
