from d0_contract import digest
def build(dependencies, trajectories):
    mechanisms=dependencies['mechanisms']
    rows=[]
    for row in trajectories['trajectories']:
        if set(row['assignment'])!=set(mechanisms): raise ValueError('mechanism coverage')
        links=[]
        for mid,state in sorted(row['assignment'].items()):
            if state not in ('holds','fails'): raise ValueError('state')
            m=mechanisms[mid]
            links.append(dict(mechanism_id=mid,condition_state=state,issues=m['issues'],record_ids=m['record_ids'],status='UNVERIFIED'))
        rows.append(dict(assignment=row['assignment'],links=links,global_issues=row['issues']))
    return dict(dependency_sha256=digest(dependencies),trajectory_sha256=digest(trajectories),rows=rows,qualification='BLOCKED')
