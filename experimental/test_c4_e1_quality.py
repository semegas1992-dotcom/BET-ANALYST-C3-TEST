import unittest
from test_c4_e1 import fixture
from c4_e1_quality import assess
class QualityTests(unittest.TestCase):
    def rows(self):
        e,c,r=fixture();r.update(provider_group="P",claim_key="event:identity:current:id",measurement="A-B")
        return e,c,r
    def test_missing(self):
        e,c,r=self.rows();o=assess(e,c,[r],["identity","production"]);self.assertEqual(o["missing_or_unresolved"],["production"]);self.assertFalse(o["synthetic_documentary_gate"])
    def test_conflict(self):
        e,c,r=self.rows();o=assess(e,c,[r,dict(r,id="r2",measurement="C-D")],["identity"]);self.assertEqual(len(o["contradictions"]),1);self.assertFalse(o["synthetic_documentary_gate"])
    def test_dependency(self):
        e,c,r=self.rows();o=assess(e,c,[r,dict(r,id="r2")],["identity"]);self.assertEqual(o["dependencies"][0]["provider_groups"],["P"]);self.assertTrue(o["synthetic_documentary_gate"]);self.assertFalse(o["collection_complete"])
    def test_replacement(self):
        e,c,r=self.rows();bad=dict(r,id="bad",status="Accès bloqué");o=assess(e,c,[bad,dict(r,replaces="bad")],["identity"]);self.assertEqual(len(o["replacements"]),1)
    def test_invalid_replacement(self):
        e,c,r=self.rows()
        with self.assertRaises(ValueError):assess(e,c,[dict(r,replaces="absent")],["identity"])
    def test_different_scope(self):
        e,c,r=self.rows();o=assess(e,c,[r,dict(r,id="r2",claim_key="other-period",measurement="different")],["identity"]);self.assertEqual(o["contradictions"],[])
