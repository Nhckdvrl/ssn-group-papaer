"""Analyze E65 only when every task of the fixed three-family panel is complete."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from data import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();root=a.root
    names=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'];runs=[root/'runs-v1'/n for n in names];start=time.monotonic();last=None
    while True:
        ready=[]
        for run in runs:
            try:
                c=json.loads((run/'config.json').read_text());complete=c.get('predictions_sha256')==sha(run/'predictions.jsonl')
            except (OSError,json.JSONDecodeError):complete=False
            ready.append(complete)
        if ready!=last:print('E65 fixed panel completion',dict(zip(names,ready)),flush=True);last=ready
        if all(ready):break
        if time.monotonic()-start>14400:raise RuntimeError('E65 full panel unfinished; inspect logs, no partial scientific effects.')
        time.sleep(10)
    out=root/'goal-by-question-map-v1.json'
    subprocess.run([sys.executable,str(Path(__file__).with_name('analyze_goal_conditioned_reading.py')),'--data',str(root/'data-v1.jsonl'),
        '--runs',*map(str,runs),'--out',str(out)],check=True)
    (root/'complete-map-v1.json').write_text(json.dumps(dict(path=str(out),sha256=sha(out),scope='Complete fixed three-goal/four-construction/three-family panel; no role-audit dependency.'),indent=2)+'\n')
    print('E65 full goal-by-question map ready',out,flush=True)


if __name__=='__main__':main()
