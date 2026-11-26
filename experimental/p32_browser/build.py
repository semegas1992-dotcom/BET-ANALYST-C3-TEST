import json, shutil, zipfile, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]).resolve()
runtime=Path(sys.argv[2]).resolve()
out.mkdir(parents=True,exist_ok=True)
for name in ('index.html','app.js','worker.js','sw.js'):
    shutil.copy2(Path(__file__).with_name(name),out/name)
shutil.copytree(runtime,out/'runtime',dirs_exist_ok=True)
with zipfile.ZipFile(out/'engine.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(root.glob('*.py')):
        z.write(p,p.name)
    for name in ('p27c_registry.json','p27c_dossiers.json'):
        z.write(root/name,name)
assets=[p.relative_to(out).as_posix() for p in sorted(out.rglob('*')) if p.is_file() and p.name!='assets.json']
(out/'assets.json').write_text(json.dumps(assets))
