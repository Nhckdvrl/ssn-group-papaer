#!/usr/bin/env python3
"""Recover only missing/invalid E59 DATA rows; retain every valid original label."""
import argparse
import json
from pathlib import Path
from step_transfer_claims import call


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--key-file', type=Path, required=True)
    args = ap.parse_args()
    assert (args.out / 'usage.json').exists(), 'Wait for all original batches to finish'
    public = {r['annotation_id']: r for r in json.loads((args.out / 'public_data.json').read_text())}
    seen = set()
    for directory in sorted(args.out.glob('batch_*')):
        if (directory / 'labels.json').exists():
            for row in json.loads((directory / 'labels.json').read_text()):
                assert row['annotation_id'] not in seen
                seen.add(row['annotation_id'])
            continue
        if not (directory / 'response.json').exists():
            continue
        response = json.loads((directory / 'response.json').read_text())
        try:
            value = json.loads(response['choices'][0]['message']['content'])
            value = value.get('cases', value) if isinstance(value, dict) else value
            if isinstance(value, dict):
                value = [{'annotation_id': k, **v} for k, v in value.items()]
            valid, invalid = [], []
            requested = {r['annotation_id'] for r in json.loads(json.loads(
                (directory / 'request.json').read_text())['messages'][1]['content'])}
            for row in value:
                aid = row.get('annotation_id')
                quote = row.get('exact_quote')
                acceptable = (aid in requested and aid not in seen
                    and row.get('handover_claim') in ['yes', 'no', 'ambiguous']
                    and isinstance(quote, str) and quote in public[aid]['memory']
                    and (row['handover_claim'] != 'yes' or bool(quote)))
                if acceptable:
                    valid.append(row)
                    seen.add(aid)
                else:
                    invalid.append(row)
            # Derived validation; raw response and original failure metadata remain untouched.
            (directory / 'labels.json').write_text(json.dumps(valid, ensure_ascii=False, indent=2) + '\n')
            (directory / 'partial_validation.json').write_text(json.dumps({
                'valid_preserved': len(valid), 'invalid_raw_labels': invalid,
                'missing_ids': sorted(requested - {r['annotation_id'] for r in valid})},
                ensure_ascii=False, indent=2) + '\n')
        except (KeyError, TypeError, ValueError) as exc:
            (directory / 'partial_validation.json').write_text(json.dumps({'unparsed': str(exc)}) + '\n')
    missing = [public[aid] for aid in sorted(set(public) - seen)]
    (args.out / 'recovery_manifest.json').write_text(json.dumps({
        'valid_original_rows_preserved': len(seen), 'missing_rows': len(missing),
        'purpose': 'DATA only, missing rows; no valid regeneration',
        'cash_endpoint_calls': 0, 'npc_cloud_calls': 0}, indent=2) + '\n')
    if not missing:
        print(json.dumps({'valid_labels': len(seen), 'new_requests': 0}))
        return
    index = max(int(d.name.split('_')[-1]) for d in args.out.glob('batch_*')) + 1
    key = args.key_file.read_text().strip()
    for offset in range(0, len(missing), 20):
        metadata = call(index + offset // 20, missing[offset:offset+20], key, args.out)
        assert metadata['complete'], 'Preserve remaining missing rows; no fallback'


if __name__ == '__main__':
    main()
