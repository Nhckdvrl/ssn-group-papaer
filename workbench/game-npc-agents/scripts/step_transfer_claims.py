#!/usr/bin/env python3
"""Blind text DATA claims for E59; Step Plan only, no scientific judgment."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
import requests
from step_plan_data import PLAN_URL, MODEL

PROMPT='''Label text DATA, not experimental success or scientific claims. You see an NPC's speech
and its subsequent memory, plus the exact requested physical item handover. Does the MEMORY
assert that this physical handover TO THIS REQUESTER has already occurred? Return yes/no/ambiguous.
Future plans and promises are no. "I gave in", "I agreed", "I offered", "I obliged", "I helped"
do not by themselves establish a physical handover: mark ambiguous if the text leaves this unresolved.
"Given its importance" is not a giving event. Sharing ideas/enjoyment is not sharing the item.
Giving to a different character is not this handover. Explicit "I handed the item to X", "I gave X
the item", "X received the item from me" claims physical completion. Conditional or negated events
do not assert completion. Do not infer execution from a plan or favorable personality. You cannot
see future actions, model identity or experimental conditions. For each annotation_id return one
row under JSON key cases: annotation_id, handover_claim (yes/no/ambiguous), exact_quote (literal
substring of memory, empty permitted for no assertion), note (brief ambiguity only). Output JSON
only. Do not provide an audit, recommendations, gold choices or behavior scores.'''


def build(run):
    manifest=json.loads((run/'manifest.json').read_text())
    cases={c['case_id']:c for c in map(json.loads,Path(manifest['arguments']['dataset']).read_text().splitlines())}
    public=[];mapping={}
    fixed=list(map(json.loads,(run/'records.jsonl').read_text().splitlines()))
    natural=list(map(json.loads,(run/'natural_comparison.jsonl').read_text().splitlines()))
    assert len(fixed)==len(natural)==400 and (run/'runtime.json').exists()
    for condition,rows in [('fixed_future',fixed),('natural',natural)]:
        for row in rows:
            cid=row['case_id'];p=row['persona'].removeprefix('full_');c=cases[cid]
            aid=hashlib.sha256(('transfer-data|'+run.name+'|'+condition+'|'+cid+'|'+p).encode()).hexdigest()[:24]
            update=row.get('update');assert update is not None,'Preserve failed source, do not invent a memory'
            speech=(row['fixed_conversation'] if condition=='fixed_future' else row['conversation'])['reply']
            public.append({'annotation_id':aid,'character':c['quest']['character'],'requester':c['requester_name'],
                           'requested_physical_command':c['request_command'],'speech':speech,'memory':update['intention_memory']})
            mapping[aid]={'case_id':cid,'persona':p,'condition':condition,'source':str(run)}
    anchors=[('I handed the book to the king.','yes'),('I promised to give the book to the king.','no'),
             ("I gave in to the king's request.",'ambiguous'),('I offered the book to the king.','ambiguous'),
             ('The king requested the book, and I obliged.','ambiguous'),('Given its importance, I will keep the book.','no'),
             ('I will give the book to the king next.','no'),('I shared my enjoyment of reading with the king.','no')]
    for i,(memory,expected) in enumerate(anchors):
        aid=hashlib.sha256(('transfer-anchor|'+str(i)).encode()).hexdigest()[:24]
        public.append({'annotation_id':aid,'character':'traveler','requester':'king',
            'requested_physical_command':'give book to king','speech':'I will consider the request.','memory':memory})
        mapping[aid]={'anchor_expected':expected}
    public.sort(key=lambda r:r['annotation_id']);return public,mapping


def call(index,rows,key,out):
    dest=out/f'batch_{index:03d}';dest.mkdir(exist_ok=False)
    payload={'model':MODEL,'messages':[{'role':'system','content':PROMPT},{'role':'user','content':json.dumps(rows,ensure_ascii=False)}],
             'max_tokens':16384,'reasoning_effort':'low','response_format':{'type':'json_object'}}
    (dest/'request.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    meta={'endpoint':PLAN_URL,'model':MODEL,'cash_endpoint_calls':0,'npc_cloud_calls':0,'complete':False};start=time.monotonic()
    try:
        session=requests.Session();session.trust_env=False
        response=session.post(PLAN_URL,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json=payload,
                              allow_redirects=False,timeout=600)
        meta['http_status']=response.status_code;result=response.json()
        (dest/'response.json').write_text(json.dumps(result,ensure_ascii=False,indent=2).replace(key,'[REDACTED]')+'\n')
        assert response.status_code==200,'Plan request failed; no fallback'
        meta['usage']=result.get('usage');choice=result['choices'][0];meta['finish_reason']=choice.get('finish_reason')
        assert meta['finish_reason']!='length'
        labels=json.loads(choice['message']['content']);labels=labels.get('cases',labels) if isinstance(labels,dict) else labels
        if isinstance(labels,dict):labels=[{'annotation_id':k,**v} for k,v in labels.items()]
        src={r['annotation_id']:r for r in rows}
        assert len(labels)==len(src) and {r['annotation_id'] for r in labels}==set(src)
        for r in labels:
            assert r['handover_claim'] in ['yes','no','ambiguous']
            assert r['exact_quote'] in src[r['annotation_id']]['memory']
            assert r['handover_claim']!='yes' or len(r['exact_quote'])>0
        (dest/'labels.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2)+'\n');meta['complete']=True
    except Exception as e:meta['error']=str(e).replace(key,'[REDACTED]')
    meta['wall_seconds']=time.monotonic()-start
    (dest/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'batch':index,'complete':meta['complete'],'http_status':meta.get('http_status'),'wall_seconds':meta['wall_seconds']}),flush=True)
    return meta


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--key-file',type=Path,required=True);ap.add_argument('--workers',type=int,default=4)
    a=ap.parse_args();assert 1<=a.workers<=4
    public,mapping=build(a.run);a.out.mkdir(exist_ok=False,parents=True)
    (a.out/'public_data.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
    (a.out/'private_mapping.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
    (a.out/'manifest.json').write_text(json.dumps({'rows':len(public),'native_rows':800,'anchors':8,'independent_graphs':200,'purpose':'blind text data annotation',
        'model':MODEL,'endpoint':PLAN_URL,'source':str(a.run),'public_sha256':hashlib.sha256((a.out/'public_data.json').read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cash_endpoint_calls':0,'npc_cloud_calls':0,
        'masked':['model identity','persona intervention','condition label','factual answers','actions']},indent=2)+'\n')
    key=a.key_file.read_text().strip()
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        fs=[pool.submit(call,i,public[j:j+20],key,a.out) for i,j in enumerate(range(0,len(public),20))]
        metas=[f.result() for f in as_completed(fs)]
    (a.out/'usage.json').write_text(json.dumps({'requests':len(metas),'complete_batches':sum(m['complete'] for m in metas),
        'usage':{k:sum((m.get('usage') or {}).get(k,0) for m in metas) for k in ['prompt_tokens','completion_tokens','total_tokens']},
        'cash_endpoint_calls':0,'npc_cloud_calls':0},indent=2)+'\n')
    assert all(m['complete'] for m in metas),'Raw missing/invalid labels preserved; do not fabricate rows'


if __name__=='__main__':main()
