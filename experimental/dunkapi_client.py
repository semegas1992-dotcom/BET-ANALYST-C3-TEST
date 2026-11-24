"""Experimental, manual-only DunkAPI adapter. No odds or engine access."""
import json, sqlite3, urllib.request, uuid
from datetime import datetime, timezone, date
from urllib.error import HTTPError

BASE="https://mcp.dunkapi.com/v1/"
COST={"get_injuries":2,"get_player":5,"search_players":1,"list_teams":1}

def season_end(bdl_start):
    if type(bdl_start) is not int or not 2000<=bdl_start<=2100:
        raise ValueError("invalid season")
    return bdl_start+1

class Budget:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS charges (day TEXT, cost INTEGER)")
        self.db.commit()
    def reserve(self,cost,today):
        if type(cost) is not int or cost<=0: raise ValueError("invalid cost")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            # Rolling 31-day conservative cap, not provider billing-cycle balance.
            used=self.db.execute("SELECT COALESCE(SUM(cost),0) FROM charges WHERE day>=date(?, '-30 days')",(today.isoformat(),)).fetchone()[0]
            if used+cost>392: raise ValueError("local credit cap")
            self.db.execute("INSERT INTO charges VALUES (?,?)",(today.isoformat(),cost))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise

def validate(endpoint,params,data):
    if not isinstance(data,dict): raise ValueError("invalid response")
    if endpoint=="get_injuries":
        day=date.fromisoformat(data["date"])
        requested=date.fromisoformat(params["date"])
        if day>requested: raise ValueError("future snapshot")
        items=data["injuries"]
        if not isinstance(items,list) or type(data["count"]) is not int or len(items)!=data["count"] or any(not isinstance(x,dict) for x in items):
            raise ValueError("invalid injury count")
        return {"snapshot_date":day.isoformat(),"requested_date":requested.isoformat(),"reported_count":len(items),"freshness":"SAME_DAY_TIME_UNVERIFIED" if day==requested else "OLDER_SNAPSHOT","unlisted_availability":"UNKNOWN","publication_time":"UNKNOWN"}
    # Player and reference schemas need authenticated qualification.
    return {"schema_status":"PENDING_AUTHENTICATED_QUALIFICATION"}

def call(endpoint,params,key,budget,transport=urllib.request.urlopen,now=None,inspect=None):
    if endpoint not in COST: raise ValueError("endpoint not allowed")
    if not key: raise ValueError("missing key")
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None: raise ValueError("timezone required")
    now=now.astimezone(timezone.utc)
    params=dict(params)
    if params.get("league","nba")!="nba": raise ValueError("NBA only")
    params["league"]="nba"
    if endpoint=="get_injuries":
        params.setdefault("date",now.date().isoformat())
        if date.fromisoformat(params["date"])>now.date(): raise ValueError("future request")
    if endpoint=="get_player" and not isinstance(params.get("player_id"),str): raise ValueError("player id required")
    budget.reserve(COST[endpoint],now.date())
    req=urllib.request.Request(BASE+endpoint,data=json.dumps(params).encode(),headers={"Content-Type":"application/json","x-api-key":key,"x-idempotency-key":str(uuid.uuid4())},method="POST")
    # No automatic retry: charge uncertainty remains reserved.
    with transport(req,timeout=30) as res:
        envelope=json.load(res)
    summary=validate(endpoint,params,envelope["data"])
    if inspect is not None:summary.update(inspect(envelope["data"]))
    return {"source":"DunkAPI","endpoint":endpoint,"retrieved_at":now.isoformat(),"credits_reserved":COST[endpoint],"summary":summary,"engine_access":False,"publication":"BLOCKED_RIGHTS_NOT_CONFIRMED","status":"QUARANTINE_UNVERIFIED"}
