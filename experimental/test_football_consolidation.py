import unittest
from datetime import datetime,timezone
from football_source_aliases import identity
from football_d0_enriched import join,aggregate
from football_coverage_monitor import summarize
class ConsolidationTests(unittest.TestCase):
    def test_aliases(self):
        self.assertEqual(identity("PD","Club Atlético de Madrid"),identity("PD","Atlético de Madrid"))
        self.assertEqual(identity("SA","Venezia FC"),identity("SA","Venezia"))
        self.assertNotEqual(identity("PD","Real Madrid"),identity("PD","Atlético de Madrid"))
    def test_replay(self):
        m={"id":1,"utcDate":"2026-10-01T12:00:00Z","lastUpdated":"2026-10-02T00:00:00Z","homeTeam":{"name":"Venezia FC"},"awayTeam":{"name":"Roma"},"score":{"fullTime":{"home":2,"away":1}}}
        r={"date":"2026-10-01","home":"Venezia","away":"Roma","ft_home":"2","ft_away":"1","home_shots":"10","away_shots":"8","home_target":"4","away_target":"3"}
        cutoff=datetime(2026,11,1,tzinfo=timezone.utc)
        a=join([m],[r],cutoff,"SA")
        b=join([dict(m)],[dict(r)],cutoff,"SA")
        self.assertEqual(a,b)
        self.assertEqual(a[1],{"anchored":1})
        self.assertEqual(aggregate([{"id":1,"home":True}],a[0]),aggregate([{"id":1,"home":True}],b[0]))
    def test_monitor_rejects_lock(self):
        d={"leagues":{},"dossiers":[],"rejections":[],"rejected_candidates":0,"audit":{"pass":True},"diversity":{"pass":True,"selected":{},"available":{}},"engine_access":True}
        self.assertFalse(summarize(d)["pass"])
    def test_monitor_rejection_accounting(self):
        d={"leagues":{},"dossiers":[],"rejections":[],"rejected_candidates":1,"audit":{"pass":True},"diversity":{"pass":True,"selected":{},"available":{}},"engine_access":False}
        self.assertFalse(summarize(d)["pass"])
