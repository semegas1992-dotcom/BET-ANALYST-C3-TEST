import unittest
from hashlib import sha256
from c4_quarantine import inspect
class QuarantineTests(unittest.TestCase):
    def test_intake(self):
        raw=b'fictional intake';h=sha256(raw).hexdigest()
        m={"event_id":"fixture","cutoff":"2026-01-02T00:00:00Z","sources":[{"url":"fixture","rights":"unknown","available_at":"2026-01-01T00:00:00Z","captured_at":"2026-01-03T00:00:00Z"}]}
        r=inspect(raw,h,m)
        self.assertIn("TEMPORAL_VIOLATION",r["issues"])
        self.assertIn("RIGHTS_UNVERIFIED",r["issues"])
        self.assertFalse(r["engine_access"])
        with self.assertRaises(ValueError):inspect(raw+b'x',h,m)
