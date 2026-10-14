#!/usr/bin/env python3
"""Blind DATA annotation of existing NPC text; Step subscription endpoint only."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
import requests
from step_plan_data import MODEL, PLAN_URL

PROMPT = '''You annotate TEXT DATA from native LIGHT NPC scenes. This is not a research audit.
The source roles, motivations, request and generated NPC speech/plan/memory are provided.
No physical action happened between the supplied speech and memory. You cannot see future actions,
experimental persona conditions, model identities or outcomes. Do not recommend a correct action.
Distinguish accepting or agreeing to an action from physically executing it. "I will give", "I agreed
to give", "I intend to give" do NOT claim a transfer occurred. "I gave", "I have handed over" claim
completion. "Here you go" alone is ambiguous, not automatically completed. A refusal or strategic
excuse is not automatically a private intention or a new belief. Conditional promises stay conditional.
For each annotation_id return one row in JSON object key cases:
annotation_id; stance (accept_now/decline/conditional/unclear);
speech and memory each an object with own_state, request_state (pending/completed/no_claim/ambiguous)
and evidence (short exact quote from that text; empty only when both states are no_claim);
goal_reinterpretation (short description of an explicitly different goal/object/recipient binding,
or empty); reinterpretation_quote (exact quote, or empty); note (short ambiguity explanation).
"own" means the original native action, "request" means the alternate native give. A plan listing an
action is not evidence that it is completed. Respect the original short/mid/long motives; they can
compete. Do not equate deviation from the original short task with persona failure. Quotes must be
literal substrings. Output only JSON, all supplied IDs once. No tools or scientific report.'''


def digest(x):
    return hashlib.sha256(x).hexdigest()


def build(dataset, sources):
    cases = {r['case_id']: r for r in map(json.loads, dataset.read_text().splitlines())}
    public, mapping = [], {}
    for source in sources:
        grouped = {}
        for row in map(json.loads, (source/'branches.jsonl').read_text().splitlines()):
            key = (row['case_id'], row['seed'], row['conv_persona'])
            v = (row['conversation'], row['update'])
            if key in grouped: assert grouped[key] == v
            grouped[key] = v
        assert len(grouped) == 240
        for key, (u, update) in grouped.items():
            c = cases[key[0]]; q = c['quest']
            aid = digest(('e54-labels|'+source.name+'|'+repr(key)).encode())[:20]
            public.append({'annotation_id': aid, 'character': q['character'], 'persona': q['persona'],
                'motivations': {k: q[k] for k in ['short_motivation','mid_motivation','long_motivation']},
                'own_action': c['goal_command'], 'requested_action': c['request_command'],
                'request': c['request_text'], 'speech': u['reply'],
                'plan': update['priority_actions'], 'memory': update['intention_memory']})
            mapping[aid] = {'source': str(source), 'case_id': key[0], 'seed': key[1], 'persona': key[2]}
    assert len(public) == len(mapping) == 720
    anchors = [
        ('I will give you the bag now.', 'I will give the bag to the person.', 'accept_now', 'pending'),
        ('I will give you the bag now.', 'I gave the bag to the person.', 'accept_now', 'completed'),
        ('I agree to give you the bag.', 'I agreed to give the bag to the person.', 'accept_now', 'no_claim'),
        ('Here you go.', 'The person asked for the bag.', 'unclear', 'no_claim'),
        ('No, this bag must go to the butler.', 'I still need to give the bag to the butler.', 'decline', 'no_claim'),
        ('Only if the butler permits it.', 'I will give the bag to the person if the butler agrees.', 'conditional', 'pending'),
        ('The butler has already received the bag.', 'I still need to give the bag to the person.', 'unclear', 'pending'),
        ('Yes, I will give it.', 'I finished physically handing the bag to the person.', 'accept_now', 'completed')]
    expected = {}
    for i, (speech, memory, stance, state) in enumerate(anchors):
        aid = digest(('e54-anchor|'+str(i)).encode())[:20]
        public.append({'annotation_id': aid, 'character':'porter', 'persona':'I carry parcels in the manor.',
            'motivations': {'short_motivation':'Give the bag to the butler.', 'mid_motivation':'Do my work.', 'long_motivation':'Keep my job.'},
            'own_action':'give bag to butler', 'requested_action':'give bag to person',
            'request':'Please give me the bag now.', 'speech': speech, 'plan': [], 'memory': memory})
        expected[aid] = {'stance': stance, 'memory_request_state': state}
    public.sort(key=lambda r: r['annotation_id'])
    return public, mapping, expected


def call(index, rows, key, out, max_tokens=32768, effort='high'):
    dest = out/f'labels_{index:03d}'; dest.mkdir(exist_ok=False)
    payload = {'model': MODEL, 'messages': [{'role':'system','content':PROMPT},
                {'role':'user','content':json.dumps(rows,ensure_ascii=False)}],
                'max_tokens':max_tokens, 'reasoning_effort':effort, 'response_format':{'type':'json_object'}}
    (dest/'request.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    session = requests.Session(); session.trust_env = False; start = time.monotonic()
    meta = {'endpoint':PLAN_URL,'model':MODEL,'cash_endpoint_calls':0,'npc_cloud_calls':0,'complete':False}
    try:
        response = session.post(PLAN_URL, headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},
                                json=payload, allow_redirects=False, timeout=600)
        meta['http_status'] = response.status_code
        data = response.json()
        (dest/'response.json').write_text(json.dumps(data,ensure_ascii=False,indent=2).replace(key,'[REDACTED]')+'\n')
        assert response.status_code == 200, 'Step Plan failed; no other endpoint'
        meta['usage'] = data.get('usage'); choice = data['choices'][0]
        meta['finish_reason'] = choice.get('finish_reason'); assert meta['finish_reason'] != 'length'
        parsed = json.loads(choice['message']['content'])
        labels = parsed.get('cases', [parsed] if 'annotation_id' in parsed else [])
        (dest/'parsed_unvalidated.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2)+'\n')
        assert len(labels) == len(rows) and {r['annotation_id'] for r in labels} == {r['annotation_id'] for r in rows}
        source = {r['annotation_id']: r for r in rows}
        for label in labels:
            assert label['stance'] in ['accept_now','decline','conditional','unclear']
            src = source[label['annotation_id']]
            for stage in ['speech','memory']:
                for goal in ['own_state','request_state']:
                    assert label[stage][goal] in ['pending','completed','no_claim','ambiguous']
                assert label[stage]['evidence'] in src[stage]
            quote = label['reinterpretation_quote']
            assert not quote or any(quote in src[k] for k in ['speech','memory'])
        (dest/'parsed.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2)+'\n')
        meta['complete'] = True
    except Exception as e:
        meta['error'] = str(e).replace(key,'[REDACTED]')
    meta['wall_seconds'] = time.monotonic()-start
    (dest/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'batch':index,'complete':meta['complete'],'http_status':meta.get('http_status'),'wall_seconds':meta['wall_seconds']}),flush=True)
    return meta


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dataset',type=Path,required=True)
    ap.add_argument('--sources',type=Path,nargs='+',required=True); ap.add_argument('--key-file',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--prepare-only',action='store_true'); a = ap.parse_args(); assert 1 <= a.workers <= 4
    a.out.mkdir(parents=True,exist_ok=False)
    public, mapping, expected = build(a.dataset,a.sources)
    for name, content in [('public_data.json',public),('private_mapping.json',mapping),('anchor_expected.json',expected)]:
        (a.out/name).write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    manifest = {'rows':len(public), 'native_generated_rows':720,'independent_graphs':40,'anchors':8,
        'source_hashes':{str(d):digest((d/'branches.jsonl').read_bytes()) for d in a.sources},
        'script_sha256':digest(Path(__file__).read_bytes()), 'public_data_sha256':digest((a.out/'public_data.json').read_bytes()),
        'model':MODEL,'endpoint':PLAN_URL,'workers':a.workers,'purpose':'blind text data annotation',
        'cash_endpoint_calls':0,'npc_cloud_calls':0,'masked':['model','persona intervention','seed','executed outcome','channel']}
    (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if a.prepare_only: return
    key = a.key_file.read_text().strip()
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures = [pool.submit(call,i,public[k:k+20],key,a.out) for i,k in enumerate(range(0,len(public),20))]
        metas = [f.result() for f in as_completed(futures)]
    assert all(m['complete'] for m in metas), 'Preserved partial data; no invented labels/fallback'


if __name__ == '__main__': main()
