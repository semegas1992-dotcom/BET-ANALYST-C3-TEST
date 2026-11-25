"""Compare pinned downloads and prior audited totals; fail closed."""
import hashlib,json
from pathlib import Path
EXPECTED={"ATP":("73aec32247a0db68d8aa8fd8003eefea132905177f1cb145502d9215b53311be",3076,2973,2908,23452,{"hard":114,"clay":42,"grass":12}),"WTA":("d9bba2a0b3793f63c737ef62a809b82b56b3ad0ee94e1f95e78cecfac7615ed2",2689,2530,2510,20096,{"hard":82,"clay":23,"grass":17,"unknown":57})}
def verify(report):
    if report["revision"]!="83733587353df8a41f2fd4f516147d5aa83f5a8d" or report["engine_access"] is not False or report["publication"]!="BLOCKED":raise ValueError("lock/revision")
    for tour,(digest,n,p,k,c,surfaces) in EXPECTED.items():
        raw=Path(tour.lower()+".csv").read_bytes()
        second=Path(tour.lower()+".second.csv").read_bytes()
        r=report["tours"][tour]
        if raw!=second or hashlib.sha256(second).hexdigest()!=digest or r["sha256"]!=digest:raise ValueError("digest:"+tour)
        actual={}
        for x in r["rejections"]:
            s=x["surface"]
            if s!=s.lower():raise ValueError("surface")
            actual[s]=actual.get(s,0)+x["count"]
        if (r["raw"],r["parsed"],r["statistically_usable"],r["audit"]["checks"],actual)!=(n,p,k,c,surfaces) or r["audit"]["issues"] or r["audit"]["status"]!="PASS":raise ValueError("regression:"+tour)
    return {"status":"PASS","engine_access":False,"publication":"BLOCKED","revision":report["revision"],"tours":report["tours"]}
if __name__=="__main__":
    Path("tennis-verification.json").write_text(json.dumps(verify(json.loads(Path("tennis-audit.json").read_text())),indent=2))
