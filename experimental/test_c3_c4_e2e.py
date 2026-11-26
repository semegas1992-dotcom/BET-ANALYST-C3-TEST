import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from c3_c4_mapping_bridge import inspect_mapping

JS = """
import fs from 'node:fs';
import crypto from 'node:crypto';
const source = fs.readFileSync(process.argv[1]);
const {createMatchSnapshot} = await import('data:text/javascript;base64,'+source.toString('base64'));
const snapshot = createMatchSnapshot({matches:[{id:1,utcDate:'2026-01-01T00:00:00Z',status:'FINISHED',homeTeam:{name:'Synthetic A'},awayTeam:{name:'Synthetic B'}}]}, {competition:'TEST',retrievedAt:'2026-01-03T00:00:00Z'});
const raw = JSON.stringify(snapshot);
console.log(JSON.stringify({raw,sha:crypto.createHash('sha256').update(raw).digest('hex')}));
"""

class EndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        builder = Path(__file__).resolve().parents[1] / 'c3-5-snapshot-builder.js'
        output = subprocess.check_output(['node','--input-type=module','-e',JS,str(builder)], timeout=15)
        envelope = json.loads(output)
        cls.raw = envelope['raw'].encode('utf-8')
        cls.sha = envelope['sha']

    def setUp(self):
        self.manifest = {'cutoff':'2026-01-04T00:00:00Z','mappings':[{'source_pointer':'/matches/0/homeTeam','target':'fixture.home','type':'string','unit':'none','record_id':'1','transformation':'identity','missing_policy':'reject','event_end':'2026-01-01T02:00:00Z','available_at':'2026-01-02T00:00:00Z','captured_at':'2026-01-03T00:00:00Z'}]}

    def test_chain(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),self.sha)
        self.assertEqual(json.loads(self.raw)['matches'][0]['homeTeam'],'Synthetic A')
        result = inspect_mapping(self.raw,self.sha,self.manifest,origin='synthetic')
        self.assertEqual(result['receipt']['status'],'QUARANTINE_UNMAPPED')
        self.assertEqual(result['receipt']['sha256'],self.sha)
        self.assertEqual(result['mapping']['status'],'QUARANTINE_UNVERIFIED')
        for stage in (result,result['receipt'],result['mapping']):
            self.assertIs(stage['engine_access'],False)
            self.assertEqual(stage['qualification'],'BLOCKED')
        self.assertEqual(result['publication'],'BLOCKED')
        self.assertEqual(result['receipt']['publication'],'BLOCKED')

    def test_tampered_bytes(self):
        with self.assertRaisesRegex(ValueError,'byte integrity'):
            inspect_mapping(self.raw+b' ',self.sha,self.manifest,origin='synthetic')

    def test_declared_real(self):
        with self.assertRaises(ValueError):
            inspect_mapping(self.raw,self.sha,self.manifest,origin='real')

    def test_future_capture(self):
        self.manifest['mappings'][0]['captured_at']='2026-01-05T00:00:00Z'
        with self.assertRaisesRegex(ValueError,'temporal leakage'):
            inspect_mapping(self.raw,self.sha,self.manifest,origin='synthetic')

    def test_missing_pointer(self):
        self.manifest['mappings'][0]['source_pointer']='/matches/0/missing'
        with self.assertRaises(KeyError):
            inspect_mapping(self.raw,self.sha,self.manifest,origin='synthetic')
