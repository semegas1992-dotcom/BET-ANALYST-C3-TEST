"""On-demand synthetic report generation; no real admission or sporting qualification."""
import json
from pathlib import Path
from c4_registered_replay import replay
from c4_integrated import run
from c4_report import render
from d0_contract import digest
from test_c4_integrated import IntegratedTests

def generate(sport, dossier):
    if sport not in ("football", "nba", "tennis"):
        raise ValueError("Unsupported sport")
    verdict = replay(dossier.get("id"), dossier)
    if verdict.get("state") != "ABOVE" or verdict.get("engine_access") is not False or verdict.get("publication") != "BLOCKED" or verdict.get("qualification") != "BLOCKED":
        raise ValueError("Synthetic registry gate rejected")
    d = dossier["payload"]["d"]
    if d["sport"] != sport:
        raise ValueError("Sport mismatch")
    extra = {k: [] for k in ("observations","configurations","comparables","indicators","sequences")}
    report = render(run(d, IntegratedTests().case(d), [], ["identity"], [1], "fixture", {}, 1, 1, {}, [], extra))
    if report["input_sha256"] != digest(d) or report["engine_access"] is not False or report["publication"] != "BLOCKED" or report["qualification"] != "BLOCKED":
        raise ValueError("Report gate rejected")
    return dict(scope="DYNAMIC_REGISTERED_SYNTHETIC", report=report, registered_result=verdict, dossier_sha256=digest(dossier))

def generate_registered(sport):
    dossiers = json.loads(Path(__file__).with_name("p27c_dossiers.json").read_text())
    matches = [d for d in dossiers if d["payload"]["d"]["sport"] == sport]
    if len(matches) != 1:
        raise ValueError("No unique registered dossier")
    return generate(sport, matches[0])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("sport", choices=["football","nba","tennis"])
    args = parser.parse_args()
    print(json.dumps(generate_registered(args.sport), ensure_ascii=False))
