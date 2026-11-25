from football_crosscheck import name

# Explicit identities observed in C3.860 missing-name diagnostics.
GROUPS={
"PL":[("Manchester United FC","Man United","Man Utd"),("Tottenham Hotspur FC","Tottenham","Spurs"),("Nottingham Forest FC","Nottingham","Nott'm Forest"),("Brighton & Hove Albion FC","Brighton Hove","Brighton"),("Coventry City FC","Coventry City","Coventry"),("Hull City AFC","Hull City","Hull"),("Ipswich Town FC","Ipswich Town","Ipswich"),("Leeds United FC","Leeds United","Leeds")],
"FL1":[("Lille OSC","Lille","LOSC Lille"),("Le Havre AC","Le Havre","Havre Athletic Club"),("ES Troyes AC","Troyes","Estac Troyes"),("AS Monaco FC","Monaco","AS Monaco"),("Stade Rennais FC 1901","Stade Rennais","Stade Rennais FC"),("Paris Saint-Germain FC","PSG","Paris Saint-Germain")]
}
# C3.874: explicit league-scoped residual aliases, subject to exact date and score checks.
GROUPS.update({
"BL1":[("TSG 1899 Hoffenheim","TSG Hoffenheim")],
"SA":[("FC Internazionale Milano","Internazionale"),("Como 1907","Como")],
"PD":[("Real Racing Club de Santander","R. Racing Club"),("RC Deportivo La Coruña","RC Deportivo")]
})
GROUPS["PD"].append(("Club Atlético de Madrid","Atlético de Madrid"))
GROUPS["SA"].append(("Venezia FC","Venezia"))
def identity(code,value):
    n=name(value)
    for group in GROUPS.get(code,[]):
        if n in {name(v) for v in group}:return name(group[0])
    return n
