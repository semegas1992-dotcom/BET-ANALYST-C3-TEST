"""Supplemental dependency routing; never a market validation."""
from d0_contract import digest
def route(event, review, trajectories, markets):
    rows=[]
    for market in markets:
        c=market["contract"]
        family,subject=c["family"],c["subject"]
        links=[]
        for dep in review["dependencies"]:
            direct=subject==dep["person_id"]
            if direct or family in dep["families_to_review"]:
                links.append({"person_id":dep["person_id"],"participant":dep["participant"],"role":dep["role"],"record_ids":dep["record_ids"],"reason":"DIRECT_SUBJECT" if direct else "POTENTIAL_ROLE_DEPENDENCY","effect":None})
        rows.append({"contract":c,"dependencies":links,"documentary_sufficiency":"NOT_ESTABLISHED","roster_robustness":"NOT_ESTABLISHED","status":"NOT_EVALUATED"})
    return {"event_sha256":digest(event),"review_sha256":digest(review),"trajectory_sha256":digest(trajectories),"markets":rows,"qualification":"BLOCKED"}
