import json
from pathlib import Path
from c4_registered_replay import replay
from c4_integrated import run
from c4_report import render
from d0_contract import digest
from test_c4_integrated import IntegratedTests

def export():
    root=Path(__file__).parent
    out={}
    for dossier in json.loads((root/"p27c_dossiers.json").read_text()):
        verdict=replay(dossier["id"],dossier)
        assert verdict["state"]=="ABOVE" and verdict["engine_access"] is False
        d=dossier["payload"]["d"]
        e=IntegratedTests().case(d)
        extra={k:[] for k in ("observations","configurations","comparables","indicators","sequences")}
        report=render(run(d,e,[],["identity"],[1],"fixture",{},1,1,{},[],extra))
        assert report["input_sha256"]==digest(d)
        out[d["sport"]]=dict(report=report,registered_result=verdict,dossier_sha256=digest(dossier),scope="PRECOMPUTED_SYNTHETIC")
    return out

if __name__=="__main__":
    print("P31_EXPORT "+json.dumps(export(),sort_keys=True,separators=(",",":")))
