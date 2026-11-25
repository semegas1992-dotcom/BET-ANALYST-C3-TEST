"""Mapping manifest validation only; no admission or source extraction."""
from datetime import datetime
from d0_contract import digest

def stamp(s):
    t=datetime.fromisoformat(s.replace('Z','+00:00'))
    if t.tzinfo is None: raise ValueError('timezone')
    return t

def validate(manifest):
    cutoff=stamp(manifest['cutoff']); targets=set()
    for row in manifest['mappings']:
        for key in ('source_pointer','target','type','unit','record_id','transformation','missing_policy'):
            if not isinstance(row[key],str) or not row[key].strip(): raise ValueError(key)
        if not row['source_pointer'].startswith('/') or row['target'] in targets: raise ValueError('mapping')
        targets.add(row['target'])
        if not stamp(row['event_end'])<=stamp(row['available_at'])<=stamp(row['captured_at'])<=cutoff: raise ValueError('temporal leakage')
    return {'manifest_sha256':digest(manifest),'status':'QUARANTINE_UNVERIFIED','engine_access':False,'qualification':'BLOCKED'}
