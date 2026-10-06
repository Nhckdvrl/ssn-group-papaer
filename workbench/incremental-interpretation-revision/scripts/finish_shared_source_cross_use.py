"""Wait for the fixed E63 family panel, then blind-audit and analyze complete outputs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from data import sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--wait-seconds',type=int,default=14400);args=ap.parse_args()
    root=args.root;script=Path(__file__).parent
    names=('Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct');runs=[root/'runs-v1'/name for name in names]
    start=time.monotonic();last=None
    while True:
        ready=[]
        for p in runs:
            cfg=p/'config.json'
            try:
                r=json.loads(cfg.read_text());complete=bool(r.get('predictions_sha256')) and r['predictions_sha256']==sha(p/'predictions.jsonl') and r['qa_predictions_sha256']==sha(p/'qa-predictions.jsonl')
            except (OSError,json.JSONDecodeError,KeyError):complete=False
            ready.append(complete)
        if ready!=last:print('E63 fixed family completion',dict(zip(names,ready)),flush=True);last=ready
        if all(ready):break
        if time.monotonic()-start>args.wait_seconds:raise RuntimeError('E63 family panel unfinished; no partial outcome analysis. Inspect production logs.')
        time.sleep(10)
    previous=[root.parent/'E53/T4-instrument-v2']
    full=root.parent/'E53/T4-full-native-v2'
    if (full/'step5/summary.json').exists():previous.append(full)
    command=[sys.executable,str(script/'audit_paraphrases.py'),'--data',str(root/'sources-v1.jsonl'),'--runs',*map(str,runs),'--out',str(root/'T4-full-v1'),'--workers','4','--previous-audits',*map(str,previous)]
    print('E63 all generation complete; auditing only new distinct source/output packets via existing Step Plan protocol',flush=True)
    subprocess.run(command,check=True)
    out=root/'shared-source-cross-use-map-v1.json'
    subprocess.run([sys.executable,str(script/'analyze_shared_source_cross_use.py'),'--data',str(root/'data-v1.jsonl'),'--sources',str(root/'sources-v1.jsonl'),'--runs',*map(str,runs),'--audits',str(root/'T4-full-v1'),*map(str,previous),'--out',str(out)],check=True)
    (root/'complete-map-v1.json').write_text(json.dumps(dict(full_result_path=str(out),full_result_sha256=sha(out),interpretation='Complete fixed panel and T4 map ready for scientific self-review; no autonomous claim upgrade or winning-cell selection.'),indent=2)+'\n')
    print('E63 full blind-audited map ready',out,flush=True)


if __name__=='__main__':main()
