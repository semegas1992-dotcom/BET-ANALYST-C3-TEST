import unittest
from c4_availability_routing import route
class TestRouting(unittest.TestCase):
    def test_scoped(self):
        for sport, family, unrelated in (("football","assists","scorer"),("nba","player_points","player_rebounds"),("tennis","aces","double_faults")):
            dep=dict(person_id="p",participant="A",role="test",record_ids=["r"],families_to_review=[family])
            markets=[{"contract":{"family":f,"subject":s}} for f,s in [(family,"q"),(unrelated,"q"),(unrelated,"p")]]
            rows=route({"sport":sport},{"dependencies":[dep]}, {},markets)["markets"]
            self.assertEqual([len(x["dependencies"]) for x in rows],[1,0,1])
            self.assertTrue(all(x["status"]=="NOT_EVALUATED" for x in rows))
            self.assertTrue(all(x["roster_robustness"]=="NOT_ESTABLISHED" for x in rows))
