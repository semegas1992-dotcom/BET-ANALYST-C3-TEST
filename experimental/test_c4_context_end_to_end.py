import unittest
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_report import render
from c4_market_scope import RULES
from d0_contract import digest

class ContextEndToEndTests(unittest.TestCase):
    def test_unavailability_to_report(self):
        for sport,role in (("football","creator"),("nba","handler"),("tennis","server")):
            with self.subTest(sport=sport):
                d,e,records,essential,x=dossier(sport)
                cfg=next(c for c in x["configurations"] if c["role"]==role)
                cfg["availability"]="unknown"
                for record in records:
                    if record["id"] in cfg["record_ids"]:
                        record["measurement"]="unknown fictional "+role
                        record["excerpt"]=record["measurement"]
                unit,period,kind=RULES[sport]["match_total"]
                contract=dict(event_sha256=digest(e),sport=sport,family="match_total",unit=unit,period=period,subject="match",direction="under")
                result=run(d,e,records,essential,[1],"fixture",{},1,1,{},[],x,market_requests=[dict(contract=contract,thresholds=[1.5,2.5])])
                stages=result["stages"]
                self.assertEqual(result["stage_sha256"],{k:digest(v) for k,v in stages.items()})
                links=[link for row in stages["scoped_uncertainty"]["rows"] for link in row["links"]]
                self.assertTrue(any(set(cfg["record_ids"]) <= set(link["record_ids"]) and any(i.startswith("ROLE_UNRESOLVED:") for i in link["issues"]) for link in links))
                routing=stages["availability_routing"]["markets"][0]
                self.assertTrue(any(dep["person_id"]==cfg["person_id"] and dep["trigger"]["status"]=="UNVERIFIED" for dep in routing["dependencies"]))
                self.assertEqual(routing["status"],"NOT_EVALUATED")
                report=render(result)
                self.assertEqual(report["sections"][3]["scoped_uncertainty"],stages["scoped_uncertainty"])
                self.assertEqual(report["sections"][5]["availability_routing"],stages["availability_routing"])
                self.assertIsNone(report["quick_summary"]["dominant_trajectory"])
                self.assertEqual(report["quick_summary"]["decision"],"NOT_ESTABLISHED")
                for obj in (result,report,report["quick_summary"]):
                    self.assertFalse(obj["engine_access"])
                    self.assertEqual(obj["qualification"],"BLOCKED")
                    self.assertEqual(obj["publication"],"BLOCKED")
