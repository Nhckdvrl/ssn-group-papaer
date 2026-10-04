"""CPU-only reconciliation of original terminal evaluations and wrapper failures.

Does not launch inference or training. Keeps the failed coordinator and worker
records, verifies all original outputs, and emits an explicitly reconciled state.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import shlex
import subprocess
import time

from e12_validate_eval import validate_results

REMOTE = '/var/tmp/xiang-data-rsi/closeout/attempt1'
NAMES = [(e, f'{p}_{a}_s29', node) for e, actions, node in (
    ('E13', ('replay', 'fresh_selected', 'fresh_law'), 'fvcrc13'),
    ('E14', ('source_only_fresh',), 'fvcrc10'))
    for p in ('init', 'used') for a in actions]


def fetch(node, path):
    return subprocess.check_output(['ssh', node, shlex.join(['cat', path])])


def save(path, data):
    if path.exists():
        assert path.read_bytes() == data, f'Existing artifact differs: {path}'
    else:
        with path.open('xb') as f:
            f.write(data)


def encode(obj): return (json.dumps(obj, indent=2) + '\n').encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    args = parser.parse_args(); out = args.results
    raw_state = fetch('fvcrc20', REMOTE + '/state.json')
    original = json.loads(raw_state)
    assert original.get('finished_utc') and not original['active']
    # The live observer opens its file for writing; wait for its final record
    # before appending the supplemental retry submission.
    schedule_path = out/'E13_E14_closeout_schedule.jsonl'
    deadline = time.monotonic() + 30
    while True:
        records = [json.loads(line) for line in schedule_path.read_text().splitlines()]
        if any(r['status'] == original['status'] and not r['active'] and len(r['completed_names']) == 8 for r in records):
            break
        assert time.monotonic() < deadline, 'Schedule observer has not recorded coordinator termination'
        time.sleep(1)
    save(out/'E13_E14_original_closeout_state.json', raw_state)
    cleanup = {'nodes': {node: [] for node in ('fvcrc20', 'fvcrc13', 'fvcrc10')}}
    audit = {'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
             'original_coordinator_status': original['status'],
             'scope': 'CPU validation only; no additional training or inference',
             'numeric_tolerance_absolute': 1e-12, 'runs': []}
    rows = []
    for experiment, name, node in NAMES:
        base = REMOTE + '/' + name
        raw_worker = fetch(node, base + '/result.json')
        worker = json.loads(raw_worker)
        save(out/f'{experiment}_{name}_original_worker_result.json', raw_worker)
        assert worker['returncode'] == 0
        payloads = {suffix: fetch(node, base + '/eval/' + filename)
                    for suffix, filename in (
                        ('raw_results', 'results/results.json'),
                        ('validated_scores', 'validated_scores.json'),
                        ('eval_manifest', 'eval_manifest.json'),
                        ('completion', 'completion.json'))}
        completion = json.loads(payloads['completion'])
        assert completion['status'] == 'completed' and completion['error'] is None
        actual = validate_results(json.loads(payloads['raw_results']))
        saved = json.loads(payloads['validated_scores'])
        assert math.isclose(actual['accuracy_percent'], saved['accuracy_percent'], rel_tol=0, abs_tol=1e-12)
        assert set(actual['benchmarks']) == set(saved['benchmarks'])
        for benchmark, row in actual['benchmarks'].items():
            other = saved['benchmarks'][benchmark]
            assert row['field'] == other['field']
            assert all(math.isclose(row[k], other[k], rel_tol=0, abs_tol=1e-12)
                       for k in ('raw', 'max', 'normalized'))
        manifest = json.loads(payloads['eval_manifest'])
        assert manifest['gpu'] == worker['launch']['gpu']
        assert manifest['judge_url'] == 'http://fvcrc20:8034/v1/chat/completions'
        assert manifest['use_vllm'] and set(manifest['benchmarks']) == set(actual['benchmarks'])
        log_audit = {}
        for filename in ('eval_stdout.txt', 'eval_stderr.txt'):
            blob = fetch(node, base + '/eval/' + filename)
            assert b'will use exact matching for evaluation' not in blob
            log_audit[filename] = {'bytes': len(blob), 'sha256': hashlib.sha256(blob).hexdigest(), 'no_exact_matching_fallback': True}
        guard = json.loads(fetch(node, base + '/descendant_guard.json'))
        assert guard['cleanup_complete'] and not guard['active_pids']
        cleanup['nodes'][node].append({'name': name, **guard})
        for suffix, blob in payloads.items():
            save(out/f'{experiment}_{name}_{suffix}.json', blob)
        audit['runs'].append({'name': name, 'original_worker_status': worker['status'],
                              'original_worker_error': worker.get('error'), 'logs': log_audit,
                              'mean_recompute_difference': actual['accuracy_percent']-saved['accuracy_percent'],
                              'validation_accepted': True})
        reconciled = {**worker, 'original_worker_status': worker['status'],
                      'original_worker_error': worker.get('error'),
                      'status': 'completed', 'validation_accepted': True,
                      'scores': saved, 'completion': completion}
        reconciled.pop('error', None)
        rows.append(reconciled)
    guard = json.loads(fetch('fvcrc20', REMOTE + '/judge/descendant_guard.json'))
    assert guard['cleanup_complete'] and not guard['active_pids']
    cleanup['nodes']['fvcrc20'].append({'name': 'judge', **guard})
    save(out/'E13_E14_descendant_cleanup.json', encode(cleanup))
    save(out/'E13_E14_closeout_validation_reconciliation.json', encode(audit))
    state = {**original, 'original_coordinator_status': original['status'],
             'original_coordinator_error': original.get('error'),
             'original_coordinator_state_file': 'E13_E14_original_closeout_state.json',
             'status': 'eight_evaluations_completed', 'runs': rows,
             'reconciliation_audit': 'E13_E14_closeout_validation_reconciliation.json'}
    state.pop('error', None)
    save(out/'E13_E14_closeout_state.json', encode(state))
    retry = json.loads(fetch('fvcrc13', REMOTE + '/used_fresh_law_s29_operational_retry_launch.json'))
    save(out/'E13_used_fresh_law_s29_operational_retry_launch.json', encode(retry))
    schedule_path = out/'E13_E14_closeout_schedule.jsonl'
    with schedule_path.open('a') as f:
        f.write(json.dumps({'observed_utc': audit['generated_utc'], 'status': 'operational_retry_schedule_reconstruction',
                            'active': [{'name': 'used_fresh_law_s29', 'experiment': 'E13', 'node': 'fvcrc13', 'gpu': 0,
                                        'submitted_utc': retry['started_utc'], 'cap_seconds': 5444}],
                            'completed_names': []}) + '\n')
    print(json.dumps({'validated_terminals': len(rows), 'original_coordinator_status': original['status']}))


if __name__ == '__main__': main()
