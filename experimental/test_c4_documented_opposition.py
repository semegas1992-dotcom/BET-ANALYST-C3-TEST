import unittest
from test_c4_linked_opposition import LinkedOppositionTests
from c4_matched_opposition import documented_contrast
class DocumentedOppositionTests(unittest.TestCase):
    def fixture(self,sport):
        rows,d,e,x,records=LinkedOppositionTests().fixture(sport)
        for link,comp in zip(x["observations"],x["comparables"]):
            oid=link["observation_id"]
            link["historical_event_id"]="event-"+oid
            for field,value in (("opponent_id","X"),("format","format1"),("conditions","conditions1")):
                rid=oid+field
                records.append(dict(id=rid,status="Contrôlée",available_at="2026-01-02T00:00:00Z",captured_at="2026-01-02T01:00:00Z",topic="baseline",source="synthetic_fixture",opened=True,scope_checked=True,coherence_checked=True,claim_key=oid+":"+field+":historical:label",measurement=value,excerpt=value))
                comp["record_ids"].append(rid)
        return rows,d,e,x,records
    def test_positive(self):
        for sport in ("football","nba","tennis"):
            with self.subTest(sport=sport):
                out=documented_contrast(*self.fixture(sport))
                self.assertEqual(out["coverage"]["included"],6)
                self.assertEqual(out["result"]["strata"][0]["contrast"],2)
                self.assertIsNone(out["forecast"])
    def test_format_separation(self):
        a=self.fixture("football")
        rec=next(r for r in a[4] if r["id"]=="A0format")
        rec["measurement"]=rec["excerpt"]="format2"
        out=documented_contrast(*a)
        self.assertTrue(all(s["contrast"] is None for s in out["result"]["strata"]))
    def test_missing_claim(self):
        a=self.fixture("nba")
        a[3]["comparables"][0]["record_ids"].remove("A0conditions")
        out=documented_contrast(*a)
        self.assertEqual(out["coverage"]["included"],5)
        self.assertEqual(out["excluded"][0]["missing"],["conditions"])
