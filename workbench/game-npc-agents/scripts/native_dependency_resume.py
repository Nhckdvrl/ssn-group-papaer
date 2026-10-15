#!/usr/bin/env python3
"""Resume complete-world E63 prefixes, preserving the original eight-world batches."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time
import native_dependency_roles as policy


def partition(dataset, prefix, shard, shards):
    rows = list(map(json.loads, dataset.read_text().splitlines()))
    old = list(map(json.loads, (prefix/'episodes.jsonl').read_text().splitlines()))
    manifest = json.loads((prefix/'manifest.json').read_text())
    lookup = {(r['case_id'], r['seed'], r['persona'], r['rule'], r['mode']): r for r in old}
    assert len(lookup) == len(old)
    ids = {r['case_id'] for r in old}
    expected = {(r['case']['case_id'], s, p, rule, mode) for r in rows if r['case']['case_id'] in ids
                for s in manifest['arguments']['seeds'] for p in policy.TRAITS for rule in policy.RULES for mode in r['requests']}
    assert set(lookup) == expected, 'prefix contains a partially written world'
    original_groups = [rows[:1]] + [rows[i:i+8] for i in range(1, len(rows), 8)]
    remaining = []
    for group in original_groups:
        status = [r['case']['case_id'] in ids for r in group]
        assert all(status) or not any(status), 'prefix splits an original batch'
        if not any(status): remaining.append(group)
    groups = [g for i, g in enumerate(remaining) if i % shards == shard]
    return manifest, groups


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--prefix', type=Path, required=True)
    ap.add_argument('--shard', type=int, required=True); ap.add_argument('--shards', type=int, default=3)
    ap.add_argument('--out', type=Path); ap.add_argument('--dry-run', action='store_true'); a = ap.parse_args()
    ref = json.loads((a.prefix/'manifest.json').read_text()); dataset = Path(ref['arguments']['dataset'])
    manifest, groups = partition(dataset, a.prefix, a.shard, a.shards)
    ids = [r['case']['case_id'] for group in groups for r in group]
    if a.dry_run:
        print(json.dumps({'worlds': len(ids), 'groups': len(groups), 'case_ids': ids})); return
    assert a.out is not None and (a.prefix/'interrupted_runtime.json').exists()
    checkpoint = json.loads((a.prefix/'interrupted_runtime.json').read_text())
    assert hashlib.sha256((a.prefix/'episodes.jsonl').read_bytes()).hexdigest() == checkpoint['episodes_sha256']
    assert manifest['script_sha256'] == hashlib.sha256(Path(policy.__file__).read_bytes()).hexdigest()
    assert manifest['personas'] == policy.TRAITS and manifest['rules'] == policy.RULES
    a.out.mkdir(parents=True, exist_ok=False)
    manifest.update(case_ids=ids, driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        prefix_directory=str(a.prefix), prefix_checkpoint=checkpoint,
        arguments={**manifest['arguments'], 'out': str(a.out), 'shard': a.shard, 'shards': a.shards})
    (a.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    policy.base.PERSONAS.clear(); policy.base.PERSONAS.update(policy.TRAITS)
    modules = policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    seeds = manifest['arguments']['seeds']
    client = policy.base.BatchClient(Path(manifest['arguments']['model']), a.out, seeds[0])
    start = time.monotonic(); count = 0; worlds = 0
    for group in groups:
        count += policy.run_group(group, seeds, client, modules, a.out); worlds += len(group)
        print(json.dumps({'worlds_completed': worlds, 'episodes': count, 'calls': client.calls,
                          'wall_seconds': time.monotonic()-start}), flush=True)
    expected = sum(len(r['requests']) for group in groups for r in group)*len(seeds)*len(policy.TRAITS)*len(policy.RULES)
    assert count == expected
    (a.out/'runtime.json').write_text(json.dumps({'worlds': worlds, 'episodes': count, 'calls': client.calls,
        'wall_seconds': time.monotonic()-start, 'model_load_seconds': client.load_seconds,
        'cloud_calls': 0}, indent=2)+'\n')


if __name__ == '__main__': main()
