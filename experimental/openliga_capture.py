"""OpenLigaDB prospective capture; never admits data to the engine."""
import hashlib,json,time,os
from pathlib import Path
from urllib.error import HTTPError
from datetime import datetime,timezone
from urllib.request import urlopen,Request
from d0_contract import stamp
from c4_quarantine import inspect
BASE="https://api.openligadb.de/getmatchdata/bl1/"
def capture(season,cutoff,fetch=None,clock=None,cache_dir=None):
    if type(season) is not int or not 2000<=season<=2100: raise ValueError("season")
    clock=clock or (lambda:datetime.now(timezone.utc))
    limit=stamp(cutoff)
    if clock()>=limit: raise ValueError("cutoff passed")
    url=BASE+str(season)
    if fetch is None:
        def fetch(url):
            agent=os.environ.get("OPENLIGA_USER_AGENT")
            if not agent or "BET-ANALYST" not in agent: raise ValueError("contact user agent required")
            for attempt in range(3):
                try:
                    with urlopen(Request(url,headers={"Accept":"application/json","User-Agent":agent}),timeout=30) as response:
                        return response.read(5000001)
                except HTTPError as exc:
                    if (exc.code!=429 and not 500<=exc.code<600) or attempt==2: raise
                    time.sleep(60*2**attempt)
    cache=Path(cache_dir)/("bl1-"+str(season)+".json") if cache_dir else None
    if cache and cache.exists():
        saved=json.loads(cache.read_text())
        captured=stamp(saved["captured_at"])
        raw=bytes.fromhex(saved["raw_hex"])
        if hashlib.sha256(raw).hexdigest()!=saved["sha256"]: raise ValueError("cache integrity")
        if captured>clock(): raise ValueError("future cache")
    else:
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
    if cache and not cache.exists():
        cache.parent.mkdir(parents=True,exist_ok=True)
        with cache.open("x") as f:
            json.dump({"captured_at":captured.isoformat(),"raw_hex":raw.hex(),"sha256":sha},f)
    manifest={"cutoff":cutoff,"sources":[{"url":url,"rights":"unverified","available_at":None,"captured_at":captured.isoformat()}]}
    return raw,{"source":"OpenLigaDB","license_claim":"ODbL-1.0","license_url":"https://www.openligadb.de/en/license","sha256":sha,"captured_at":captured.isoformat(),"cutoff":cutoff,"upcoming":upcoming,"quarantine":inspect(raw,sha,manifest),"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
