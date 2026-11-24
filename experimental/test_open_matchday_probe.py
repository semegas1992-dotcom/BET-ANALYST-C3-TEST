import unittest
from open_matchday_probe import inspect
class CSVTests(unittest.TestCase):
    def test_missing_not_zero(self):
        self.assertEqual(inspect(b"a,b\n0,\n")["nonempty"],{"a":1,"b":0})
    def test_extra_column(self):
        with self.assertRaises(ValueError):inspect(b"a,b\n1,2,3\n")
    def test_duplicate_header(self):
        with self.assertRaises(ValueError):inspect(b"a,a\n1,2\n")
