import unittest
from copy import deepcopy
from c4_positive_fixtures import dossier
from c4_integrated import run
from c4_report import render
from c4_market_scope import RULES
from d0_contract import digest
class OppositionEndToEndTests(unittest.TestCase):
    def test_report_chain(self):
        for mode in ("zero","positive","negative","mixed","incomplete","contradictory"):
            with self.subTest(mode=mode):self.check_chain(mode)
    def check_chain(self,mode):
        for sport,metric in (("football","goals_for"),("nba","points_for"),("tennis","first_serve_won")):
            with self.subTest(sport=sport):
                d,e,records,essential,x=dossier(sport)
                # Expand the existing fictional NBA/tennis observations to three per participant.
                if sport!="football" or mode=="contradictory":
                    for o in list(d["observations"]):
                        old=o["id"]
                        for n in (1,2,3,4,5) if mode=="contradictory" else (1,2):
                            new=old+str(n)
                            d["observations"].append(dict(deepcopy(o),id=new))
                            for key in ("observations","comparables","indicators"):
                                for item in [v for v in x[key] if v["observation_id"]==old]:
                                    item=deepcopy(item);item["observation_id"]=new
                                    if key=="observations":item["historical_event_id"]="historical-"+new
                                    x[key].append(item)
                unit,period,_=RULES[sport]["team_total"]
                rows=[]
                for link in x["observations"]:
                    oid=link["observation_id"]
                    comp=next(c for c in x["comparables"] if c["observation_id"]==oid)
                    for field,val in (("opponent_id","X"),("format",period),("conditions","same")):
                        rid=oid+":"+field
                        records.append(dict(id=rid,topic="baseline",event_id=e["id"],source="synthetic_fixture",available_at=d["cutoff"],captured_at=d["cutoff"],status="Contrôlée",opened=True,scope_checked=True,coherence_checked=True,excerpt=val,provider_group="fictional",claim_key=oid+":"+field+":historical:label",measurement=val))
                        comp["record_ids"].append(rid)
                    i=next(i for i in x["indicators"] if i["observation_id"]==oid and i["metric"]==metric)
                    rows.append(dict(sport=sport,metric=metric,context="same",opponent="X",side="A" if link["participant"]==e["participants"][0] else "B",observation_id=oid,value=i["value"]))
                if mode=="contradictory":
                    for side in ("A","B"):
                        for n,row in enumerate([r for r in rows if r["side"]==side]):
                            rec=next(v for v in records if v["id"]==row["observation_id"]+":opponent_id")
                            rec["measurement"]=rec["excerpt"]="X" if n<3 else "Y"
                if mode!="zero":
                    arows=[r for r in rows if r["side"]=="A"]
                    for n,row in enumerate(arows):
                        delta=(2 if n<3 else -1) if mode=="contradictory" else 2 if mode=="positive" else -1 if mode=="negative" else (4 if n==0 else -1) if mode=="mixed" else 0
                        row["value"]+=delta
                        i=next(i for i in x["indicators"] if i["observation_id"]==row["observation_id"] and i["metric"]==metric)
                        i["value"]=row["value"]
                        for rec in records:
                            if rec["id"] in i["record_ids"]:
                                rec["measurement"]=rec["excerpt"]=str(i["value"])
                    if mode=="incomplete":
                        comp=next(c for c in x["comparables"] if c["observation_id"]==arows[0]["observation_id"])
                        comp["record_ids"].remove(arows[0]["observation_id"]+":conditions")
                c=dict(event_sha256=digest(e),sport=sport,family="team_total",unit=unit,period=period,subject=e["participants"][0],direction="over")
                result=run(d,e,records,essential,[1],"fixture",{},1,1,{},[],x,market_requests=[dict(contract=c,thresholds=[1.5,2.5])],matched_rows=rows)
                stages=result["stages"];op=stages["matched_opposition"]
                report=render(result)
                if mode=="contradictory":
                    self.assertEqual({v["contrast"] for v in op["documented"]["result"]["strata"]},{2,-1})
                self.assertEqual(op["documented"]["coverage"]["included"],len(rows)-(mode=="incomplete"))
                self.assertEqual(op["envelope"]["metrics"][metric]["direction"],{"positive":"POSITIVE","negative":"NEGATIVE"}.get(mode,"UNRESOLVED"))
                self.assertEqual(report["sections"][3]["opposition_context"],op["envelope"]["scenario_context"])
                self.assertEqual(report["sections"][4]["descriptive_envelopes"],op["envelope"]["metrics"])
                self.assertEqual(report["sections"][5]["opposition_context"],stages["E5"]["opposition_context"])
                self.assertEqual(stages["E5"]["opposition_context"][0]["status"],"NO_COMPATIBLE_CONTEXT" if sport=="tennis" or (mode=="incomplete" and sport=="nba") else "CONTEXT_ONLY")
                self.assertEqual(report["qualification"],"BLOCKED")
                self.assertEqual(report["quick_summary"]["decision"],"NOT_ESTABLISHED")
                result["stages"]["E5"]["opposition_context"].clear()
                with self.assertRaisesRegex(ValueError,"integrity"):render(result)
