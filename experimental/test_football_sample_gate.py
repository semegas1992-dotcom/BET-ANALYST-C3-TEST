import unittest
from football_d0_enriched import sample_gate
class SampleGateTests(unittest.TestCase):
    def side(self,n,eligible):
        p={"n":1,"home_share":1,"gf_mean":2,"ga_mean":0,"win_share":1}
        q={"n":1,"home_share":0,"gf_mean":0,"ga_mean":2,"win_share":0}
        return {**{k:{"shots_for":{"n":n,"eligible":eligible}} for k in ("advanced_season","advanced_last5")},"independent_check":{"bias":{k:{"covered":p,"missing":q} for k in ("advanced_season","advanced_last5")}}}
    def test_low_count(self):
        self.assertEqual(sample_gate(self.side(4,4))["advanced_season"]["fields"]["shots_for"]["status"],"INSUFFICIENT")
    def test_low_coverage(self):
        self.assertEqual(sample_gate(self.side(7,10))["advanced_season"]["fields"]["shots_for"]["status"],"INSUFFICIENT")
    def test_boundary(self):
        self.assertEqual(sample_gate(self.side(8,10))["advanced_season"]["fields"]["shots_for"]["status"],"DESCRIPTIVE_ONLY")
    def test_lock(self):
        self.assertFalse(sample_gate(self.side(10,10))["advanced_season"]["engine_access"])
    def test_gap(self):
        self.assertEqual(sample_gate(self.side(8,10))["advanced_season"]["profile_gaps"]["gf_mean"],2)
