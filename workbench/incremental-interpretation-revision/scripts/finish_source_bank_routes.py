"""Finish the fixed E64 panel, reuse completed labels, and produce every bank contrast."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from data import sha


def share_api_slots(root):
    """Reduce E53 drivers only after all live HTTP requests have returned."""
    manifest = root.parent/'E53/restore-eight-workers.json'
    if not manifest.exists():
        print('E53 restore controller still pending; awaiting its safe handoff',flush=True)
        while not manifest.exists():time.sleep(10)
    record=json.loads(manifest.read_text());commands=[];old=[]
    for pid in record['new']:
        try:
            args=Path(f'/proc/{pid}/cmdline').read_bytes().decode().strip('\0').split('\0')
        except FileNotFoundError:continue
        assert 'audit_paraphrases.py' in ' '.join(args)
        args[args.index('--workers')+1]='2';commands.append(args);old.append(pid)
    if not old:return
    locks=[]
    try:
        for i in range(8):
            f=(root.parent/'step-plan-slots'/str(i)).open('a');fcntl.flock(f,fcntl.LOCK_EX);locks.append(f)
        time.sleep(1)
        for pid in old:
            try:os.kill(pid,signal.SIGTERM)
            except ProcessLookupError:pass
        time.sleep(1);new=[]
        for i,cmd in enumerate(commands):
            with (root.parent/'E53'/f'T4-E64-shared-pass{i+1}.log').open('w') as log:
                proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);new.append(proc.pid)
        (root/'api-share.json').write_text(json.dumps(dict(old=old,new=new,E53_workers_per_pass=2,E64_workers=4,
            policy='All shared HTTP slots returned before handoff; caches, protocol, independent order and batch2 unchanged.'),indent=2)+'\n')
    finally:
        for f in locks:fcntl.flock(f,fcntl.LOCK_UN);f.close()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args();root=args.root
    script=Path(__file__).parent;names=['Qwen3-8B','gemma-3-12b-it','Meta-Llama-3.1-8B-Instruct'];runs=[root/'runs-v1'/name for name in names]
    start=time.monotonic();last=None
    while True:
        complete=[]
        for path in runs:
            try:
                c=json.loads((path/'config.json').read_text());ok=c.get('predictions_sha256')==sha(path/'predictions.jsonl') and c.get('qa_predictions_sha256')==sha(path/'qa-predictions.jsonl')
            except (OSError,KeyError,json.JSONDecodeError):ok=False
            complete.append(ok)
        if complete!=last:print('E64 complete panel',dict(zip(names,complete)),flush=True);last=complete
        if all(complete):break
        if time.monotonic()-start>43200:raise RuntimeError('E64 full panel unfinished; inspect logs without interpreting partial outcomes.')
        time.sleep(10)
    share_api_slots(root)
    previous=[root.parent/'E63/T4-full-v1',root.parent/'E53/T4-instrument-v2']
    sources=root.parent/'E63/sources-v1.jsonl';data=root.parent/'E63/data-v1.jsonl'
    subprocess.run([sys.executable,str(script/'audit_paraphrases.py'),'--data',str(sources),'--runs',*map(str,runs),'--out',str(root/'T4-full-v1'),
        '--workers','4','--previous-audits',*map(str,previous)],check=True)
    results=[]
    for reference,comparison in [('BASE_BANK','FULL_BANK'),('BASE_BANK','TARGET_BANK'),('BASE_BANK','CONTEXT_BANK'),('CONTEXT_BANK','TARGET_BANK')]:
        out=root/f'{comparison}-minus-{reference}-v1.json'
        subprocess.run([sys.executable,str(script/'analyze_source_bank_routes.py'),'--data',str(data),'--sources',str(sources),'--runs',*map(str,runs),
            '--audits',str(root/'T4-full-v1'),*map(str,previous),'--reference-condition',reference,'--comparison-condition',comparison,'--out',str(out)],check=True)
        results.append(dict(path=str(out),sha256=sha(out),reference=reference,comparison=comparison))
    (root/'complete-map-v1.json').write_text(json.dumps(dict(results=results,policy='All registered families, source cohorts and conditions; complete blind audit before outcome analysis.'),indent=2)+'\n')
    print('E64 all contrasts ready',flush=True)


if __name__=='__main__':main()
