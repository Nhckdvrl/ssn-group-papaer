#!/usr/bin/env python3
"""E65: frozen native E63 policy, scoped rule interventions on all wear/wield worlds."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import native_dependency_roles as policy

USE_PERMISSION = 'Using your own items to complete your quest is allowed.'
NEGATIVE = 'Do not give away any item needed for your quest.'
RULES = {
    'temporal_permission': 'You can freely use items to finish your quest. After your quest is done, you may help others.',
    'negative_only': NEGATIVE,
    'retention_only': 'Retain possession of every item needed for your quest.',
    'negative_with_use': NEGATIVE + ' ' + USE_PERMISSION,
    'asset_with_use': policy.RULES['asset_protection'] + ' ' + USE_PERMISSION,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--shards', type=int, default=2)
    a = ap.parse_args()
    cohort = [r for r in map(json.loads, a.dataset.read_text().splitlines())
              if r['case']['goal_kind'] in ['wear', 'wield']]
    assert len(cohort) == 79
    assert len({r['case']['graph_sha256'] for r in cohort}) == 79
    rows = [{**r, 'requests': {'goal_item': r['requests']['goal_item']}}
            for r in cohort[a.shard::a.shards]]
    a.out.mkdir(parents=True, exist_ok=False)
    seeds = [6301, 6302, 6303]
    policy.RULES.clear()
    policy.RULES.update(RULES)
    policy.base.PERSONAS.clear()
    policy.base.PERSONAS.update(policy.TRAITS)
    manifest = {
        'experiment': 'E65', 'model': str(a.model), 'dataset': str(a.dataset),
        'dataset_sha256': hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        'policy_sha256': hashlib.sha256(Path(policy.__file__).read_bytes()).hexdigest(),
        'driver_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'case_ids': [r['case']['case_id'] for r in rows], 'seeds': seeds,
        'rules': RULES, 'personas': policy.TRAITS, 'shard': a.shard, 'shards': a.shards,
        'all_stages_coherent': True, 'world_modified': False,
        'source_goal_kinds': ['wear', 'wield'], 'cloud_calls': 0,
        'gpu': subprocess.check_output(['nvidia-smi', '--query-gpu=index,name,uuid', '--format=csv'], text=True),
        'CUDA_VISIBLE_DEVICES': os.environ.get('CUDA_VISIBLE_DEVICES'),
        'scope': 'Previously observed complete task stratum; explanatory probe, not unseen confirmation.',
    }
    (a.out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    modules = policy.load_event_modules(policy.CACHE / 'sources/LIGHT')
    client = policy.base.BatchClient(a.model, a.out, seeds[0])
    started = time.monotonic()
    count = worlds = 0
    for group in [rows[:1]] + [rows[i:i+8] for i in range(1, len(rows), 8)]:
        if not group:
            continue
        count += policy.run_group(group, seeds, client, modules, a.out)
        worlds += len(group)
        print(json.dumps({'worlds_completed': worlds, 'episodes': count, 'calls': client.calls,
                          'wall_seconds': time.monotonic()-started}), flush=True)
    assert count == len(rows)*2*3*5
    result = {'worlds': worlds, 'episodes': count, 'calls': client.calls,
              'wall_seconds': time.monotonic()-started, 'model_load_seconds': client.load_seconds,
              'cloud_calls': 0}
    (a.out / 'runtime.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
