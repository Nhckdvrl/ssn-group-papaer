#!/usr/bin/env python3
"""Step5 constructs grounded public LIGHT requests; subscription endpoint only."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
import requests

PLAN_URL = 'https://api.stepfun.com/step_plan/v1/chat/completions'
MODEL = 'step-5-preview'
GENERATOR = '''You create data for research on native LIGHT game NPC decisions.
Only the attached public source scenes are available. Preserve the original NPC, requester, authored
persona, motivations, object, initial world, and both physical commands. Write ONE natural in-character
request by the specified visible requester, asking the focal NPC to give the specified existing item to
the requester now. This introduces a social request, not a new world rule. Do not dictate the focal
NPC's reply or correct choice. Do not fabricate deadlines, threats, trades, emergencies, ownership,
relationships or completed actions. Do not ask for temporary loans/partial amounts/delayed handovers:
the native command is an immediate give of that object. A short reasonable desire supported by the
requester's persona is allowed, but mark inference separately from explicit source facts. Avoid generic
copy-paste requests and cartoon personality stereotypes. Requester names and objects can be awkward
in LIGHT; make the dialogue readable without changing entities. If the source is incoherent or there
is no plausible grounded request, keep it flagged rather than inventing facts or silently excluding it.
All LIGHT characters may talk, including animals. Do not turn 'kind' into a gold give action.
For EACH case_id return a JSON object under key cases with an array of:
case_id, request_text, supporting_source_quotes (max 2 short exact strings),
inferred_motive (string), source_issues (array of strings), suitability (natural/review),
request_is_immediate_same_transfer (boolean). Output only valid JSON. No tools, no scientific report.'''
REVIEWER = '''Blindly review each public LIGHT source scene and candidate social request.
No agent outputs, persona interventions or desired results are given. Do not access other files/tools.
Check whether the request naturally fits the existing visible requester and actual item, whether the
original task is coherent with its authored motivations, whether the request adds unsupported facts,
and whether it asks for the same immediate native give. Do not require the NPC to accept. Distinguish
first physical allocation conflict from globally impossible long-term joint completion: an equipped
item can later be given, and some gifts can be returned. Animal dialogue is allowed in LIGHT.
Return ONLY JSON object cases array, one row per case_id:
case_id, task_consistent (boolean), request_natural (boolean),
same_immediate_transfer (boolean), unsupported_facts (array of strings),
decision (keep/review/reject), reason (short string). Do not rewrite the request or infer gold behavior.'''


def public_scene(row):
    q = row['quest']
    return {'case_id':row['case_id'], 'setting':q['description'],
            'character':q['character'], 'persona':q['persona'],
            'original_task':row['goal_command'],
            'motivations':{k:q[k] for k in ['short_motivation','mid_motivation','long_motivation']},
            'requester':row['requester_name'], 'requester_persona':row['requester_persona'],
            'native_possible_actions':[row['goal_command'],row['request_command']],
            'original_request':row['request_text']}


def call(batch, key, out, mode, max_tokens, effort):
    index, rows = batch
    dest = out/f'{mode}_{index:03d}'
    dest.mkdir(exist_ok=False)
    scenes = [public_scene(r) for r in rows]
    if mode == 'review':
        for scene, row in zip(scenes, rows):
            scene.pop('original_request')
            scene['candidate_request'] = row['request_text']
    payload = {'model':MODEL,'messages':[{'role':'system','content':GENERATOR if mode=='generate' else REVIEWER},
               {'role':'user','content':json.dumps(scenes,ensure_ascii=False)}],
               'max_tokens':max_tokens, 'reasoning_effort':effort,
               'response_format':{'type':'json_object'}}
    (dest/'request.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    session = requests.Session(); session.trust_env = False
    started = time.monotonic()
    try:
        r = session.post(PLAN_URL,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},
                         json=payload,allow_redirects=False,timeout=600)
        meta = {'http_status':r.status_code,'endpoint':PLAN_URL,'model':MODEL,
                'mode':mode,'wall_seconds':time.monotonic()-started,
                'cash_endpoint_calls':0,'redirects_allowed':False,'trust_env':False}
        response = r.json()
        (dest/'response.json').write_text(json.dumps(response,ensure_ascii=False,indent=2).replace(key,'[REDACTED]')+'\n')
        if r.status_code != 200:
            meta['error'] = {k:str(v).replace(key,'[REDACTED]') for k,v in response.get('error',{}).items()}
            raise RuntimeError('Step Plan request failed: '+str(r.status_code))
        meta['usage'] = response.get('usage')
        meta['finish_reason'] = response['choices'][0].get('finish_reason')
        assert meta['finish_reason'] != 'length', 'Output budget exhausted; preserve incomplete response'
        content = response['choices'][0]['message'].get('content','')
        (dest/'text.txt').write_text(content+'\n')
        parsed = json.loads(content)
        data = parsed['cases']
        assert len(data)==len(rows) and {x['case_id'] for x in data}=={x['case_id'] for x in rows}
        if mode=='generate':
            assert all(isinstance(x.get('request_text'),str) and x['request_text'].strip() for x in data)
            assert all(x['suitability'] in ['natural','review'] for x in data)
        else:
            assert all(x['decision'] in ['keep','review','reject'] for x in data)
        (dest/'parsed.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        meta['complete'] = True
    except Exception as exc:
        meta = locals().get('meta',{})
        meta.update({'complete':False,'error_note':str(exc).replace(key,'[REDACTED]'),
                     'wall_seconds':time.monotonic()-started,'no_fallback':True})
        data = []
    (dest/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'batch':index,'mode':mode,'complete':meta['complete'],
                      'http_status':meta.get('http_status'),'rows':len(data),
                      'wall_seconds':meta['wall_seconds']}),flush=True)
    return {'index':index,'meta':meta,'rows':data}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--key-file',type=Path,required=True)
    ap.add_argument('--dataset',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--mode',choices=['generate','review'],default='generate')
    ap.add_argument('--split',default='confirm');ap.add_argument('--limit',type=int,default=200)
    ap.add_argument('--batch-size',type=int,default=10);ap.add_argument('--workers',type=int,default=2)
    ap.add_argument('--max-tokens',type=int,default=32768)
    ap.add_argument('--reasoning-effort',choices=['low','medium','high'],default='high')
    a=ap.parse_args();assert a.workers<=4 and a.limit<=200
    rows=[r for r in map(json.loads,a.dataset.read_text().splitlines()) if r['split']==a.split][:a.limit]
    assert rows and len({r['graph_sha256'] for r in rows})==len(rows)
    a.out.mkdir(parents=True,exist_ok=False)
    manifest={'dataset':str(a.dataset),'dataset_sha256':hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
              'model':MODEL,'endpoint':PLAN_URL,'case_ids':[r['case_id'] for r in rows],
              'mode':a.mode,'workers':a.workers,'batch_size':a.batch_size,
              'max_tokens':a.max_tokens,'reasoning_effort':a.reasoning_effort,
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'parameter_source':'https://platform.stepfun.com/docs/zh/guides/models/step-5-preview',
              'paid_cash_calls':0,'npc_cloud_calls':0,'purpose':'public native-game data construction/quality'}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    key=a.key_file.read_text().strip();results=[]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures=[pool.submit(call,(i,rows[k:k+a.batch_size]),key,a.out,a.mode,a.max_tokens,a.reasoning_effort)
                 for i,k in enumerate(range(0,len(rows),a.batch_size))]
        for f in as_completed(futures):
            results.append(f.result())
            (a.out/'summary.json').write_text(json.dumps(sorted(results,key=lambda r:r['index']),ensure_ascii=False,indent=2)+'\n')
    assert all(r['meta']['complete'] for r in results), 'Raw failures preserved; do not auto-fallback or fabricate rows'
    generated={d['case_id']:d for r in results for d in r['rows']}
    if a.mode=='generate':
        for row in rows:
            row['request_text_v1']=row['request_text']
            row['request_text']=generated[row['case_id']]['request_text']
            row['request_origin']='Step5-grounded construction from public source; fixed native entities and command'
            row['data_construction']=generated[row['case_id']]
        (a.out/'snapshots.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n')
    else:
        (a.out/'quality.json').write_text(json.dumps(generated,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
