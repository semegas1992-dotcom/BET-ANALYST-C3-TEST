import unittest
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_event_contract import RULES,audit
from c4_trajectories import audit as ta
from d0_contract import digest
class EventTrajectoryTests(unittest.TestCase):
    def test_multisport(self):
        for sport in RULES:
            d,e,r,essential,x=dossier(sport)
            f,u,p=RULES[sport]
            c=dict(event_sha256=digest(e),sport=sport,family=f,unit=u,period=p,subject="match",direction="over")
            result=run(d,e,r,essential,[1],"fixture",{},1,1,{},[],x,[dict(contract=c,thresholds=[2.5,1.5])])
            s=result["stages"];self.assertEqual(len(s["trajectories"]["trajectories"]),16)
            self.assertTrue(all(a["passed"] for a in result["audits"]))
            s["trajectories"]["trajectories"].pop()
            with self.assertRaises(ValueError):ta(s["specific_dependencies"],s["trajectories"])
            c["period"]="wrong"
            with self.assertRaises(ValueError):run(d,e,r,essential,[1],"fixture",{},1,1,{},[],x,[dict(contract=c,thresholds=[1.5,2.5])])
