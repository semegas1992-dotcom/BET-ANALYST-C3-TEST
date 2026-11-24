import unittest
from football_qualification_v5 import rejection_reasons,select_diverse,diversity_audit

class QualificationV5Tests(unittest.TestCase):
    def sides(self,n=5,e=5):
        return {s:{**{p:{f:{"n":n,"eligible":e} for f in ("shots_for","shots_against","target_for","target_against")} for p in ("advanced_season","advanced_last5")},"independent_check":{"checks":32,"issues":[]}} for s in ("home","away")}
    def test_complete(self):
        self.assertEqual(rejection_reasons(self.sides()),[])
    def test_low_count(self):
        self.assertEqual(len(rejection_reasons(self.sides(4,5))),16)
    def test_low_coverage(self):
        self.assertTrue(rejection_reasons(self.sides(5,7)))
    def test_boundary(self):
        self.assertFalse(rejection_reasons(self.sides(8,10)))
    def test_invalid(self):
        self.assertTrue(rejection_reasons(self.sides(6,5)))
    def test_missing_field(self):
        s=self.sides();del s["home"]["advanced_last5"]["target_for"]
        self.assertTrue(rejection_reasons(s))
    def test_audit_failure(self):
        s=self.sides();s["home"]["independent_check"]["issues"]=["bad"]
        self.assertIn("home:observation_audit",rejection_reasons(s))
    def test_diversity(self):
        c=[{"id":i,"competition":"A" if i<12 else "B","kickoff":f"{i:02}"} for i in range(14)]
        selected=select_diverse(c)
        self.assertEqual(sum(d["competition"]=="B" for d in selected),2)
        self.assertTrue(diversity_audit(c,selected)["pass"])
        self.assertFalse(diversity_audit(c,c[:10])["pass"])
    def test_empty(self):
        self.assertTrue(diversity_audit([],[])["pass"])
    def test_deterministic(self):
        c=[{"id":i,"competition":str(i%3),"kickoff":f"{i:02}"} for i in range(15)]
        self.assertEqual(select_diverse(c),select_diverse(list(reversed(c))))
