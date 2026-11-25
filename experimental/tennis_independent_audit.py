"""Independent arithmetic comparison, never admits data to the engine."""
from fractions import Fraction
def audit(rows, qualify):
    issues=[]; checks=0
    for row in rows:
        q=qualify(row)
        for side,opp in (("w","l"),("l","w")):
            if q["service"][side]["status"]!="OK":continue
            s=row["stats"]; total=s[side+"_svpt"]
            losses=(s[side+"_1stIn"]-s[side+"_1stWon"])+(total-s[side+"_1stIn"]-s[side+"_2ndWon"])
            for observed,expected in ((q["service"][side]["won"],total-losses),(q["service"][side]["total"],total),(q["return"][opp]["won"],losses),(q["return"][opp]["total"],total)):
                checks+=1
                if observed!=expected:issues.append(row["id"]+":"+side)
    return {"checks":checks,"issues":issues,"status":"PASS" if checks and not issues else "FAIL","engine_access":False}
