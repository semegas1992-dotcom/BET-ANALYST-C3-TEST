import unittest
import json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
from p32_dynamic import generate, generate_registered
from p31_export import export

class P32DynamicTests(unittest.TestCase):
    def test_three_sports_parity(self):
        baseline = export()
        for sport in baseline:
            with self.subTest(sport=sport):
                result = generate_registered(sport)
                self.assertEqual(result["scope"], "DYNAMIC_REGISTERED_SYNTHETIC")
                for key in ("report","registered_result","dossier_sha256"):
                    self.assertEqual(result[key], baseline[sport][key])
    def test_actual_execution(self):
        import p32_dynamic
        with patch("p32_dynamic.run", wraps=p32_dynamic.run) as engine:
            generate_registered("football")
            generate_registered("football")
            self.assertEqual(engine.call_count, 2)
    def test_reject_mutations(self):
        dossiers = json.loads(Path(__file__).with_name("p27c_dossiers.json").read_text())
        for original in dossiers:
            sport = original["payload"]["d"]["sport"]
            for key, value in (("origin","real"),("engine_access",True),("id","unknown")):
                d = deepcopy(original)
                d[key] = value
                with self.assertRaises(ValueError):
                    generate(sport,d)
            with self.assertRaises(ValueError):
                generate("nba" if sport != "nba" else "football",original)
    def test_unknown_sport(self):
        with self.assertRaises(ValueError):
            generate_registered("unknown")
