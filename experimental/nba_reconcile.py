from datetime import date

def compare(a,b):
    fields=('date','home','away','home_score','away_score','home_periods','away_periods')
    def valid(r):
        if not isinstance(r,dict) or any(r.get(k) is None for k in fields): return False
        try: date.fromisoformat(r['date'])
        except (ValueError,TypeError): return False
        if any(not isinstance(r[k],str) or not r[k].strip() for k in ('home','away')) or r['home']==r['away']: return False
        h,v=r['home_periods'],r['away_periods']
        if not isinstance(h,list) or not isinstance(v,list) or len(h)!=len(v) or len(h)<4: return False
        if any(type(x)!=int or x<0 for x in h+v): return False
        return all(type(r[k])==int for k in ('home_score','away_score')) and sum(h)==r['home_score'] and sum(v)==r['away_score'] and sum(h)!=sum(v) and all(sum(h[:n])==sum(v[:n]) for n in range(4,len(h)))
    diffs=[k for k in fields if a.get(k)!=b.get(k)] if isinstance(a,dict) and isinstance(b,dict) else []
    return {'status':('MATCH' if not diffs else 'DIVERGENCE') if valid(a) and valid(b) else 'INCOMPLETE_OR_INVALID','differences':diffs,'engine_access':False,'publication':'BLOCKED','qualification':'BLOCKED'}
