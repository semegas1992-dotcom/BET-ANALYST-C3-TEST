import unittest,copy
from tennis_d0 import build
from d0_contract import digest
class TennisD0Tests(unittest.TestCase):
    def fixture(self):
        stats={p+"_"+k:v for p in ("w","l") for k,v in zip(("svpt","1stIn","1stWon","2ndWon","ace","df","bpSaved","bpFaced"),(60,40,30,10,5,3,2,5))}
        row=dict(id="m1",tour="ATP",winner_id="ATP:1",loser_id="ATP:3",surface="hard",best_of=3,score="6-4 6-4",stats=stats)
        return dict(schema="D0_EXPERIMENTAL_V1",sport="tennis",origin="synthetic",engine_access=False,cutoff="2026-01-02T00:00:00Z",kickoff="2026-01-03T00:00:00Z",event=dict(tour="ATP",players=["ATP:1","ATP:2"],surface="hard",best_of=3),observations=[dict(id="m1",source="synthetic_fixture",event_end="2026-01-01T00:00:00Z",available_at="2026-01-01T01:00:00Z",captured_at="2026-01-01T02:00:00Z",row=row)])
    def test_digest(self):
        d=self.fixture();r=build(d);self.assertEqual(r["input_sha256"],digest(d));self.assertEqual(r,build(d));self.assertEqual(r.pop("sha256"),digest(r))
    def test_lock(self):
        r=build(self.fixture());self.assertFalse(r["engine_access"]);self.assertEqual(r["qualification"],"BLOCKED");self.assertFalse(r["samples"]["ATP:2"]["sample_gate"])
    def test_real_rejected(self):
        d=self.fixture();d["origin"]="archive"
        with self.assertRaises(ValueError):build(d)
    def test_leakage(self):
        d=self.fixture();d["observations"][0]["available_at"]="2026-01-04T00:00:00Z"
        with self.assertRaises(ValueError):build(d)
    def test_identity(self):
        d=self.fixture();d["event"]["players"][1]="WTA:2"
        with self.assertRaises(ValueError):build(d)
    def test_duplicate(self):
        d=self.fixture();d["observations"].append(copy.deepcopy(d["observations"][0]))
        with self.assertRaises(ValueError):build(d)

    def test_forbidden(self):
        d=self.fixture();d["event"]["odds"]=2
        with self.assertRaises(ValueError):build(d)
    def test_bad_score(self):
        d=self.fixture();d["observations"][0]["row"]["score"]="6-4"
        with self.assertRaises(ValueError):build(d)
    def test_bad_id(self):
        d=self.fixture();d["event"]["players"][1]="ATP:abc"
        with self.assertRaises(ValueError):build(d)
