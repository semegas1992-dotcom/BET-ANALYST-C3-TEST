import unittest
from tennis_stat_qualification import score_valid,service,qualify,surface_sample
class TennisStatTests(unittest.TestCase):
    def test_scores(self):
        for s,b in [("6-4 7-6(5)",3),("6-4 4-6 6-3 6-2",5)]:
            self.assertTrue(score_valid(s,b))
        for s in ("6-4","6-4 6-4 6-0","6-4 8-6","4-6 4-6","6-4 RET","6-4 6-4(2)"):
            self.assertFalse(score_valid(s,3))
    def fixture(self):
        stats={s+"_"+k:v for s in ("w","l") for k,v in zip(("svpt","1stIn","1stWon","2ndWon","ace","df","bpSaved","bpFaced"),(60,40,30,10,5,3,2,5))}
        return dict(id="x",surface="hard",winner_id="ATP:1",loser_id="ATP:2",score="6-4 6-4",best_of=3,stats=stats)
    def test_independent_return(self):
        r=self.fixture();q=qualify(r)
        self.assertEqual(q["service"]["w"]["won"],40)
        self.assertEqual(q["return"]["l"],dict(won=20,total=60))
    def test_missing_invalid(self):
        r=self.fixture();r["stats"]["w_svpt"]=None
        self.assertEqual(service(r["stats"],"w")["status"],"MISSING")
        r["stats"]["w_svpt"]=10
        self.assertEqual(service(r["stats"],"w")["status"],"INVALID")
    def test_samples(self):
        rows=[dict(self.fixture(),id=str(i)) for i in range(5)]
        self.assertTrue(surface_sample(rows,"ATP:1","hard")["sample_gate"])
        self.assertFalse(surface_sample(rows[:4],"ATP:1","hard")["sample_gate"])
        self.assertFalse(surface_sample(rows,"ATP:1","clay")["sample_gate"])
        self.assertFalse(surface_sample(rows+[rows[0]],"ATP:1","hard")["sample_gate"])
