#!/usr/bin/env python3
"""Recover only missing source DATA; retain successful original annotations."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import source_motivation_data as source


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--key-file', type=Path, required=True)
    ap.add_argument('--batch-size', type=int, default=4, choices=[1, 2, 4])
    args = ap.parse_args()
    assert (args.run / 'usage.json').exists(), 'Finish original requests first'
    summary = json.loads((args.run / 'collection.json').read_text())
    missing = set(summary['missing_ids'])
    public = json.loads((args.run / 'public_data.json').read_text())
    pending = [r for r in public if r['annotation_id'] in missing]
    assert len(pending) == len(missing)
    args.out.mkdir(parents=True, exist_ok=False)
    for name in ['public_data.json', 'private_mapping.json']:
        (args.out / name).write_bytes((args.run / name).read_bytes())
    (args.out / 'manifest.json').write_text(json.dumps({
        'source': str(args.run), 'pending_ids': sorted(missing),
        'purpose': 'recover missing extractive DATA only', 'rows_per_batch': args.batch_size,
        'endpoint': source.PLAN_URL, 'model': source.MODEL,
        'cash_endpoint_calls': 0, 'npc_cloud_calls': 0}, indent=2)+'\n')
    # The former schema sometimes used scope for the motivation level. Make the
    # requested field semantics explicit, without changing any semantic criterion.
    source.PROMPT += '''
Use EXACTLY this JSON schema. scope is the beneficiary category, NEVER short/mid/long.
{"cases":[{"annotation_id":"copy ID","motivation_levels":{
"short_motivation":{"scope":"self|other|self_and_other|unspecified","beneficiary_text":"names/roles","exact_quote":"literal source substring"},
"mid_motivation":{"scope":"self|other|self_and_other|unspecified","beneficiary_text":"names/roles","exact_quote":"literal source substring"},
"long_motivation":{"scope":"self|other|self_and_other|unspecified","beneficiary_text":"names/roles","exact_quote":"literal source substring"}},
"support_claim":"yes|no|unclear","request_quote":"literal request substring or empty","motivation_quote":"literal motivation substring or empty"}]}
Choose ONE category per field, not the vertical-bar examples. Include every supplied ID.
Do not write reasoning or explanations; brief beneficiary_text and literal quotes suffice.
'''
    key = args.key_file.read_text().strip()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(source.call, index, pending[offset:offset+args.batch_size], key, args.out)
                   for index, offset in enumerate(range(0, len(pending), args.batch_size))]
        results = [f.result() for f in as_completed(futures)]
    (args.out / 'usage.json').write_text(json.dumps({
        'requests': len(results), 'complete_batches': sum(r['complete'] for r in results),
        'total_tokens': sum((r.get('usage') or {}).get('total_tokens', 0) for r in results),
        'cash_endpoint_calls': 0, 'npc_cloud_calls': 0}, indent=2)+'\n')


if __name__ == '__main__':
    main()
