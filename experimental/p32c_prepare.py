"""Prepare input-only P32C packets. Never generate or expose branch A output."""
import json, hashlib, sys
from pathlib import Path
from d0_contract import digest, validate
from c4_registered_replay import REGISTRY_PATH, REGISTRY_SHA256
ROOT=Path(__file__).parent
def prepare(out):
    registry=json.loads(REGISTRY_PATH.read_text())
    if digest(registry)!=REGISTRY_SHA256: raise ValueError("registry mismatch")
    dossiers=json.loads((ROOT/"p27c_dossiers.json").read_text())
    ref=(ROOT/"KRAFT_V3_REFERENCE.txt").read_bytes()
    manifest={"registry_sha256":REGISTRY_SHA256,"kraft_file_sha256":hashlib.sha256(ref).hexdigest(),"application_commit":"f8e62500d628fe897d68f1039d8187d514c96032","cases":[]}
    if len(dossiers)!=3 or {x["id"] for x in dossiers}!=set(registry["entries"]): raise ValueError("case set")
    for sport in ("football","nba","tennis"):
        case=next(x for x in dossiers if x["id"]=="P27C-"+sport)
        if digest(case)!=registry["entries"][case["id"]] or case["origin"]!="synthetic" or case["engine_access"] is not False: raise ValueError("dossier gate")
        d=case["payload"]["d"]
        if d["sport"]!=sport: raise ValueError("sport")
        entry={"id":case["id"],"sport":sport,"dossier_sha256":digest(case),"d0_sha256":validate(d)}
        manifest["cases"].append(entry)
        folder=out/"branch-b"/sport
        folder.mkdir(parents=True,exist_ok=True)
        (folder/"D0.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
        (folder/"KRAFT_V3_REFERENCE.txt").write_bytes(ref)
        (folder/"manifest.json").write_text(json.dumps(entry,indent=2))
        (folder/"MISSION.txt").write_text("Analyse independently using only D0.json and unchanged KRAFT reference. No external research, odds, results, other branch or dossier payload. Distinguish facts, hypotheses and missing information. Preserve synthetic locks and no sporting conclusion. Seven sections. Freeze report before comparison. Do not infer predictive validity.")
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2))
    print("P32C_INPUTS_FROZEN",json.dumps(manifest))
if __name__=="__main__": prepare(Path(sys.argv[1]))
