import unittest,hashlib
from c4_t01_receipt import receive
from c4_trajectory_prompts import build
class TestExtensions(unittest.TestCase):
    def test_receipt(self):
        raw=b'{"example":true}'
        self.assertFalse(receive(raw,hashlib.sha256(raw).hexdigest())["engine_access"])
        with self.assertRaises(ValueError): receive(raw,"bad")
    def test_duplicate(self):
        raw=b'{"a":1,"a":2}'
        with self.assertRaises(ValueError): receive(raw,hashlib.sha256(raw).hexdigest())
    def test_prompts(self):
        for sport in ("football","nba","tennis"):
            r=build(sport,{"trajectories":[{"assignment":{},"issues":["missing"]}]})
            self.assertEqual(len(r["rows"][0]["prompts"]),3)
            self.assertIsNone(r["dominant"])
            self.assertEqual(r["rows"][0]["issues"],["missing"])
