#!/usr/bin/env python3
"""E69 actual inference and observed launch-to-shutdown cost, including profile."""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    jobs = []
    for kind, name in [('profile', 'e69_profile_launch.json'),
                       ('main', 'e69_main_launch.json'),
                       ('adaptive', 'e69_controls_launch.json')]:
        launches = json.loads((args.runs_root/name).read_text())
        if isinstance(launches, dict):
            launches = [launches]
        for launch in launches:
            folder = Path(launch['cmd'][launch['cmd'].index('--out')+1])
            runtime = json.loads((folder/'runtime.json').read_text())
            calls = tokens_in = tokens_out = errors = 0
            for row in map(json.loads, (folder/'model_calls.jsonl').open()):
                calls += 1
                tokens_in += row['prompt_tokens']
                tokens_out += row['completion_tokens']
                errors += int(bool(row['parse_error']))
            assert calls == runtime['calls'] and runtime['cloud_calls'] == 0
            end = max((folder/'runtime.json').stat().st_mtime,
                      folder.with_suffix('.log').stat().st_mtime)
            jobs.append({'kind': kind, 'folder': str(folder), 'gpu': launch['gpu'],
                         'pid': launch['pid'], 'episodes': runtime['episodes'],
                         'new_calls': calls, 'parse_errors': errors,
                         'prompt_tokens': tokens_in, 'completion_tokens': tokens_out,
                         'runtime_gpu_hours': (runtime['wall_seconds']+runtime['model_load_seconds'])/3600,
                         'observed_launch_through_last_log_gpu_hours': (end-launch['start_epoch'])/3600})
    assert len(jobs) == 7
    totals = {key: sum(row[key] for row in jobs) for key in
              ['new_calls', 'parse_errors', 'prompt_tokens', 'completion_tokens',
               'runtime_gpu_hours', 'observed_launch_through_last_log_gpu_hours']}
    result = {'status': 'COMPLETE', 'experiment': 'E69', 'jobs': jobs, 'totals': totals,
              'main_branches': 2760, 'adaptive_branches': 144,
              'profile_branches': 12, 'profile_reused_in_main': True,
              'peak_authorized_gpus_used': 4, 'new_cloud_calls': 0,
              'scope': ['Runtime includes model load and recorded inference, but excludes initial Python/import startup.',
                        'Observed launch-to-last-log time additionally includes startup and logged engine teardown; one GPU per job.',
                        'Profile calls count once; cached E68/profile outputs are not new inference calls.',
                        'Known-world branches and three seeds do not increase the number of independent source worlds.']}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(totals))


if __name__ == '__main__':
    main()
