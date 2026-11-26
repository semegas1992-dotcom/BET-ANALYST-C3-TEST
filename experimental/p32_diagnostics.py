"""Browser diagnostic wrapper; never alters the registry or admission result."""
import sys, json
from pathlib import Path
from d0_contract import digest
from c4_registered_replay import REGISTRY_PATH, REGISTRY_SHA256
from p32_dynamic import generate_registered

def browser_generate(sport):
    trace=[]
    def tracer(frame,event,arg):
        name=Path(frame.f_code.co_filename).name
        if name in ("c4_registered_replay.py","c4_event_conditional.py"):
            if event=="return":
                trace.append((name,frame.f_lineno,str(arg)[:300]))
            elif event=="exception":
                trace.append((name,frame.f_lineno,str(arg[1])[:300]))
            return tracer
        return None
    previous=sys.gettrace()
    sys.settrace(tracer)
    try:
        return generate_registered(sport)
    except ValueError as exc:
        registry=json.loads(REGISTRY_PATH.read_text())
        dossiers=json.loads(REGISTRY_PATH.with_name("p27c_dossiers.json").read_text())
        d=next(x for x in dossiers if x["payload"]["d"]["sport"]==sport)
        raise ValueError(json.dumps(dict(error=str(exc),python=sys.version,registry_match=digest(registry)==REGISTRY_SHA256,dossier_match=registry["entries"].get(d["id"])==digest(d),trace=trace))) from exc
    finally:
        sys.settrace(previous)
