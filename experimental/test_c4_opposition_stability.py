import unittest
from c4_matched_opposition import stability
class StabilityTests(unittest.TestCase):
    def test_stable(self):
        s=stability({"A":[2,3,4],"B":[0,1,2]})
        self.assertEqual((s["minimum"],s["maximum"],s["recalculations"]),(1.5,2.5,6))
        self.assertTrue(s["sign_preserved"])
    def test_sensitive(self):
        s=stability({"A":[0,0,9],"B":[2,2,2]})
        self.assertEqual((s["minimum"],s["maximum"]),(-2,2.5))
        self.assertFalse(s["sign_preserved"])
    def test_equal(self):
        s=stability({"A":[1,1,1],"B":[1,1,1]})
        self.assertEqual((s["minimum"],s["maximum"]),(0,0))
        self.assertTrue(s["sign_preserved"])
