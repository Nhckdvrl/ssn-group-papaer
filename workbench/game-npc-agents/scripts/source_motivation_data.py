#!/usr/bin/env python3
"""Blind extractive source DATA: stated beneficiaries, never utility/gold judging."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
import requests
from step_plan_data import PLAN_URL, MODEL

PROMPT = '''Extract source-text DATA only. Do not judge an NPC's correct choice, real utility,
personality, experiment success, or scientific claims. You see authored character/motivations
and a request. For EACH of short_motivation, mid_motivation, long_motivation, classify only
the beneficiary explicitly described: self, other, self_and_other, unspecified. Use the stated
purpose, not who physically receives an item. Giving to a king to secure better pay can serve
self; a request or a task verb alone never proves altruism. Do not infer unstated benefits,
relationships, trustworthiness or eventual success. Each level: scope, beneficiary_text
(brief extractive names/roles), exact_quote (literal substring of that motivation; empty if
unspecified). Separately, does the REQUEST TEXT explicitly claim to help the NPC's authored
motivation? support_claim: yes/no/unclear, request_quote (literal substring of request),
motivation_quote (literal substring of one authored motivation matching the claim, empty if
no explicit support). This is a claim in text, not verification of real help. Preserve uncertainty.
Return JSON only under key cases: one row per annotation_id, with motivation_levels containing
the three named levels, support_claim, request_quote, motivation_quote. No advice, action
predictions, scores or audit. All experimental conditions and behaviors are hidden.'''


def call(index, rows, key, out):
    folder = out / f'batch_{index:03d}'
    folder.mkdir(exist_ok=False)
    payload = {'model': MODEL, 'messages': [{'role': 'system', 'content': PROMPT},
        {'role': 'user', 'content': json.dumps(rows, ensure_ascii=False)}],
        'reasoning_effort': 'low', 'max_tokens': 16384, 'response_format': {'type': 'json_object'}}
    (folder / 'request.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    metadata = {'endpoint': PLAN_URL, 'model': MODEL, 'complete': False,
                'cash_endpoint_calls': 0, 'npc_cloud_calls': 0}
    start = time.monotonic()
    try:
        session = requests.Session(); session.trust_env = False
        response = session.post(PLAN_URL, headers={'Authorization': 'Bearer '+key}, json=payload,
                                allow_redirects=False, timeout=600)
        result = response.json()
        (folder / 'response.json').write_text(json.dumps(result, ensure_ascii=False, indent=2).replace(key, '[REDACTED]')+'\n')
        metadata['http_status'] = response.status_code
        metadata['usage'] = result.get('usage')
        assert response.status_code == 200
        choice = result['choices'][0]; metadata['finish_reason'] = choice.get('finish_reason')
        assert metadata['finish_reason'] != 'length'
        labels = json.loads(choice['message']['content']); labels = labels.get('cases', labels)
        if isinstance(labels, dict): labels = [{'annotation_id': k, **v} for k,v in labels.items()]
        sources = {r['annotation_id']: r for r in rows}
        assert len(labels) == len(sources) and {r['annotation_id'] for r in labels} == set(sources)
        for row in labels:
            source = sources[row['annotation_id']]
            assert set(row['motivation_levels']) == {'short_motivation','mid_motivation','long_motivation'}
            for level, label in row['motivation_levels'].items():
                assert label['scope'] in ['self','other','self_and_other','unspecified']
                assert label['exact_quote'] in source[level]
                assert label['scope'] == 'unspecified' or label['exact_quote']
            assert row['support_claim'] in ['yes','no','unclear']
            assert row['request_quote'] in source['request_text']
            assert any(row['motivation_quote'] in source[k] for k in row['motivation_levels'])
            assert row['support_claim'] != 'yes' or (row['request_quote'] and row['motivation_quote'])
        (folder / 'labels.json').write_text(json.dumps(labels, ensure_ascii=False, indent=2)+'\n')
        metadata['complete'] = True
    except Exception as exc:
        metadata['error'] = str(exc).replace(key, '[REDACTED]')
    metadata['wall_seconds'] = time.monotonic()-start
    (folder / 'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps({'batch': index, 'complete': metadata['complete'],
                      'http_status': metadata.get('http_status')}), flush=True)
    return metadata


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--key-file', type=Path, required=True)
    args = ap.parse_args()
    cases = list(map(json.loads, args.dataset.read_text().splitlines()))
    assert len(cases) == len({c['graph_sha256'] for c in cases}) == 200
    public, mapping = [], {}
    for case in cases:
        aid = hashlib.sha256(('motivation-source|'+case['case_id']).encode()).hexdigest()[:24]
        public.append({'annotation_id': aid, 'character': case['quest']['character'],
            **{k:case['quest'][k] for k in ['short_motivation','mid_motivation','long_motivation']},
            'request_text': case['request_text']})
        mapping[aid] = case['case_id']
    public.sort(key=lambda r:r['annotation_id'])
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'public_data.json').write_text(json.dumps(public, ensure_ascii=False, indent=2)+'\n')
    (args.out / 'private_mapping.json').write_text(json.dumps(mapping, indent=2)+'\n')
    (args.out / 'manifest.json').write_text(json.dumps({'graphs':200,'purpose':'extractive text DATA only',
        'endpoint':PLAN_URL,'model':MODEL,'masked':['personas','models','conditions','behavior outcomes'],
        'dataset_sha256':hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cash_endpoint_calls':0,'npc_cloud_calls':0},indent=2)+'\n')
    key = args.key_file.read_text().strip()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(call, index, public[offset:offset+10], key, args.out)
                   for index,offset in enumerate(range(0,200,10))]
        results = [f.result() for f in as_completed(futures)]
    (args.out / 'usage.json').write_text(json.dumps({'requests':len(results),
        'complete_batches':sum(r['complete'] for r in results),
        'total_tokens':sum((r.get('usage') or {}).get('total_tokens',0) for r in results),
        'cash_endpoint_calls':0,'npc_cloud_calls':0},indent=2)+'\n')
    assert all(r['complete'] for r in results), 'Preserve missing/invalid DATA, no fallback'


if __name__ == '__main__':
    main()
