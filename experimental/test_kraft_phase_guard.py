import unittest
from kraft_phase_guard import validate_phase,validate_market,FOOTBALL_FAMILIES
from football_pipeline_demo import analyze
from test_d0_pipeline_demo import fixture
class KraftGuardTests(unittest.TestCase):
    def test_no_forced_scenarios(self):
        self.assertEqual(analyze(fixture())["scenarios"],[])
    def test_excluded_markets(self):
        for f in ("corners","cards","player_shots","player_shots_on_target"):
            with self.assertRaises(ValueError):validate_market(f)
    def test_allowed_markets(self):
        for f in FOOTBALL_FAMILIES:validate_market(f)
    def test_pre_odds_nested(self):
        for k in ("odds","value","stake","ticket","parlay","profitability","simulation","probabilities"):
            with self.assertRaises(ValueError):validate_phase({"engine_access":False,"nested":[{k:1}]})
    def test_market_guard(self):
        with self.assertRaises(ValueError):validate_phase({"engine_access":False,"markets":[{"family":"corners"}]})
    def test_lock(self):
        with self.assertRaises(ValueError):validate_phase({"engine_access":True})
