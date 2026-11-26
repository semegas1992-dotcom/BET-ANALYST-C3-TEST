import json
import unittest
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
from d0_contract import digest
from c4_registered_replay import replay,REGISTRY_PATH

class P27CIntegration(unittest.TestCase):
    def test_frozen(self):
        root=Path(__file__).parent
        dossiers=json.loads((root/"p27c_dossiers.json").read_text())
        oracle=json.loads((root/"p27c_expected.json").read_text())
        for i,original in enumerate(dossiers):
            for case,expected in oracle.items():
                with self.subTest(id=original["id"],case=case):
                    d=deepcopy(original);key=d["id"]
                    if case=="substitution": d=deepcopy(dossiers[(i+1)%len(dossiers)])
                    if case in ("alteration","rehashed"): d["payload"]["packet"]["scenarios"][0]["bounds"]=[0,1]
                    if case=="rehashed": d["sha256"]=digest(d)
                    if case=="threshold": d["payload"]["threshold"]+=1
                    if case=="registry_altered":
                        r=json.loads(REGISTRY_PATH.read_text());r["entries"][key]="0"*64
                        with patch("c4_registered_replay.REGISTRY_PATH") as path:
                            path.read_text.return_value=json.dumps(r)
                            actual=replay(key,d)
                    else:
                        actual=replay(key,d)
                        if case=="replay": self.assertEqual(actual,replay(key,d))
                    print("P27C",key,case,expected,actual["state"],flush=True)
                    self.assertEqual(actual["state"],expected)
                    self.assertIs(actual["engine_access"],False)
                    self.assertIs(actual["predictive_validity_verified"],False)
                    self.assertEqual(actual["publication"],"BLOCKED")
                    self.assertEqual(actual["qualification"],"BLOCKED")
