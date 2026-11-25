import hashlib,json,zipfile,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SPECS=[
("football",14994825927,"1eb7da40c7aba1d766fe85fe58ddc9851e09437ff8c8bdc3a78433075d098fcd","football-d0-enriched.json"),
("nba",15000318977,"d8466bf0e79ea05752d61b613ef47353cdaf71585ef948efc8b2cbc41f9d1088","nba-batch-quarantine.json"),
("tennis",15000561579,"e384cbfb87eda062228331f6771f92fc79e745cf8b1097dac4c1ff032db3bdf0","tennis-d0.json")]
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return sha(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def require(ok,msg):
    if not ok:raise ValueError(msg)
def run(folder):
    report=[]
    for sport,aid,expected,name in SPECS:
        path=folder/f"github-actions-artifact-{aid}.zip"
        require(sha(path.read_bytes())==expected,"ZIP_HASH "+sport)
        with zipfile.ZipFile(path) as z:
            if sport=="tennis":
                names=[n for n in z.namelist() if n.endswith(".json")]
                require(len(names)==1,"TENNIS_FILE")
                name=names[0]
            raw=z.read(name)
            d=json.loads(raw)
            checks=[]
            if sport=="tennis":
                o=d["output"];i=d["input"]
                require(canonical(i)==o["input_sha256"],"INPUT_HASH")
                require(canonical({k:v for k,v in o.items() if k!="sha256"})==o["sha256"],"OUTPUT_HASH")
                require(len(i["observations"])==len(o["evidence"]),"EVIDENCE_COUNT")
                for r,e in zip(i["observations"],o["evidence"]):
                    require(canonical(r)==e["sha256"],"EVIDENCE_HASH")
                checks=["input","output","evidence"]
            if sport=="nba":
                a=json.loads(z.read("nba-independent-audit.json"))
                require(canonical(d)==a["input_sha256"],"NBA_AUDIT_HASH")
                checks=["independent_audit_input"]
        p=subprocess.run(["node",str(ROOT/"replay-native.cjs"),sha(raw)],input=raw,capture_output=True,check=True)
        preview=json.loads(p.stdout)
        require(preview["sport"]==sport and preview["engine_access"] is False and preview["publication"]=="BLOCKED","PREVIEW")
        report.append({"sport":sport,"artifact":aid,"zip_sha256":expected,"file_sha256":sha(raw),"internal_checks":checks,"preview":preview})
    return {"status":"PASS","scope":"quarantine only; football upstream hashes not independently recomputed","imports":report}
if __name__=="__main__":
    print(json.dumps(run(Path(sys.argv[1])),indent=2,sort_keys=True))
