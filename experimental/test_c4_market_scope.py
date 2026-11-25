import unittest
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_market_scope import RULES
from d0_contract import digest
class MarketScopeTests(unittest.TestCase):
    def test_families(self):
        for sport,rules in RULES.items():
            d,e,r,essential,x=dossier(sport)
            requests=[]
            for family,(unit,period,kind) in rules.items():
                subject="match" if kind=="match" else e["participants"][0] if kind=="team" else x["configurations"][0]["person_id"]
                c=dict(event_sha256=digest(e),sport=sport,family=family,unit=unit,period=period,subject=subject,direction="win" if family=="result" else "under")
                requests.append(dict(contract=c,thresholds=[] if family=="result" else [1.5,2.5]))
            result=run(d,e,r,essential,[1],"fixture",{},1,1,{},[],x,market_requests=requests)
            reports=result["stages"]["E5"]["market_scopes"]
            self.assertEqual(len(reports),len(rules))
            self.assertTrue(all(a["status"]=="BLOCKED" for m in reports for a in m["assessment"]))
            requests[0]["contract"]["period"]="wrong"
            with self.assertRaises(ValueError):run(d,e,r,essential,[1],"fixture",{},1,1,{},[],x,market_requests=requests)
