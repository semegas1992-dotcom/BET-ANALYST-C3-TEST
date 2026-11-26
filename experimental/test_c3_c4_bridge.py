import hashlib
import json
import unittest
from c3_c4_bridge import quarantine_snapshot

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.dumps({'schema':'BET_ANALYST_MATCH_SNAPSHOT_V1','status':'RECEIVED_UNVERIFIED','matches':[]}).encode()
        self.sha = hashlib.sha256(self.raw).hexdigest()
    def test_quarantine(self):
        result = quarantine_snapshot(self.raw, self.sha, origin='synthetic')
        self.assertFalse(result['engine_access'])
        self.assertEqual(result['qualification'], 'BLOCKED')
    def test_real_rejected(self):
        with self.assertRaises(ValueError): quarantine_snapshot(self.raw, self.sha, origin='real')
    def test_tamper(self):
        with self.assertRaises(ValueError): quarantine_snapshot(self.raw+b' ', self.sha, origin='synthetic')
    def test_wrong_schema(self):
        raw=b'{}'
        with self.assertRaises(ValueError): quarantine_snapshot(raw, hashlib.sha256(raw).hexdigest(), origin='synthetic')
