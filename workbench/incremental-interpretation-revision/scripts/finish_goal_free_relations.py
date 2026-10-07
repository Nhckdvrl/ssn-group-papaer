"""E67 complete generation, blind T4-v2, then full-scope scientific map."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from data import sha


def main(a):
    root=a.root;script=Path(__file__).parent;names=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'];runs=[root/'runs-v2'/n for n in names];last=None;start=time.monotonic()
    while True:
        complete=[]
        for r in runs:
            try:
                x=json.loads((r/'config.json').read_text());ok=x.get('predictions_sha256')==sha(r/'predictions.jsonl')
            except (OSError,json.JSONDecodeError):ok=False
            complete.append(ok)
        if complete!=last:print('E67 complete generation',dict(zip(names,complete)),flush=True);last=complete
        if all(complete):break
        if time.monotonic()-start>43200:raise RuntimeError('Inspect unfinished generator logs; do not interpret partial outcomes.')
        time.sleep(10)
    audits=[root/'T4-full-v2'];previous=[]
    # Reuse a completed, corrected pool only if available now, by exact packet SHA.
    e64=root.parent/'E64/T4-full-v2'
    if (e64/'step5/summary.json').exists():previous=[e64,root.parent/'E64/legacy-non-MVRR-v1']
    cmd=[sys.executable,str(script/'audit_paraphrases_role_v2.py'),'--data',str(root/'sources-v1.jsonl'),'--runs',*map(str,runs),'--out',str(audits[0]),'--workers','4']
    if previous:cmd+=['--previous-audits',*map(str,previous)]
    subprocess.run(cmd,check=True)
    out=root/'goal-to-free-role-map-v1.json'
    subprocess.run([sys.executable,str(script/'analyze_goal_free_relations.py'),'--sources',str(root/'sources-v1.jsonl'),'--runs',*map(str,runs),'--audits',*map(str,audits+previous),'--qa-root',str(root.parent/'E65/runs-v1'),'--out',str(out)],check=True)
    (root/'complete-map-v1.json').write_text(json.dumps(dict(path=str(out),sha256=sha(out)),indent=2)+'\n');print('E67 complete blind map ready',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args())
