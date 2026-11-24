def distribution(rows):
    n=len(rows)
    totals=[r["gf"]+r["ga"] for r in rows]
    return {"n":n,"btts":sum(r["gf"]>0 and r["ga"]>0 for r in rows),"over_1_5":sum(t>1.5 for t in totals),"over_2_5":sum(t>2.5 for t in totals),"over_3_5":sum(t>3.5 for t in totals),"clean_sheets":sum(r["ga"]==0 for r in rows),"failed_to_score":sum(r["gf"]==0 for r in rows),"total_histogram":{str(t):totals.count(t) for t in sorted(set(totals))},"interpretation":"DESCRIPTIVE_NOT_PROBABILITY"}

def halves(rows):
    valid=[r for r in rows if r.get("ht_gf") is not None and r.get("ht_ga") is not None]
    n=len(valid)
    return {"n":n,"eligible":len(rows),"coverage":n/len(rows) if rows else None,"first_half_gf":sum(r["ht_gf"] for r in valid)/n if n else None,"first_half_ga":sum(r["ht_ga"] for r in valid)/n if n else None,"second_half_gf":sum(r["gf"]-r["ht_gf"] for r in valid)/n if n else None,"second_half_ga":sum(r["ga"]-r["ht_ga"] for r in valid)/n if n else None}

def enrich(rows,opponent):
    return {"season":distribution(rows),"last5":distribution(rows[:5]),"last10":distribution(rows[:10]),"halves":halves(rows),"h2h":{"scope":"SAME_COMPETITION_SEASON_ONLY","rows":[r for r in rows if r.get("opponent")==opponent]},"sample":{"n":len(rows),"last5_complete":len(rows)>=5,"last10_complete":len(rows)>=10,"external_completeness":"NOT_VERIFIED"}}
