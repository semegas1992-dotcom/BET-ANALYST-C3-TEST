import hashlib
import json
import unittest
from c3_c4_mapping_bridge import inspect_mapping

class MappingBridgeTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.dumps({'schema':'BET_ANALYST_MATCH_SNAPSHOT_V1','status':'RECEIVED_UNVERIFIED','matches':[{'id':1,'homeTeam':'Synthetic A'}]}).encode()
        self.sha = hashlib.sha256(self.raw).hexdigest()
        t = '2026-01-01T00:00:00Z'
        self.manifest = {'cutoff':t,'mappings':[{'source_pointer':'/matches/0/homeTeam','target':'fixture.home','type':'string','unit':'none','record_id':'1','transformation':'identity','missing_policy':'reject','event_end':t,'available_at':t,'captured_at':t}]}
    def run_bridge(self):
        return inspect_mapping(self.raw,self.sha,self.manifest,origin='synthetic')
    def test_quarantine(self):
        self.assertEqual(self.run_bridge()['mapping']['status'],'QUARANTINE_UNVERIFIED')
        self.assertFalse(self.run_bridge()['engine_access'])
    def test_missing_pointer(self):
        self.manifest['mappings'][0]['source_pointer']='/missing'
        with self.assertRaises(KeyError): self.run_bridge()
    def test_leakage(self):
        self.manifest['mappings'][0]['captured_at']='2026-01-02T00:00:00Z'
        with self.assertRaisesRegex(ValueError,'temporal leakage'): self.run_bridge()
    def test_empty(self):
        self.manifest['mappings']=[]
        with self.assertRaises(ValueError): self.run_bridge()
