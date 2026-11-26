"""Experimental synthetic-only snapshot receipt; never admits data to C4."""
import json
from c4_t01_receipt import receive


def quarantine_snapshot(raw, expected_sha256, *, origin):
    if origin != 'synthetic':
        raise ValueError('synthetic origin required')
    receipt = receive(raw, expected_sha256)
    snapshot = json.loads(raw)
    if snapshot.get('schema') != 'BET_ANALYST_MATCH_SNAPSHOT_V1' or snapshot.get('status') != 'RECEIVED_UNVERIFIED':
        raise ValueError('snapshot schema/status')
    if not isinstance(snapshot.get('matches'), list):
        raise ValueError('matches required')
    return receipt
