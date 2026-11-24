import unittest
from football_d0_preview import qualify,preview
from datetime import date
class PreviewTests(unittest.TestCase):
    def test_shots(self):
        r=qualify({"home_shots":"1","home_target":"2","home_fouls":"3"})
        self.assertIsNone(r["home_target"]["value"])
        self.assertEqual(r["home_fouls"]["value"],3)
    def test_corners(self):
        self.assertEqual(qualify({"home_corners":"4","home_corners_1h":"1","home_corners_2h":"2"})["home_corners"]["status"],"QUARANTINED_CONFLICT")
    def test_zero(self):self.assertEqual(qualify({"home_shots":"0"})["home_shots"]["value"],0)
    def test_missing(self):self.assertEqual(qualify({})["home_shots"]["status"],"UNAVAILABLE")
    def test_empty(self):self.assertTrue(preview([],[],date(2026,11,24))["accounting_ok"])
