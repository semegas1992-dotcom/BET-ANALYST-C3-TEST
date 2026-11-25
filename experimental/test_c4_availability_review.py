import unittest
from c4_availability_review import review
class TestAvailability(unittest.TestCase):
    def test_roles(self):
        for sport,role in (("football","creator"),("nba","handler"),("tennis","server")):
            a=dict(participant="A",person_id="p",role=role,availability="absent",record_ids=["r"])
            b=dict(a,person_id="q",availability="available")
            historical={"mean":5}
            result=review(sport,[a,b],historical)
            self.assertEqual(historical,{"mean":5})
            row=result["dependencies"][0]
            self.assertEqual(row["replacement_candidates"],["q"])
            self.assertIsNone(row["effect"])
            self.assertIn("handicap",row["families_to_review"])
            self.assertEqual(review(sport,[b],historical)["dependencies"],[])
