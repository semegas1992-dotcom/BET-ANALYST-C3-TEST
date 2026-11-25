"""Synthetic family coverage inventory, no selection or sporting recommendation."""
FAMILIES={"football":("result","double_chance","goal_handicap","match_goals","team_goals","both_score","period","scorers","assists"),"nba":("result","handicap","match_total","team_total","period_total","individual"),"tennis":("result","set_winner","set_count","game_handicap","set_handicap","match_total","player_total","set_total","tiebreak","breaks","aces","double_faults")}
def inventory(sport):
    if sport not in FAMILIES:raise ValueError("sport")
    return {"sport":sport,"families":[{"family":f,"status":"NOT_EVALUATED","reason":"No validated opposition-adjusted event model or matching evidence"} for f in FAMILIES[sport]],"engine_access":False,"publication":"BLOCKED","qualification":"BLOCKED"}
