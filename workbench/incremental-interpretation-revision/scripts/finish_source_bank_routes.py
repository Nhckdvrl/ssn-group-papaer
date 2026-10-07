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
from data import sha,write_jsonl


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
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--role-v2',action='store_true');args=parser.parse_args();root=args.root
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
    audit_runs=runs;auditor='audit_paraphrases.py';version='v1'
    if args.role_v2:
        version='v2';auditor='audit_paraphrases_role_v2.py'
        # Input-defined correction scope: every MVRR packet, irrespective of old labels.
        source_rows=[json.loads(l) for l in sources.read_text().splitlines()]
        mvrr={r['sentence'] for r in source_rows if r['construction']=='MVRR'}
        retained=[];removed=0;original=[]
        for directory in previous:
            labels=directory/'step5/annotated.jsonl';original.append(dict(path=str(directory),sha256=sha(labels)))
            for row in map(json.loads,labels.read_text().splitlines()):
                source=row['sentence'].split('\n\nPARAPHRASE:\n',1)[0].removeprefix('SOURCE:\n')
                if source in mvrr:removed+=1
                else:retained.append(row)
        assert len({r['item_id'] for r in retained})==len(retained)
        legacy=root/'legacy-non-MVRR-v1';(legacy/'step5').mkdir(parents=True,exist_ok=True)
        write_jsonl(legacy/'step5/annotated.jsonl',retained)
        (legacy/'step5/summary.json').write_text(json.dumps(dict(complete=True,retained=len(retained),removed_MVRR=removed,
            policy='Completed v1 labels retained only outside the input-defined MVRR correction scope; no filtering by outcome or direction.'))+'\n')
        (legacy/'scope.json').write_text(json.dumps(dict(original=original,scope='Input-defined non-MVRR completed legacy labels. MVRR regenerated with role-v2 clarification.',annotation_sha256=sha(legacy/'step5/annotated.jsonl')),indent=2)+'\n')
        previous=[legacy]
        audit_runs=[root.parent/'E63/runs-v1'/name for name in names]+runs
    audit=root/f'T4-full-{version}'
    subprocess.run([sys.executable,str(script/auditor),'--data',str(sources),'--runs',*map(str,audit_runs),'--out',str(audit),
        '--workers','4','--previous-audits',*map(str,previous)],check=True)
    results=[]
    for reference,comparison in [('BASE_BANK','FULL_BANK'),('BASE_BANK','TARGET_BANK'),('BASE_BANK','CONTEXT_BANK'),('CONTEXT_BANK','TARGET_BANK')]:
        out=root/f'{comparison}-minus-{reference}-{version}.json'
        subprocess.run([sys.executable,str(script/'analyze_source_bank_routes.py'),'--data',str(data),'--sources',str(sources),'--runs',*map(str,runs),
            '--audits',str(audit),*map(str,previous),'--reference-condition',reference,'--comparison-condition',comparison,'--out',str(out)],check=True)
        results.append(dict(path=str(out),sha256=sha(out),reference=reference,comparison=comparison))
    if args.role_v2:
        e63=root.parent/'E63/shared-source-cross-use-map-v2.json'
        subprocess.run([sys.executable,str(script/'analyze_shared_source_cross_use.py'),'--data',str(data),'--sources',str(sources),
            '--runs',*[str(root.parent/'E63/runs-v1'/name) for name in names],'--audits',str(audit),*map(str,previous),'--out',str(e63)],check=True)
        results.append(dict(path=str(e63),sha256=sha(e63),scope='E63 same frozen runs, corrected MVRR T4 v2; original v1 preserved.'))
    (root/f'complete-map-{version}.json').write_text(json.dumps(dict(results=results,policy='All registered families, source cohorts and conditions; complete blind audit before outcome analysis.'),indent=2)+'\n')
    print('E64 all contrasts ready',flush=True)


if __name__=='__main__':main()
