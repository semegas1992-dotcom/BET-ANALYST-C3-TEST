import unittest
from football_source_aliases import identity,GROUPS
class AliasTests(unittest.TestCase):
    def test_observed_aliases(self):
        for code,groups in GROUPS.items():
            for g in groups:
                self.assertEqual(len({identity(code,v) for v in g}),1)
    def test_distinct_groups(self):
        for code,groups in GROUPS.items():
            self.assertEqual(len(groups),len({identity(code,g[0]) for g in groups}))
    def test_scoped(self):
        self.assertNotEqual(identity("FL1","Spurs"),identity("FL1","Tottenham"))
    def test_no_fuzzy(self):
        self.assertNotEqual(identity("PL","Manchester City"),identity("PL","Man Utd"))
    def test_paris_distinct(self):
        self.assertNotEqual(identity("FL1","Paris FC"),identity("FL1","PSG"))
