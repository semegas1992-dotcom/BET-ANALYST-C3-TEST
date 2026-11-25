"""Coverage monitoring, no raw source persistence."""
import json
from collections import Counter
from football_qualification_v5 import rejection_reasons,select_diverse
def summarize(d):
    leagues={}
    for code,v in d["leagues"].items():
        counts=v["counts"]; total=sum(counts.values()); n=counts.get("anchored",0)
        leagues[code]={"anchored":n,"total":total,"coverage":n/total if total else None,"source_hash":v["sha256"]}
    issues=[]
    for x in d["dossiers"]:
        if rejection_reasons(x["sides"]):issues.append("P2:"+str(x["id"]))
    if not d["audit"]["pass"] or not d["diversity"]["pass"]:issues.append("upstream audit")
    if not all(v["accounting_ok"] for v in d["leagues"].values()):issues.append("accounting")
    if d["engine_access"] is not False:issues.append("engine lock")
    if len({x["id"] for x in d["dossiers"]+d["rejections"]})!=len(d["dossiers"])+len(d["rejections"]):issues.append("duplicate")
    if len(d["rejections"])!=d["rejected_candidates"]:issues.append("rejection accounting")
    return {"leagues":leagues,"rejections":dict(Counter(x["competition"] for x in d["rejections"])),"selected":d["diversity"]["selected"],"available":d["diversity"]["available"],"issues":issues,"pass":not issues,"engine_access":False}
def main():
    with open("football-d0-enriched.json") as f:d=json.load(f)
    a=summarize(d)
    with open("football-coverage-monitor.json","w") as f:json.dump(a,f,indent=2,sort_keys=True)
    print(json.dumps(a,sort_keys=True))
    return int(not a["pass"])
if __name__=="__main__":raise SystemExit(main())
