import csv,io,json,hashlib
from datetime import datetime,timezone
from urllib.request import urlopen
URL="https://raw.githubusercontent.com/oladeeayo/open-matchday/master/data/ENG_1_premier-league/results_2627.csv"
def inspect(raw):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    rows=list(reader)
    fields=reader.fieldnames or []
    if not fields or len(fields)!=len(set(fields)) or any(None in r for r in rows):raise ValueError("invalid CSV")
    return {"rows":len(rows),"fields":fields,"nonempty":{k:sum(bool((r.get(k) or "").strip()) for r in rows) for k in fields}}
def main():
    report={"engine_access":False,"publication":"BLOCKED_UPSTREAM_RIGHTS_NOT_CONFIRMED","source":URL}
    try:
        with urlopen(URL,timeout=30) as f:raw=f.read(5000001)
        if len(raw)>5000000:raise ValueError("size cap")
        report.update(inspect(raw),sha256=hashlib.sha256(raw).hexdigest(),observed=datetime.now(timezone.utc).isoformat())
    except Exception as e:report["error"]=type(e).__name__
    with open("open-matchday-probe.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps(report))
    return int("error" in report or not report.get("rows"))
if __name__=="__main__":raise SystemExit(main())
