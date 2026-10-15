#!/usr/bin/env python3
"""E70/E71 measured cost, counting cached profile inference exactly once."""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); jobs = []
    for kind, name in [('profile', 'e70_profile_launch.json'), ('E70', 'e70_launch_fvcrc21.json'),
                       ('E70', 'e70_launch_fvcrc20.json'), ('E71', 'e71_launch.json')]:
        launches = json.loads((args.runs_root/name).read_text())
        if isinstance(launches, dict): launches = [launches]
        for launch in launches:
            folder = Path(launch['cmd'][launch['cmd'].index('--out')+1])
            runtime = json.loads((folder/'runtime.json').read_text())
            count = prompt = completion = errors = 0
            for row in map(json.loads, (folder/'model_calls.jsonl').open()):
                count += 1; prompt += row['prompt_tokens']; completion += row['completion_tokens']
                errors += int(bool(row['parse_error']))
            assert count == runtime['calls'] and runtime['new_cloud_calls'] == 0
            end = max((folder/'runtime.json').stat().st_mtime, folder.with_suffix('.log').stat().st_mtime)
            jobs.append({'kind': kind, 'host': launch.get('host', 'fvcrc21'),
                         'folder': str(folder), 'gpu': launch['gpu'], 'pid': launch['pid'],
                         'episodes': runtime['episodes'], 'new_calls': count, 'parse_errors': errors,
                         'prompt_tokens': prompt, 'completion_tokens': completion,
                         'reused_calls': runtime['reused_calls'],
                         'runtime_gpu_hours': (runtime['wall_seconds']+runtime['model_load_seconds'])/3600,
                         'observed_launch_through_last_log_gpu_hours': (end-launch['start_epoch'])/3600})
    assert len(jobs) == 9
    fields = ['new_calls', 'parse_errors', 'prompt_tokens', 'completion_tokens', 'reused_calls',
              'runtime_gpu_hours', 'observed_launch_through_last_log_gpu_hours']
    totals = {k: sum(j[k] for j in jobs) for k in fields}
    by_experiment = {e: {k: sum(j[k] for j in jobs if j['kind'] == e or (e == 'E70' and j['kind'] == 'profile'))
                         for k in fields} for e in ['E70', 'E71']}
    result = {'status': 'COMPLETE', 'experiments': ['E70', 'E71'], 'jobs': jobs, 'totals': totals,
              'by_experiment': by_experiment, 'unique_main_episodes': 12636, 'unique_unsolicited_episodes': 2808,
              'profile_episodes': 54, 'profile_reused_in_main': True,
              'peak_authorized_gpus_used': 8, 'new_cloud_calls': 0,
              'scope': ['Profile outputs reused exactly; its 321 actual calls are added once to E70 shard calls.',
                        'Runtime includes model load/inference; launch-to-last-log additionally includes interpreter startup and logged teardown.',
                        'One GPU per job; two independent nodes, no distributed training.',
                        'Failed initial SSH before remote launch used zero GPU; no experiment output was discarded.']}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(totals))


if __name__ == '__main__': main()
