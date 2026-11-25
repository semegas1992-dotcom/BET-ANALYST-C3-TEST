"""Export a deterministic synthetic report and explicit audit scope."""
import json
from pathlib import Path
from kraft_report import build_report
from test_d0_pipeline_demo import fixture
def main():
    d=fixture()
    report=build_report(d)
    assert report==build_report(d)
    assert report["p2_pass"] and not report["engine_access"]
    assert len(report["sections"])==7 and len(report["evidence"])==16
    assert report["sections"][-1]["decision"]=="ABSTENTION"
    Path("kraft-synthetic-report.json").write_text(json.dumps({"input":d,"report":report,"scope":"technical synthetic only"},ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
