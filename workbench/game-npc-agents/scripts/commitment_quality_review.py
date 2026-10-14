#!/usr/bin/env python3
"""User-authorized blind quality audit, explicit free OpenCode model only."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import subprocess
import time

PROMPT = '''You are a blind data reviewer of existing LIGHT fantasy NPC game scenarios.
Read every attached scene. Do not use tools or access other files. No agent outputs or experimental
conditions are provided. Evaluate: authored task versus its motivations; plausibility of this visible
character requesting the item; meaningful physical resource conflict; serious contradictions or fabricated
context. All LIGHT agents, including animals, may communicate. A request being declined is not an invalid
scene; abstract traits are not gold actions. Return ONLY a JSON array with one row for every case_id:
case_id, task_consistent (boolean), request_natural (boolean), meaningful_conflict (boolean),
decision (keep/review/reject), reason (short string). Do not infer unstated reasons for requesting an item.'''


def parse_review(path):
    texts = []
    for line in path.read_text().splitlines():
        event = json.loads(line)
        if event.get('type') == 'text':
            texts.append(event['part']['text'])
        if event.get('part', {}).get('type') == 'tool':
            raise ValueError('Reviewer used a tool; audit is not read-only prompt-only')
    s = '\n'.join(texts).strip()
    if s.startswith('```'):
        s = s[s.index('\n')+1:s.rindex('```')].strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # Some Free-model streams contain analysis followed by the final array.
        # Parse only a complete array whose rows carry IDs; never generate labels.
        decoder=json.JSONDecoder()
        found=[]
        for i,c in enumerate(s):
            if c!='[':continue
            try:
                value,_=decoder.raw_decode(s[i:])
                if (isinstance(value,list) and value
                        and all(isinstance(r,dict) and 'case_id' in r and 'decision' in r for r in value)):
                    found.append(value)
            except json.JSONDecodeError:
                pass
        if not found:raise
        return found[-1]


def run(path):
    index = path.stem.split('_')[-1]
    dest = path.with_name(f'review_{index}.jsonl')
    expected = {r['case_id'] for r in json.loads(path.read_text())}
    if dest.exists() and dest.stat().st_size:
        try:
            rows = parse_review(dest)
            assert {r['case_id'] for r in rows} == expected
            return {'batch': index, 'status': 'existing_complete', 'rows': rows}
        except Exception:
            return {'batch': index, 'status': 'existing_invalid_preserved', 'rows': []}
    env = dict(os.environ)
    env['OPENCODE_DB'] = f'/tmp/npc-quality-e50-{index}.db'
    start = time.monotonic()
    with dest.open('x') as f, dest.with_suffix('.stderr').open('x') as err:
        proc = subprocess.run(['/home/xiang/.opencode/bin/opencode','run','--standalone',
            '--model','opencode/big-pickle','--format','json','--file',str(path),PROMPT],
            cwd='/tmp',env=env,stdout=f,stderr=err,timeout=900)
    try:
        rows = parse_review(dest)
        assert len(rows) == len(expected) and {r['case_id'] for r in rows} == expected
        assert all(r['decision'] in {'keep','review','reject'} for r in rows)
        status = 'complete' if proc.returncode == 0 else 'nonzero_preserved'
    except Exception as exc:
        rows, status = [], 'invalid_preserved:'+str(exc)
    return {'batch':index,'status':status,'exit_code':proc.returncode,
            'wall_seconds':time.monotonic()-start,'rows':rows}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True)
    ap.add_argument('--workers',type=int,default=2)
    ap.add_argument('--max-scenes',type=int,default=200);a=ap.parse_args()
    assert 0 < a.max_scenes <= 200, 'External review limited to 200 authorized public scenarios'
    files=sorted(a.directory.glob('batch_*.json'))
    selected=[];count=0
    for f in files:
        n=len(json.loads(f.read_text()))
        if count+n > a.max_scenes:
            break
        selected.append(f);count+=n
    files=selected
    results=[]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        tasks={pool.submit(run,f):f for f in files}
        for task in as_completed(tasks):
            try:result=task.result()
            except Exception as exc:result={'batch':tasks[task].stem,'status':'failed_preserved:'+str(exc),'rows':[]}
            results.append(result)
            (a.directory/'quality_summary.json').write_text(json.dumps({
                'provider_model':'opencode/big-pickle','official_price':'Free',
                'price_source':'https://opencode.ai/v2/docs/console/models/',
                'runtime_npc_cloud_calls':0,'paid_calls':0,'batches':results},indent=2)+'\n')
            print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)


if __name__=='__main__':main()
