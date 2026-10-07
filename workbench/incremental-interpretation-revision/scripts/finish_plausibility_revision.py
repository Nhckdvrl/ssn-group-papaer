"""Analyze E69 only after all registered family outputs close and hash-match."""
import json
from pathlib import Path
import subprocess
import sys
import time
from data import sha

root=Path(sys.argv[1]);names=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'];runs=[root/'runs-v1'/n for n in names];last=None
while True:
    ready=[]
    for p in runs:
        try:c=json.loads((p/'config.json').read_text());ok=c.get('predictions_sha256')==sha(p/'predictions.jsonl')
        except (OSError,json.JSONDecodeError):ok=False
        ready.append(ok)
    if ready!=last:print('E69 complete panel',dict(zip(names,ready)),flush=True);last=ready
    if all(ready):break
    time.sleep(10)
out=root/'plausibility-structure-map-v1.json'
subprocess.run([sys.executable,str(Path(__file__).with_name('plausibility_revision.py')),'analyze','--data',str(root/'data-v1.jsonl'),'--runs',*map(str,runs),'--out',str(out)],check=True)
(root/'complete-map-v1.json').write_text(json.dumps(dict(path=str(out),sha256=sha(out)),indent=2)+'\n');print('E69 complete map ready',flush=True)
