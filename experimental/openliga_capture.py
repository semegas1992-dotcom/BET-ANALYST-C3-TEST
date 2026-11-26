"""OpenLigaDB prospective capture; never admits data to the engine."""
import hashlib,json
from datetime import datetime,timezone
from urllib.request import urlopen,Request
from d0_contract import stamp
from c4_quarantine import inspect
BASE="https://api.openligadb.de/getmatchdata/bl1/"
def capture(season,cutoff,fetch=None,clock=None):
    if type(season) is not int or not 2000<=season<=2100: raise ValueError("season")
    clock=clock or (lambda:datetime.now(timezone.utc))
    limit=stamp(cutoff)
    if clock()>=limit: raise ValueError("cutoff passed")
    url=BASE+str(season)
    if fetch is None:
        def fetch(url):
            with urlopen(Request(url,headers={"Accept":"application/json"}),timeout=30) as response:
                return response.read(5000001)
    raw=fetch(url)
    captured=clock()
    if captured>limit: raise ValueError("late capture")
    if not isinstance(raw,bytes) or not 0<len(raw)<=5000000: raise ValueError("size")
    rows=json.loads(raw)
    if not isinstance(rows,list): raise ValueError("schema")
    ids=set(); upcoming=[]
    for row in rows:
        ident=row["matchID"]
        if type(ident) is not int or ident in ids: raise ValueError("identity")
        ids.add(ident)
        kickoff=stamp(row["matchDateTimeUTC"])
        if row.get("matchIsFinished") is False and kickoff>limit:
            upcoming.append({"id":ident,"kickoff":kickoff.isoformat()})
    sha=hashlib.sha256(raw).hexdigest()
    manifest={"cutoff":cutoff,"sources":[{"url":url,"rights":"unverified","available_at":None,"captured_at":captured.isoformat()}]}
    return raw,{"source":"OpenLigaDB","license_claim":"ODbL-1.0","license_url":"https://www.openligadb.de/en/license","sha256":sha,"captured_at":captured.isoformat(),"cutoff":cutoff,"upcoming":upcoming,"quarantine":inspect(raw,sha,manifest),"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
