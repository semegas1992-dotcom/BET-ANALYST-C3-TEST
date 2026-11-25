import unittest
from c4_scoped_uncertainty import build
from d0_contract import digest
class SnapshotTests(unittest.TestCase):
    def test_input_mutation(self):
        d={'mechanisms':{'m':{'issues':['missing'],'record_ids':['r']}}}
        t={'trajectories':[{'assignment':{'m':'holds'},'issues':['missing']}]}
        out=build(d,t); before=digest(out)
        d['mechanisms']['m']['issues'].append('new')
        d['mechanisms']['m']['record_ids'].clear()
        t['trajectories'][0]['assignment']['m']='fails'
        t['trajectories'][0]['issues'].clear()
        self.assertEqual(digest(out),before)
    def test_output_mutation(self):
        d={'mechanisms':{'m':{'issues':['missing'],'record_ids':['r']}}}
        t={'trajectories':[{'assignment':{'m':'holds'},'issues':['missing']}]}
        before=(digest(d),digest(t)); out=build(d,t)
        row=out['rows'][0]; row['assignment']['m']='fails'; row['global_issues'].clear(); row['links'][0]['issues'].clear(); row['links'][0]['record_ids'].clear()
        self.assertEqual((digest(d),digest(t)),before)
