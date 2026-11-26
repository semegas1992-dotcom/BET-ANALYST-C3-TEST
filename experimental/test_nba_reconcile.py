import unittest
from copy import deepcopy
from nba_reconcile import compare
class TestReconcile(unittest.TestCase):
    def test_cases(self):
        a=dict(date='2020-01-01',home='A',away='B',home_score=100,away_score=96,home_periods=[25]*4,away_periods=[24]*4)
        for field,value,status in [('date','2020-01-02','DIVERGENCE'),('home','C','DIVERGENCE'),('away_score',None,'INCOMPLETE_OR_INVALID'),('home_periods',[24,26,25,25],'DIVERGENCE'),('home_score',101,'INCOMPLETE_OR_INVALID'),('home_periods',[True,25,25,49],'INCOMPLETE_OR_INVALID')]:
            with self.subTest(field=field,value=value):
                b=deepcopy(a);b[field]=value;self.assertEqual(compare(a,b)['status'],status)
        self.assertEqual(compare(a,a)['status'],'MATCH')
    def test_overtime(self):
        a=dict(date='2020-01-01',home='A',away='B',home_score=110,away_score=108,home_periods=[25]*4+[10],away_periods=[25]*4+[8]);self.assertEqual(compare(a,a)['status'],'MATCH');a['away_periods']=[24]*4+[12];self.assertEqual(compare(a,a)['status'],'INCOMPLETE_OR_INVALID')
    def test_locks(self):
        self.assertEqual(compare({},None),dict(status='INCOMPLETE_OR_INVALID',differences=[],engine_access=False,publication='BLOCKED',qualification='BLOCKED'))
