import unittest, tempfile, io, json
from datetime import datetime, timezone, date, timedelta
from unittest.mock import Mock
from dunkapi_client import Budget, call, season_end

NOW=datetime(2026,11,24,12,tzinfo=timezone.utc)
class DunkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.b=Budget(self.tmp.name+"/budget.db")
        self.transport=Mock(return_value=io.BytesIO(json.dumps({"data":{"date":"2026-11-24","injuries":[],"count":0}}).encode()))
    def tearDown(self):
        self.b.db.close()
        self.tmp.cleanup()
    def request(self,endpoint="get_injuries",params=None,key="fake"):
        return call(endpoint,params or {},key,self.b,self.transport,NOW)
    def test_season(self):
        self.assertEqual(season_end(2026),2027)
    def test_injury_unknown(self):
        r=self.request()
        self.assertEqual(r["summary"]["unlisted_availability"],"UNKNOWN")
        self.assertFalse(r["engine_access"])
        self.assertEqual(r["credits_reserved"],2)
    def test_no_odds(self):
        with self.assertRaises(ValueError):self.request("get_odds")
        self.transport.assert_not_called()
    def test_no_key(self):
        with self.assertRaises(ValueError):self.request(key="")
        self.transport.assert_not_called()
    def test_future(self):
        with self.assertRaises(ValueError):self.request(params={"date":"2026-11-25"})
        self.transport.assert_not_called()
    def test_quota(self):
        self.b.reserve(391,NOW.date())
        with self.assertRaises(ValueError):self.request()
        self.transport.assert_not_called()
    def test_persistence(self):
        self.b.reserve(392,NOW.date())
        other=Budget(self.tmp.name+"/budget.db")
        try:
            with self.assertRaises(ValueError):other.reserve(1,NOW.date())
        finally:other.db.close()
    def test_rolling(self):
        self.b.reserve(392,NOW.date()-timedelta(days=31))
        self.b.reserve(392,NOW.date())
    def test_failure_reserved(self):
        self.transport.side_effect=TimeoutError()
        with self.assertRaises(TimeoutError):self.request()
        with self.assertRaises(ValueError):self.b.reserve(391,NOW.date())
        self.assertEqual(self.transport.call_count,1)
    def test_future_response(self):
        self.transport.return_value=io.BytesIO(b'{"data":{"date":"2026-11-25","injuries":[],"count":0}}')
        with self.assertRaises(ValueError):self.request()
    def test_bad_count(self):
        self.transport.return_value=io.BytesIO(b'{"data":{"date":"2026-11-24","injuries":[],"count":1}}')
        with self.assertRaises(ValueError):self.request()
    def test_old_report(self):
        self.transport.return_value=io.BytesIO(b'{"data":{"date":"2026-11-23","injuries":[],"count":0}}')
        self.assertEqual(self.request()["summary"]["freshness"],"OLDER_SNAPSHOT")
