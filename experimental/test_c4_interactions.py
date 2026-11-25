import unittest
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_interactions import audit
from c4_market_independent import audit as market_audit
from c4_market_scope import RULES
from d0_contract import digest
class InteractionTests(unittest.TestCase):
    def test_counterexamples(self):
        for sport in RULES:
            d,e,r,essential,x=dossier(sport)
            unit,period,_=RULES[sport]["match_total"]
            c=dict(event_sha256=digest(e),sport=sport,family="match_total",unit=unit,period=period,subject="match",direction="over")
            s=run(d,e,r,essential,[1],"fixture",{},1,1,{},[],x,market_requests=[dict(contract=c,thresholds=[1.5,2.5])])["stages"]
            self.assertEqual(len(s["interactions"]["rows"]),16)
            m=s["E5"]["market_scopes"][0]
            m["assessment"][0]["issues"]=[]
            with self.assertRaises(ValueError):market_audit(e,x,s["trajectories"],m)
            s["interactions"]["rows"][0]["estimate"]=10
            with self.assertRaises(ValueError):audit(s["specific_dependencies"],s["trajectories"],s["interactions"])
