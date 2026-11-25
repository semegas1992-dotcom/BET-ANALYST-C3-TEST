import unittest
from copy import deepcopy
from c4_matched_opposition import linked_contrast

class LinkedOppositionTests(unittest.TestCase):
    def fixture(self,sport):
        d=dict(sport=sport,cutoff="2026-01-03T00:00:00Z",observations=[])
        e=dict(participants=["a","b"])
        x=dict(indicators=[],observations=[],comparables=[])
        records=[]; rows=[]
        for side,p in zip(("A","B"),e["participants"]):
            for n in range(3):
                oid=side+str(n); v=n+(2 if side=="A" else 0)
                d["observations"].append(dict(id=oid,event_end="2026-01-01T00:00:00Z"))
                for suffix in ("i","o","c"):
                    records.append(dict(id=oid+suffix,status="Contrôlée",available_at="2026-01-02T00:00:00Z",captured_at="2026-01-02T01:00:00Z"))
                x["indicators"].append(dict(observation_id=oid,metric="m",value=v,unit="points",record_ids=[oid+"i"]))
                x["observations"].append(dict(observation_id=oid,participant=p,record_ids=[oid+"o"]))
                x["comparables"].append(dict(observation_id=oid,record_ids=[oid+"c"]))
                rows.append(dict(sport=sport,metric="m",context="same",opponent="X",side=side,observation_id=oid,value=v))
        return rows,d,e,x,records
    def test_linked(self):
        for sport in ("football","nba","tennis"):
            with self.subTest(sport=sport):
                out=linked_contrast(*self.fixture(sport))
                self.assertEqual(out["result"]["strata"][0]["contrast"],2)
                self.assertEqual(len(out["evidence"]),6)
                self.assertIsNone(out["result"]["forecast"])
    def test_divergent_value(self):
        a=self.fixture("football"); a[0][0]["value"]=99
        with self.assertRaisesRegex(ValueError,"measurement"): linked_contrast(*a)
    def test_missing_reference(self):
        a=self.fixture("nba"); a[4].pop(0)
        with self.assertRaisesRegex(ValueError,"chronology"): linked_contrast(*a)
    def test_late_capture(self):
        a=self.fixture("tennis"); a[4][0]["captured_at"]="2026-01-04T00:00:00Z"
        with self.assertRaisesRegex(ValueError,"chronology"): linked_contrast(*a)
    def test_wrong_participant(self):
        a=self.fixture("football"); a[0][0]["side"]="B"
        with self.assertRaisesRegex(ValueError,"identity"): linked_contrast(*a)
