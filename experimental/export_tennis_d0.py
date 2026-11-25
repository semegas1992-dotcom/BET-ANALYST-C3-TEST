import json
from pathlib import Path
from tennis_d0 import build
from test_tennis_d0 import TennisD0Tests
from d0_contract import digest
if __name__=="__main__":
    d=TennisD0Tests().fixture()
    a=build(d);b=build(json.loads(json.dumps(d)))
    assert a==b
    assert a["sha256"]==digest({k:v for k,v in a.items() if k!="sha256"})
    Path("tennis-d0-demo.json").write_text(json.dumps({"input":d,"output":a},sort_keys=True,indent=2)+"\n")
