#!/usr/bin/env python3
"""E63 paired native outcomes; average seeds before bootstrapping worlds."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from commitment_behavior_report import estimate


FIELDS = ['target_given_before_goal', 'goal_executed', 'request_given',
          'both_completed', 'unresolved', 'handover_without_goal',
          'goal_executed_after_pre_goal_handover', 'protocol_error', 'steps',
          'request_before_original_goal_POST_HOC']


def values(row):
    first_request = next((i for i, h in enumerate(row['history']) if h['request_given_after']), None)
    first_goal = next((i for i, h in enumerate(row['history']) if h['goal_executed_after']), None)
    before_goal = first_request is not None and (first_goal is None or first_request < first_goal)
    return {
        **{f: float(row[f]) for f in FIELDS if f in row and f != 'protocol_error'},
        'unresolved': float(not row['goal_executed'] and not row['request_given']),
        'handover_without_goal': float(row['request_given'] and not row['goal_executed']),
        'goal_executed_after_pre_goal_handover': float(row['target_given_before_goal'] and row['goal_executed']),
        'protocol_error': float(bool(row['protocol_error'])),
        'request_before_original_goal_POST_HOC': float(before_goal),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--directories', type=Path, nargs='+', required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--partial', action='store_true')
    ap.add_argument('--prefix-directory', type=Path)
    a = ap.parse_args()
    manifests, rows, runtimes, calls, assigned = [], [], [], [], set()
    directories = ([a.prefix_directory] if a.prefix_directory else []) + a.directories
    for d in directories:
        m = json.loads((d / 'manifest.json').read_text())
        if d == a.prefix_directory:
            checkpoint = json.loads((d/'interrupted_runtime.json').read_text())
            assert hashlib.sha256((d/'episodes.jsonl').read_bytes()).hexdigest() == checkpoint['episodes_sha256']
            m['case_ids'] = sorted({r['case_id'] for r in map(json.loads, (d/'episodes.jsonl').read_text().splitlines())})
        assert not assigned.intersection(m['case_ids']), 'overlapping shards'
        assigned.update(m['case_ids']); manifests.append(m)
        if (d / 'runtime.json').exists():
            runtimes.append(json.loads((d / 'runtime.json').read_text()))
        elif d == a.prefix_directory:
            runtimes.append(checkpoint)
        elif not a.partial:
            raise AssertionError(f'incomplete worker: {d}')
        for filename, target in [('episodes.jsonl', rows), ('model_calls.jsonl', calls)]:
            if (d / filename).exists():
                for line in (d / filename).read_text().splitlines():
                    try:
                        target.append(json.loads(line))
                    except json.JSONDecodeError:
                        if not a.partial: raise
        if m.get('resumed_worker_from'):
            previous = list(map(json.loads, (Path(m['resumed_worker_from'])/'model_calls.jsonl').read_text().splitlines()))
            assert len(previous) == m['prior_worker_runtime']['calls']
            calls.extend(previous)
    ref = manifests[0]
    for m in manifests:
        for k in ['dataset_sha256', 'script_sha256', 'personas', 'rules', 'max_action_steps']:
            assert m[k] == ref[k], k
        for k in ['model', 'seeds', 'dataset']:
            assert m['arguments'][k] == ref['arguments'][k], k
    cases = {r['case']['case_id']: r for r in map(json.loads, Path(ref['arguments']['dataset']).read_text().splitlines())}
    lookup = {(r['case_id'], r['seed'], r['persona'], r['rule'], r['mode']): r for r in rows}
    assert len(lookup) == len(rows), 'duplicate episode keys'
    seeds, personas, rules = ref['arguments']['seeds'], list(ref['personas']), list(ref['rules'])
    expected = {(cid, s, p, rule, mode) for cid in assigned for s in seeds
                for p in personas for rule in rules for mode in cases[cid]['requests']}
    assert set(lookup).issubset(expected)
    if not a.partial:
        assert assigned == set(cases) and set(lookup) == expected
    # Partial runs include only entire completed worlds, never outcome-selected rows.
    complete = {cid for cid in assigned if all(k in lookup for k in expected if k[0] == cid)}
    paired = {cid for cid in complete if 'other_item' in cases[cid]['requests']}
    data = {k: values(r) for k, r in lookup.items()}
    report = {'status': 'PARTIAL' if a.partial else 'COMPLETE', 'manifests': manifests,
              'runtimes': runtimes, 'episodes': len(rows), 'expected_episodes': len(expected),
              'complete_worlds': len(complete), 'paired_worlds': len(paired),
              'missing_keys': len(expected - set(lookup)), 'cells': {},
              'persona_contrasts': {}, 'rule_contrasts': {}, 'asset_contrasts': {},
              'persona_by_asset_interactions': {}, 'conversation_stances': {},
              'paired_persona_outcomes': {},
              'protocol_errors': sum(bool(r['protocol_error']) for r in rows),
              'engine_rejections': dict(Counter(h.get('error', 'unspecified') for r in rows
                  for h in r['history'] if not h['legal'])),
              'native_stochastic_failures': sum(bool(h.get('stochastic_failure')) for r in rows for h in r['history'])}

    def cell(gs, mode, p, rule):
        return {f: estimate([np.mean([data[cid, s, p, rule, mode][f] for s in seeds])
                             for cid in sorted(gs)]) for f in FIELDS}

    def contrast(gs, left, right):
        return {f: estimate([np.mean([data[(cid, s, *left)][f] - data[(cid, s, *right)][f]
                                      for s in seeds]) for cid in sorted(gs)]) for f in FIELDS}

    for mode, gs in [('goal_item', complete), ('other_item', paired)]:
        for rule in rules:
            for p in personas:
                report['cells'][f'{mode}/{rule}/{p}'] = cell(gs, mode, p, rule)
                report['conversation_stances'][f'{mode}/{rule}/{p}'] = dict(Counter(
                    (lookup[cid, s, p, rule, mode]['conversation'] or {}).get('stance', 'protocol_error')
                    for cid in gs for s in seeds))
            report['persona_contrasts'][f'{mode}/{rule}'] = contrast(gs,
                ('agreeable', rule, mode), ('firm', rule, mode))
            def endpoint(row):
                return ('both' if row['both_completed'] else 'original_goal_only' if row['goal_executed']
                        else 'request_only' if row['request_given'] else 'neither')
            report['paired_persona_outcomes'][f'{mode}/{rule}'] = dict(Counter(
                endpoint(lookup[cid, s, 'firm', rule, mode])+' -> '+endpoint(lookup[cid, s, 'agreeable', rule, mode])
                for cid in gs for s in seeds))
        for p in personas:
            for rule in rules:
                if rule != 'none':
                    report['rule_contrasts'][f'{mode}/{p}/{rule}-minus-none'] = contrast(gs,
                        (p, rule, mode), (p, 'none', mode))
    # Within-world item comparisons use exactly the 100 qualified pairs.
    for rule in rules:
        for p in personas:
            report['asset_contrasts'][f'{p}/{rule}/goal-minus-other'] = contrast(paired,
                (p, rule, 'goal_item'), (p, rule, 'other_item'))
        report['persona_by_asset_interactions'][rule] = {f: estimate([
            np.mean([data[cid, s, 'agreeable', rule, 'goal_item'][f]
                     - data[cid, s, 'firm', rule, 'goal_item'][f]
                     - data[cid, s, 'agreeable', rule, 'other_item'][f]
                     + data[cid, s, 'firm', rule, 'other_item'][f] for s in seeds])
            for cid in sorted(paired)]) for f in FIELDS}
    report['qualification_strata'] = {}
    for legal in [False, True]:
        gs = {cid for cid in complete if cases[cid]['requests']['goal_item']['original_goal_immediately_legal_after_give'] == legal}
        label = 'substitute_remains' if legal else 'immediate_goal_blocked'
        report['qualification_strata'][label] = {'worlds': len(gs), 'cells': {
            f'{p}/{rule}': cell(gs, 'goal_item', p, rule) for p in personas for rule in rules}}
    report['calls'] = {'count': len(calls), 'parse_errors': sum(bool(r['parse_error']) for r in calls),
        'prompt_tokens': sum(r['prompt_tokens'] for r in calls),
        'completion_tokens': sum(r['completion_tokens'] for r in calls)}
    if not a.partial:
        assert len(calls) == sum(rt['calls'] + rt.get('prior_run', {}).get('calls', 0) for rt in runtimes)
    report['raw_sha256'] = {str(d): hashlib.sha256((d / 'episodes.jsonl').read_bytes()).hexdigest()
                             for d in directories if (d / 'episodes.jsonl').exists()}
    report['scope'] = ['Native task event and requested item IDs are separate physical readouts.',
        'Other items need not be worthless for broader goals; this is not a randomized utility intervention.',
        'Give before goal and eight-step failure are not permanent utility destruction; recovery remains legal.',
        'Critical-item branches stop at actual original task execution; other-item branches continue to measure both events.',
        'POST-HOC symmetric request_before_original_goal uses event order in both item conditions; total request_given has different post-goal observation windows.',
        'target_given_before_goal is the original goal-item-only flag; its other-item value is structurally zero, not a symmetric cooperation measure.',
        'Rules are ordinary strong prompt controls, not a new alignment method.',
        'Partial completed worlds follow the frozen source order, not random interim population samples.']
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'episodes', 'complete_worlds', 'paired_worlds',
        'missing_keys', 'protocol_errors', 'native_stochastic_failures', 'calls']}))


if __name__ == '__main__': main()
