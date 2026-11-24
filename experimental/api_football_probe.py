import os,json,time
from urllib.request import Request,urlopen
from urllib.parse import urlencode
def call(path,params,key):
    with urlopen(Request("https://v3.football.api-sports.io/"+path+"?"+urlencode(params),headers={"x-apisports-key":key}),timeout=25) as r:
        d=json.load(r)
    if d.get("errors"):return {"status":"API_ERROR","error_fields":list(d["errors"]) if isinstance(d["errors"],dict) else []},[]
    rows=d.get("response")
    if not isinstance(rows,list):raise ValueError("response shape")
    return {"status":"OK","count":len(rows),"fields":sorted(rows[0]) if rows and isinstance(rows[0],dict) else []},rows
def main():
    key=os.environ.get("API_FOOTBALL_KEY")
    report={"engine_access":False,"publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","calls":{}}
    try:
        if not key:raise ValueError("missing key")
        meta,rows=call("leagues",{"id":39},key)
        report["calls"]["leagues"]=meta
        seasons=[s for row in rows for s in row.get("seasons",[]) if s.get("current")]
        report["current_seasons"]=[{"year":s.get("year"),"coverage":s.get("coverage")} for s in seasons]
        time.sleep(7)
        meta,rows=call("fixtures",{"league":39,"season":2026,"next":1},key)
        report["calls"]["fixtures"]=meta
        if rows:
            fid=rows[0]["fixture"]["id"]
            for endpoint in ("injuries","fixtures/lineups"):
                time.sleep(7)
                meta,_=call(endpoint,{"fixture":fid},key)
                report["calls"][endpoint]=meta
        time.sleep(7)
        meta,rows=call("fixtures",{"league":39,"season":2025,"last":1},key)
        report["calls"]["historical_fixture"]=meta
        if rows:
            fid=rows[0]["fixture"]["id"]
            for endpoint in ("fixtures/statistics","fixtures/players"):
                time.sleep(7)
                meta,_=call(endpoint,{"fixture":fid},key)
                report["calls"][endpoint]=meta
    except Exception as e:report["error"]=type(e).__name__;report["http_code"]=getattr(e,"code",None)
    with open("api-football-probe.json","w") as f:json.dump(report,f,indent=2)
    print(json.dumps(report))
    return int("error" in report or any(v["status"]!="OK" for v in report["calls"].values()))
if __name__=="__main__":raise SystemExit(main())
