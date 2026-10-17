#!/usr/bin/env python3
"""E71 no-request baseline and graph-paired comparison with fixed E70 cells."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from native_request_precondition_execution import SEEDS
from native_request_precondition_report import metrics
from native_rule_cross_report import summarize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--solicited-runs', type=Path, nargs='+')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    sources = {r['case']['case_id']: r for r in map(json.loads, args.data.open())}
    manifest = json.loads((args.run/'manifest.json').read_text())
    runtime = json.loads((args.run/'runtime.json').read_text())
    lookup = {}
    for row in map(json.loads, (args.run/'episodes.jsonl').open()):
        key = row['case_id'], row['seed'], row['persona'], row['condition']
        assert key not in lookup and row['conversation'] is None and row['requester_id'] is None
        lookup[key] = row
    expected = {(cid, s, p, state+'_unsolicited') for cid in sources for s in SEEDS
                for p in ['firm', 'agreeable'] for state in ['ready', 'equipped']}
    assert set(lookup) == expected and len(lookup) == 1404
    assert manifest['source_data_sha256'] == hashlib.sha256(args.data.read_bytes()).hexdigest()
    calls = Counter()
    for row in map(json.loads, (args.run/'model_calls.jsonl').open()):
        calls.update(count=1, parse_errors=int(bool(row['parse_error'])),
                     prompt_tokens=row['prompt_tokens'], completion_tokens=row['completion_tokens'])
    assert calls['count'] == runtime['calls']
    source_files = {str(args.run/'episodes.jsonl'): hashlib.sha256((args.run/'episodes.jsonl').read_bytes()).hexdigest()}
    if args.solicited_runs:
        for folder in args.solicited_runs:
            assert (folder/'runtime.json').exists()
            m = json.loads((folder/'manifest.json').read_text())
            assert m['model'] == manifest['model'] and m['data_sha256'] == manifest['source_data_sha256']
            for row in map(json.loads, (folder/'episodes.jsonl').open()):
                if row['condition'] not in ['ready_aligned', 'ready_divert', 'equipped_aligned', 'equipped_divert']:
                    continue
                key = row['case_id'], row['seed'], row['persona'], row['condition']
                assert key not in lookup
                lookup[key] = row
            source_files[str(folder/'episodes.jsonl')] = hashlib.sha256((folder/'episodes.jsonl').read_bytes()).hexdigest()
        assert len(lookup) == 4212
    values = {k: metrics(r) for k, r in lookup.items()}
    fields = [f for f in next(iter(values.values())) if not f.startswith('stance_') and f != 'to_requester']

    def estimate(terms):
        matrix = [np.mean([[sum(w*values[cid, seed, p, cond][f] for w, p, cond in terms)
                            for f in fields] for seed in SEEDS], axis=0) for cid in sorted(sources)]
        return summarize(matrix, fields)

    cells = {}; contrasts = {}; changes = {}
    for state in ['ready', 'equipped']:
        for persona in ['firm', 'agreeable']:
            cells[persona+'/'+state+'_unsolicited'] = estimate([(1, persona, state+'_unsolicited')])
        contrasts['A_minus_F/'+state+'_unsolicited'] = estimate([(1, 'agreeable', state+'_unsolicited'), (-1, 'firm', state+'_unsolicited')])
        if args.solicited_runs:
            for direction in ['aligned', 'divert']:
                cond = state+'_'+direction; base = state+'_unsolicited'
                for persona in ['firm', 'agreeable']:
                    cells[persona+'/'+cond] = estimate([(1, persona, cond)])
                    contrasts[persona+'/'+direction+'_minus_unsolicited/'+state] = estimate([(1, persona, cond), (-1, persona, base)])
                    counter = Counter()
                    for cid in sources:
                        for seed in SEEDS:
                            a, b = values[cid, seed, persona, base], values[cid, seed, persona, cond]
                            for f in ['to_goal', 'to_competitor', 'no_transfer']:
                                counter[f+'/gained'] += int(b[f] > a[f])
                                counter[f+'/lost'] += int(b[f] < a[f])
                    changes[persona+'/'+cond] = dict(counter)
                contrasts['persona_x_'+direction+'_vs_unsolicited/'+state] = estimate([
                    (1, 'agreeable', cond), (-1, 'firm', cond), (-1, 'agreeable', base), (1, 'firm', base)])
    for persona in ['firm', 'agreeable']:
        contrasts[persona+'/equipped_minus_ready/unsolicited'] = estimate([
            (1, persona, 'equipped_unsolicited'), (-1, persona, 'ready_unsolicited')])
        if args.solicited_runs:
            for direction in ['aligned', 'divert']:
                contrasts[persona+'/secondary_context_x_state/'+direction] = estimate([
                    (1, persona, 'equipped_'+direction), (-1, persona, 'equipped_unsolicited'),
                    (-1, persona, 'ready_'+direction), (1, persona, 'ready_unsolicited')])
    result = {'status': 'COMPLETE', 'experiment': 'E70+E71' if args.solicited_runs else 'E71',
              'model': manifest['model'], 'worlds': len(sources), 'unsolicited_episodes': 1404,
              'total_compared_episodes': len(lookup), 'cells': cells, 'contrasts': contrasts,
              'paired_outcome_changes': changes, 'unsolicited_actual_calls': dict(calls),
              'unsolicited_runtime_gpu_hours': (runtime['wall_seconds']+runtime['model_load_seconds'])/3600,
              'runtime': runtime, 'source_sha256': source_files,
              'data_sha256': manifest['source_data_sha256'],
              'scope': ['Absence of both solicitation and generated dialogue is a context-package baseline, not a single-token intervention.',
                        'Authored recipient and selected source item unchanged; first Give stopping and eight-action horizon match E70.',
                        'No-request stance/requester metrics are inapplicable and omitted.',
                        'Context-by-state is a secondary derived contrast added during collection; primary outcomes/cells unchanged.',
                        'Three seeds averaged within each of 117 graphs; 4000 paired graph bootstrap samples; pointwise intervals.']}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['status', 'experiment', 'worlds', 'total_compared_episodes', 'unsolicited_actual_calls']}), flush=True)


if __name__ == '__main__':
    main()
