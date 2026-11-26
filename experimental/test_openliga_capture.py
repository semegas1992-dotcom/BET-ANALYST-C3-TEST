import unittest,json
from datetime import datetime,timezone
from openliga_capture import capture
class CaptureTests(unittest.TestCase):
    def test_locks(self):
        now=lambda:datetime(2026,11,26,tzinfo=timezone.utc)
        raw=json.dumps([{"matchID":1,"matchDateTimeUTC":"2026-11-28T14:30:00Z","matchIsFinished":False}]).encode()
        original,report=capture(2026,"2026-11-27T00:00:00Z",lambda _:raw,now)
        self.assertEqual(original,raw)
        self.assertFalse(report["engine_access"])
        self.assertEqual(report["publication"],"BLOCKED")
        self.assertIn("TIMESTAMP_MISSING",report["quarantine"]["issues"])
        self.assertIn("RIGHTS_UNVERIFIED",report["quarantine"]["issues"])
        self.assertEqual(len(report["upcoming"]),1)
    def test_late(self):
        with self.assertRaises(ValueError):
            capture(2026,"2026-11-25T00:00:00Z",lambda _:b"[]",lambda:datetime(2026,11,26,tzinfo=timezone.utc))
if __name__=="__main__":unittest.main()
