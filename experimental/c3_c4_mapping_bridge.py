"""Validate a synthetic mapping manifest against a quarantined C3 snapshot."""
import json
from c3_c4_bridge import quarantine_snapshot
from c4_t01_mapping import validate


def inspect_mapping(raw, expected_sha256, manifest, *, origin):
    receipt = quarantine_snapshot(raw, expected_sha256, origin=origin)
    snapshot = json.loads(raw)
    if not manifest['mappings']:
        raise ValueError('empty mapping')
    mapping = validate(manifest)
    for row in manifest['mappings']:
        value = snapshot
        for part in row['source_pointer'].split('/')[1:]:
            part = part.replace('~1', '/').replace('~0', '~')
            if isinstance(value, list):
                if not part.isascii() or not part.isdecimal() or str(int(part)) != part:
                    raise ValueError('invalid array pointer')
                value = value[int(part)]
            else:
                value = value[part]
        if value is None:
            raise ValueError('missing source value')
    return {'receipt': receipt, 'mapping': mapping, 'engine_access': False,
            'qualification': 'BLOCKED', 'publication': 'BLOCKED'}
