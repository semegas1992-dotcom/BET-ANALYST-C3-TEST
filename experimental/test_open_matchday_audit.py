import unittest
from open_matchday_audit import integer,audit
from datetime import date
class AuditTests(unittest.TestCase):
    def test_null(self):self.assertIsNone(integer(""))
    def test_zero(self):self.assertEqual(integer("0"),0)
    def test_negative(self):
        with self.assertRaises(ValueError):integer("-1")
    def test_decimal(self):
        with self.assertRaises(ValueError):integer("1.5")
    def test_cutoff(self):
        self.assertEqual(audit(b"date,home,away\n2026-11-24,A,B\n",date(2026,11,24))["issues"]["cutoff_excluded"],1)
