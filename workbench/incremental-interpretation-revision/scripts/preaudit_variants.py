"""Independent opencode pre-audit while Step5 resources are unavailable.

This never overwrites Step5 annotations or silently turns an advisory into gold.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from data import CACHE,sha
from step_audit import PROMPT,items_from

def one(item,model,out):
    uid=hashlib.sha256(item['variant_id'].encode()).hexdigest()[:20]
    p=out/f'{uid}.review.json'
    message=PROMPT+'\nDo not use tools, execute commands, or edit files.\nINPUT JSON:\n'+json.dumps(item,separators=(',',':'))
    request={'model':model,'message':message,'advisory_only':True}
    request_hash=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
    if p.exists():
        prev=json.loads(p.read_text())
        if prev['request_sha256']==request_hash and prev['status']=='complete_advisory':return prev
    (out/f'{uid}.request.json').write_text(json.dumps(request,indent=2)+'\n')
    env=dict(os.environ)
    for k in list(env):
        if k.lower() in ('http_proxy','https_proxy','all_proxy'):env.pop(k)
    env.update(NO_PROXY='*',no_proxy='*')
    events=out/f'{uid}.events.jsonl';err=out/f'{uid}.stderr'
    with events.open('w') as f,err.open('w') as e:
        try:code=subprocess.run(['opencode','run',message,'--pure','-m',model,'--dir',str(CACHE),'--format','json'],env=env,stdout=f,stderr=e,timeout=360).returncode
        except subprocess.TimeoutExpired:code=124
    ev=[]
    for line in events.read_text().splitlines():
        try:ev.append(json.loads(line))
        except json.JSONDecodeError:pass
    text=''.join(x.get('part',{}).get('text','') for x in ev if x.get('type')=='text')
    text=re.sub(r'^```(?:json)?\s*|\s*```$','',text.strip())
    report={'variant_id':item['variant_id'],'request_sha256':request_hash,'events_sha256':sha(events),
            'model':model,'exit_code':code,'proxy_used':False,'advisory_only':True}
    try:
        assert code==0,'process did not finish normally'
        assert any(x.get('type')=='step_finish' for x in ev),'missing finish event'
        a=json.loads(text);assert a['variant_id']==item['variant_id']
        ids=[x['item_id'] for x in a['answers']]
        assert len(ids)==len(set(ids)) and set(ids)=={x['item_id'] for x in item['questions']}
        assert a['grammaticality'] in ('acceptable','marginal','unacceptable')
        for x in a['answers']:
            assert type(x['question_valid']) is bool and x['answer'] in ('Yes','No',None)
            assert x['certainty'] in ('clear','interpretation_dependent','invalid')
        report.update(status='complete_advisory',annotation=a)
    except Exception as e:report.update(status='incomplete_advisory',error=type(e).__name__+': '+str(e)[:100])
    p.write_text(json.dumps(report,indent=2)+'\n');print(item['variant_id'],report['status'],flush=True);return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=CACHE/'normalized/jurayj.jsonl')
    p.add_argument('--model',default='opencode/mimo-v2.6-flash-free');p.add_argument('--workers',type=int,default=4)
    p.add_argument('--limit',type=int);p.add_argument('--out',type=Path,default=CACHE/'opencode-preaudit-E01-v2');a=p.parse_args()
    assert 1<=a.workers<=8;a.out.mkdir(exist_ok=True)
    items=items_from([json.loads(x) for x in a.data.read_text().splitlines()])
    items.sort(key=lambda i:(int(i['variant_id'].split(':')[1]),{'NPZ':0,'NPS':1,'MVRR':2}[i['construction']]))
    if a.limit:items=items[:a.limit]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:reviews=list(pool.map(lambda item:one(item,a.model,a.out),items))
    (a.out/'manifest.json').write_text(json.dumps({'model':a.model,'data_sha256':sha(a.data),'advisory_only':True,'proxy_used':False,'concurrency':a.workers,'reviews':reviews},indent=2)+'\n')
