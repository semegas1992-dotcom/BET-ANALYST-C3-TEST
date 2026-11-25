import unittest
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_market_scope import RULES
from c4_report import render
from d0_contract import digest

class IndividualContextTests(unittest.TestCase):
    def test_individual_subjects(self):
        for sport,family,role in (("football","scorer","finisher"),("football","assists","creator"),("nba","player_points","handler"),("nba","player_rebounds","interior"),("tennis","aces","server"),("tennis","double_faults","server")):
            with self.subTest(sport=sport,family=family):
                d,e,records,essential,x=dossier(sport)
                cfg=next(c for c in x["configurations"] if c["role"]==role)
                cfg["availability"]="unknown"
                for rec in records:
                    if rec["id"] in cfg["record_ids"]:
                        rec["measurement"]=rec["excerpt"]="unknown fictional "+role
                unit,period,_=RULES[sport][family]
                c=dict(event_sha256=digest(e),sport=sport,family=family,unit=unit,period=period,subject=cfg["person_id"],direction="over")
                result=run(d,e,records,essential,[1],"fixture",{},1,1,{},[],x,market_requests=[dict(contract=c,thresholds=[0.5,1.5])])
                report=render(result)
                scope=report["sections"][5]["market_scopes"][0]
                self.assertTrue(scope["assessment"])
                for row in scope["assessment"]:
                    self.assertIn("PERSON_UNRESOLVED",row["issues"])
                    self.assertIn("INDIVIDUAL_ESTIMATE_MISSING",row["issues"])
                    self.assertEqual(row["status"],"BLOCKED")
                links=report["sections"][5]["availability_routing"]["markets"][0]["dependencies"]
                self.assertTrue(any(link["person_id"]==cfg["person_id"] and link["reason"]=="DIRECT_SUBJECT" for link in links))
                self.assertEqual(report["qualification"],"BLOCKED")
