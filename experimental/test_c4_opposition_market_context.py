import unittest
from d0_contract import digest
from c4_opposition_market_context import route
class MarketContextTests(unittest.TestCase):
    def fixture(self,sport="football"):
        metric,unit,period=("goals_for","goals","regulation") if sport=="football" else ("points_for","points","including_overtime")
        e={"sport":sport,"participants":["A","B"]}
        claims={"opponent_id":["X","r1"],"format":[period,"r2"],"conditions":["same","r3"]}
        d={"trace":[{"metric":metric,"unit":unit,"participant":p,"observation_id":p,"claims":claims} for p in e["participants"]]}
        env={"documented_sha256":digest(d),"metrics":{metric:{"strata":[{"stratum":[sport,metric,digest([period,"same"]),"X"],"contrast":2}]}}}
        m={"contract":{"event_sha256":digest(e),"sport":sport,"family":"team_total","unit":unit,"period":period,"subject":"A","direction":"over"}}
        return e,d,env,m
    def test_positive(self):
        for sport in ("football","nba"):
            out=route(*self.fixture(sport))
            self.assertEqual(out["status"],"CONTEXT_ONLY")
            self.assertEqual(out["references"][0]["observation_ids"],["A"])
            self.assertIsNone(out["estimate"])
    def test_incompatible(self):
        for field,value in (("unit","other"),("participant","C")):
            e,d,env,m=self.fixture()
            d["trace"][0][field]=value
            env["documented_sha256"]=digest(d)
            self.assertEqual(route(e,d,env,m)["status"],"NO_COMPATIBLE_CONTEXT")
    def test_total(self):
        e,d,env,m=self.fixture()
        m["contract"].update(family="match_total",subject="match")
        self.assertEqual(route(e,d,env,m)["references"],[])
    def test_hash(self):
        e,d,env,m=self.fixture()
        d["trace"].clear()
        with self.assertRaisesRegex(ValueError,"hash"):route(e,d,env,m)
