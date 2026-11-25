import unittest
from datetime import datetime,timezone
from football_source_aliases import identity
from football_d0_enriched import join

class ResidualAliasTests(unittest.TestCase):
    def test_aliases(self):
        for code,a,b in [("BL1","TSG 1899 Hoffenheim","TSG Hoffenheim"),("SA","FC Internazionale Milano","Internazionale"),("SA","Como 1907","Como"),("PD","Real Racing Club de Santander","R. Racing Club"),("PD","RC Deportivo La Coruña","RC Deportivo")]:
            self.assertEqual(identity(code,a),identity(code,b))
    def test_distinct(self):
        self.assertNotEqual(identity("SA","AC Milan"),identity("SA","Internazionale"))
        self.assertNotEqual(identity("PD","Racing de Ferrol"),identity("PD","R. Racing Club"))
    def test_scope(self):
        self.assertNotEqual(identity("PL","Como 1907"),identity("PL","Como"))
    def test_score_conflict(self):
        m={"id":1,"utcDate":"2026-10-01T12:00:00Z","lastUpdated":"2026-10-02T00:00:00Z","homeTeam":{"name":"Como 1907"},"awayTeam":{"name":"Roma"},"score":{"fullTime":{"home":2,"away":1}}}
        r={"date":"2026-10-01","home":"Como","away":"Roma","ft_home":"1","ft_away":"1"}
        a,c,_=join([m],[r],datetime(2026,11,1,tzinfo=timezone.utc),"SA")
        self.assertEqual(a,{})
        self.assertEqual(c,{"conflict":1})
    def test_duplicate(self):
        m={"id":1,"utcDate":"2026-10-01T12:00:00Z","lastUpdated":"2026-10-02T00:00:00Z","homeTeam":{"name":"Como 1907"},"awayTeam":{"name":"Roma"},"score":{"fullTime":{"home":2,"away":1}}}
        r={"date":"2026-10-01","home":"Como","away":"Roma","ft_home":"2","ft_away":"1"}
        a,c,_=join([m],[r,dict(r)],datetime(2026,11,1,tzinfo=timezone.utc),"SA")
        self.assertEqual(a,{})
        self.assertEqual(c,{"ambiguous":1})
