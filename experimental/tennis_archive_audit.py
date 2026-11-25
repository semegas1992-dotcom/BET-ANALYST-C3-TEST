"""Pinned archive audit; no raw data publication."""
import json,hashlib,csv,io
from pathlib import Path
from collections import Counter
from tennis_csv_adapter import parse_csv
from tennis_stat_qualification import qualify
from tennis_independent_audit import audit
REV="83733587353df8a41f2fd4f516147d5aa83f5a8d"
def run():
    result={"revision":REV,"engine_access":False,"publication":"BLOCKED","tours":{}}
    for tour in ("ATP","WTA"):
        raw=Path(tour.lower()+".csv").read_bytes()
        parsed=parse_csv(raw,tour)
        original=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        rejected=Counter()
        for r in parsed["rejected"]:
            surface=(original[r["row"]-2].get("surface") or "unknown").strip().lower()
            rejected[(surface,r["reason"])]+=1
        accepted=0
        for r in parsed["rows"]:
            q=qualify(r)
            reasons=[]
            if not q["score_valid"]:reasons.append("score")
            for side,s in q["service"].items():
                if s["status"]!="OK":reasons.append(side+":"+s["status"])
            if reasons:rejected[(r["surface"],"+".join(reasons))]+=1
            else:accepted+=1
        a=audit(parsed["rows"],qualify)
        result["tours"][tour]={"sha256":hashlib.sha256(raw).hexdigest(),"raw":len(original),"parsed":len(parsed["rows"]),"statistically_usable":accepted,"rejections":[{"surface":s,"reason":r,"count":n} for (s,r),n in sorted(rejected.items())],"audit":a}
        if a["status"]!="PASS" or len(original)!=accepted+sum(rejected.values()):raise RuntimeError("audit/accounting")
    Path("tennis-audit.json").write_text(json.dumps(result,indent=2))
if __name__=="__main__":run()
