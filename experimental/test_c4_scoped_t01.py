import unittest
from c4_scoped_uncertainty import build
from c4_t01_mapping import validate
class Tests(unittest.TestCase):
    def test_scoped(self):
        for sport in ('football','nba','tennis'):
            d={'mechanisms':{'a':{'issues':['absence'],'record_ids':['r1']},'b':{'issues':[],'record_ids':['r2']}}}
            t={'trajectories':[{'assignment':{'a':'fails','b':'holds'},'issues':['absence']}]}
            r=build(d,t)['rows'][0]
            self.assertEqual(r['links'][1]['issues'],[])
            self.assertEqual(r['links'][0]['record_ids'],['r1'])
            self.assertEqual(r['global_issues'],['absence'])
    def test_quarantine(self):
        m={'cutoff':'2026-11-25T12:00:00Z','mappings':[dict(source_pointer='/x',target='x',type='number',unit='points',record_id='r',transformation='identity',missing_policy='reject',event_end='2026-11-24T12:00:00Z',available_at='2026-11-24T13:00:00Z',captured_at='2026-11-25T11:00:00Z')]}
        self.assertFalse(validate(m)['engine_access'])
        m['mappings'][0]['captured_at']='2026-11-26T12:00:00Z'
        self.assertRaises(ValueError,validate,m)
