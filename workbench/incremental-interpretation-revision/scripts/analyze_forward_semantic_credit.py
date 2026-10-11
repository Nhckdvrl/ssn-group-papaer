"""E95 complete-only actual semantic comparisons versus frozen reconstruction ranks."""
import argparse
import collections
import json
from pathlib import Path
import time

from data import sha
from current_open_baseline import MODELS
from forward_semantic_credit import rank
from analyze_correct_answer_carry import estimate


def analyze(root, selected_models=None, output_name='forward-semantic-credit-map-v1.json', manifest_name='complete-map-v1.json'):
    models = MODELS if selected_models is None else selected_models
    assert models and set(models) <= set(MODELS)
    data = root / 'data-v1.jsonl'
    rows = [json.loads(s) for s in data.read_text().splitlines()]
    meta = {r['item_id']: r for r in rows}
    index, raw, provenance = {}, {}, []
    for experiment, target in [('E91', raw), ('E95', index)]:
        parent = root.parent / experiment
        for run in json.loads((parent / 'runner-pids-v1.json').read_text()):
            if run['model'] not in models:
                continue
            out = Path(run['out'])
            cfg = json.loads((out / 'config.json').read_text())
            assert cfg['predictions_sha256'] == sha(out / 'predictions.jsonl')
            assert cfg['data_sha256'] == sha(parent / 'data-v1.jsonl')
            assert cfg['model_manifest_sha256'] == sha(root.parent / 'models' / run['model'] / 'manifest.json')
            ps = [json.loads(s) for s in (out / 'predictions.jsonl').read_text().splitlines()]
            assert len(ps) == cfg['tasks']
            for p in ps:
                if experiment == 'E95':
                    r = meta[p['item_id']]
                    assert int(r['sentence_sha256'][:16], 16) % run['shards'] == run['shard']
                    expected_order = ['BASE_BANK', 'TARGET_BANK'] if p['order_index'] == 0 else ['TARGET_BANK', 'BASE_BANK']
                    assert p['candidate_order'] == expected_order
                    key = run['model'], p['item_id'], p['mode'], p['order_index']
                else:
                    assert abs(sum(p['token_logprobs']) - p['reward_sum']) < 1e-8
                    key = run['model'], p['item_id']
                assert key not in target
                target[key] = p
            provenance.append(dict(experiment=experiment, model=run['model'], shard=run['shard'],
                                   config_sha256=sha(out / 'config.json'), predictions_sha256=cfg['predictions_sha256'],
                                   gpu_hours=cfg['gpu_hours'], code_sha256=cfg['code_sha256']))
    expected = {(m, r['item_id'], mode, o) for m in models for r in rows
                for mode in ['NATIVE', 'RECOVERY'] for o in [0, 1]}
    assert set(index) == expected and len(raw) == 648 * len(models)
    records = []
    for grader in models:
        for r in rows:
            b, t = [raw[grader, r['E91_item_ids'][k]] for k in ['BASE_BANK', 'TARGET_BANK']]
            assert b['observation_tokens'] == t['observation_tokens']
            rr = rank(b['reward_sum'], t['reward_sum'])
            for mode in ['NATIVE', 'RECOVERY']:
                for order in [0, 1]:
                    p = index[grader, r['item_id'], mode, order]
                    ar = None
                    if p['answer'] == 'c':
                        ar = 0
                    elif p['answer'] in ['a', 'b']:
                        selected = p['candidate_order'][0 if p['answer'] == 'a' else 1]
                        ar = 1 if selected == 'TARGET_BANK' else -1
                    z = dict(r, grader=grader, mode=mode, order_index=order,
                             raw_rank=rr, actual_rank=ar, actual_stopped=p['stopped'],
                             actual_unknown=ar is None, actual_capped=p['capped'],
                             actual_tokens=len(p['output_tokens']), metrics={})
                    for reference in ['fidelity', 'pattern']:
                        gold = r[reference + '_rank']
                        if gold is None:
                            continue
                        lo = float(p['stopped'] and ar == gold)
                        hi = float(not p['stopped'] or ar is None or ar == gold)
                        rc = float(rr == gold)
                        z['metrics'][reference] = dict(actual_lower_correct=lo, actual_upper_correct=hi,
                            raw_correct=rc, actual_minus_raw_lower=lo-rc, actual_minus_raw_upper=hi-rc,
                            actual_correct_raw_wrong=float(lo and not rc),
                            actual_wrong_raw_correct=float(p['stopped'] and ar is not None and ar != gold and rc),
                            actual_opposes=float(p['stopped'] and ar is not None and gold * ar < 0),
                            raw_opposes=float(gold * rr < 0),
                            actual_tie=float(p['stopped'] and ar == 0), raw_tie=float(rr == 0),
                            unknown=float(ar is None), capped=float(p['capped']))
                    records.append(z)
    panels, counts = [], []
    for grader in models:
        for mode in ['NATIVE', 'RECOVERY']:
            cohort = [r for r in records if r['grader'] == grader and r['mode'] == mode]
            groups = {'all': cohort}
            for field in ['generator', 'construction', 'condition', 'order_index', 'fidelity_rank', 'pattern_rank', 'identical_interpretations']:
                for value in sorted({str(r[field]) for r in cohort}):
                    groups[field + ':' + value] = [r for r in cohort if str(r[field]) == value]
            for g in sorted({r['generator'] for r in cohort}):
                for c in ['gp', 'control']:
                    for ct in ['ALL', 'MVRR', 'NPZ', 'NPS']:
                        groups[f'generator:{g}|condition:{c}|construction:{ct}'] = [
                            r for r in cohort if r['generator'] == g and r['condition'] == c
                            and (ct == 'ALL' or r['construction'] == ct)]
            for group, selected in groups.items():
                counts.append(dict(grader=grader, mode=mode, group=group, outputs=len(selected),
                    pairs=len({r['item_id'] for r in selected}),
                    fidelity_eligible_outputs=sum('fidelity' in r['metrics'] for r in selected),
                    actual_rank_counts=dict(collections.Counter(str(r['actual_rank']) for r in selected)),
                    unknown=sum(r['actual_unknown'] for r in selected), capped=sum(r['actual_capped'] for r in selected)))
                for reference in ['fidelity', 'pattern']:
                    eligible = [r for r in selected if reference in r['metrics']]
                    subsets = {'all_eligible': eligible, 'changed_DIAGNOSTIC': [r for r in eligible if r[reference+'_rank'] != 0],
                               'ties_DIAGNOSTIC': [r for r in eligible if r[reference+'_rank'] == 0]}
                    for subset, rs in subsets.items():
                        if not rs:
                            continue
                        for metric in rs[0]['metrics'][reference]:
                            panels.append(dict(grader=grader, mode=mode, group=group, reference=reference,
                                subset=subset, metric=metric,
                                **estimate(rs, [r['metrics'][reference][metric] for r in rs], seed=95)))
    # The recovery contrast is paired on exactly the same item and candidate order.
    ri = {(r['grader'], r['item_id'], r['mode'], r['order_index']): r for r in records}
    for grader in models:
        for reference in ['fidelity', 'pattern']:
            rs = [r for r in records if r['grader'] == grader and r['mode'] == 'NATIVE' and reference in r['metrics']]
            for condition in ['ALL', 'gp', 'control']:
                sub = [r for r in rs if condition == 'ALL' or r['condition'] == condition]
                for bound in ['lower', 'upper']:
                    values = []
                    for r in sub:
                        rec = ri[grader, r['item_id'], 'RECOVERY', r['order_index']]['metrics'][reference]
                        nat = r['metrics'][reference]
                        values.append(rec['actual_'+bound+'_correct'] - nat['actual_'+('upper' if bound == 'lower' else 'lower')+'_correct'])
                    panels.append(dict(grader=grader, mode='RECOVERY-minus-NATIVE', group='condition:'+condition,
                        reference=reference, subset='all_eligible', metric=bound, **estimate(sub, values, seed=95)))
    out = root / output_name
    assert not out.exists()
    out.write_text(json.dumps(dict(data_sha256=sha(data), panels=panels, counts=counts, records=records, runs=provenance,
        models=models, analysis_scope='Full preregistered panel' if selected_models is None else 'INTERIM complete model-family data, hypothesis generation only; original full panel continues.',
        statistics='Source then original lexical cluster; 10000 bootstrap seed95. All paired texts retained. Fidelity NA explicit; changed and tie subsets diagnostic, not outcome selection.',
        limits='Actual content comparison is a different interface from observation reconstruction. Same frozen registered questions only, not complete-world semantic certification. Uses explicit post-hoc corrected teacher labels, not current graders as Gold. No shared Bayes-joint assumption.'), indent=2)+'\n')
    result = dict(map_sha256=sha(out), panels=len(panels), actual_outputs=len(index),
                  gpu_hours=sum(r['gpu_hours'] for r in provenance if r['experiment'] == 'E95'), new_api_calls=0)
    (root / manifest_name).write_text(json.dumps(result, indent=2)+'\n')
    print('E95 COMPLETE', result, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--wait', action='store_true')
    a = p.parse_args()
    if a.wait:
        while True:
            runs = json.loads((a.root / 'runner-pids-v1.json').read_text())
            if all((Path(r['out']) / 'config.json').exists() and 'predictions_sha256' in json.loads((Path(r['out']) / 'config.json').read_text()) for r in runs):
                break
            time.sleep(20)
    analyze(a.root)
