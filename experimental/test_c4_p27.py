import json
import unittest
from pathlib import Path
from unittest.mock import patch
from copy import deepcopy
from d0_contract import digest
from c4_frozen_registry import verify,REGISTRY_PATH

class P27Tests(unittest.TestCase):
    def test_frozen(self):
        root=Path(__file__).parent
        oracle=json.loads((root/"p27_expected.json").read_text())
        a,b=json.loads((root/"p27_dossiers.json").read_text())
        for case,expected in oracle["cases"].items():
            with self.subTest(case=case):
                d=deepcopy(a); key=a["id"]
                if case=="replay": self.assertEqual(verify(key,d),verify(key,d))
                if case=="substitution": d=deepcopy(b)
                if case in ("alteration","rehashed"): d["payload"]["bounds"]=[0,1]
                if case=="rehashed": d["sha256"]=digest(d)
                if case=="unknown": key="UNKNOWN";d["id"]=key
                if case=="missing": del d["payload"]
                if case=="malformed": d=None
                if case=="registry_altered":
                    r=json.loads(REGISTRY_PATH.read_text());r["entries"][key]="0"*64
                    with patch("c4_frozen_registry.REGISTRY_PATH") as path:
                        path.read_text.return_value=json.dumps(r)
                        actual=verify(key,d)
                else: actual=verify(key,d)
                print("P27",case,expected,actual["state"],flush=True)
                self.assertEqual(actual["state"],expected)
                self.assertIs(actual["engine_access"],False)
                self.assertIs(actual["predictive_validity_verified"],False)
                self.assertEqual(actual["publication"],"BLOCKED")
                self.assertEqual(actual["qualification"],"BLOCKED")
