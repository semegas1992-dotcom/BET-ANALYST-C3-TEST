"""Sport-specific observation prompts, never evidence or predictions."""
from d0_contract import digest
PROMPTS={"football":["opening pressing and progression","midmatch chance creation and transitions","late game-state changes"],"nba":["opening pace and shot profile","rotation and possession changes","late lineup and foul context"],"tennis":["opening service and return patterns","set-level adaptation","late service stability"]}
def build(sport, trajectories):
    return {"sport":sport,"trajectory_sha256":digest(trajectories),"rows":[{"assignment":r["assignment"],"issues":r["issues"],"prompts":PROMPTS[sport][:],"status":"UNVERIFIED","estimate":None} for r in trajectories["trajectories"]],"dominant":None,"qualification":"BLOCKED"}
