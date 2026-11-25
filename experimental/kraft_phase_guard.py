"""Pre-odds synthetic report guard; not a predictive model."""
FOOTBALL_FAMILIES=frozenset(("result","double_chance","goal_handicap","match_goals","team_goals","both_score","period","scorer","assister"))
FORBIDDEN=frozenset(("odds","value","stake","ticket","parlay","profitability","simulation","probabilities"))
def validate_market(family):
    if family not in FOOTBALL_FAMILIES:raise ValueError("outside KRAFT football scope")
def validate_phase(report):
    def walk(v):
        if isinstance(v,dict):
            for k,x in v.items():
                if k in FORBIDDEN:raise ValueError("outside synthetic pre-odds scope")
                walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    walk(report)
    if report.get("engine_access") is not False:raise ValueError("quarantine")
    for m in report.get("markets",[]):validate_market(m["family"])
    return report
