"""Frozen E71 contrasts; conflict queries are cue diagnostics, not accuracy."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d / 'run.json').read_text())
    assert run['sanity_max_error'] <= .1 and run['fixedQ_shared_relative_logit_spread_max'] <= .02
    assert run['nonlabel_flip_feature_error_max'] == run['forbidden_attention_mass_max'] == run['untouched_cache_error_max'] == 0
    rows = [json.loads(line) for line in (d / 'behavior.jsonl').read_text().splitlines()]
    assert len(rows) == run['args']['n']
    gold = np.array([r['signs'] for r in rows])
    assert gold.shape == (len(rows), 8) and np.array_equal(gold[:, :4], gold[:, 4:])
    assert np.array_equal(gold[:, :2], -gold[:, 2:4])
    raw = {k: np.array([r['scores'][k] for r in rows]) for k in rows[0]['scores']}
    means = {k: (v[:, :4] * gold[:, :4]).mean(1) for k, v in raw.items()}
    acc = {k: (v[:, :4] * gold[:, :4] > 0).mean(1) for k, v in raw.items()}
    ranks = {k: ((v[:, :2] - v[:, 2:4]) * gold[:, :2] > 0).mean(1) for k, v in raw.items()}
    metrics = {'margin': means, 'accuracy': acc, 'paired_source_ranking': ranks}
    out = dict(run=run, conditions={}, contrasts={}, transfer={}, cue_diagnostics={}, cooperation={}, attention={})
    for k in raw:
        out['conditions'][k] = {name: interval(v[k]) for name, v in metrics.items()}
        out['cue_diagnostics'][k] = {
            'natural_minus_flipped_code_margin': interval(((raw[k][:, :4] - raw[k][:, 4:]) * gold[:, :4]).mean(1)),
            'interpretation': 'Linked: conflicting keys have no unique default gold; this measures cue influence, not accuracy.'}
        if k.startswith('orthogonal.'):
            out['cue_diagnostics'][k]['both_code_values_accuracy'] = interval((raw[k] * gold > 0).mean(1))
        if k in rows[0]['attention']:
            nl = len(rows[0]['attention'][k])
            out['attention'][k] = {}
            for site in ['prefix', 'label']:
                for stat in ['mass', 'within_source', 'within_code']:
                    v = np.array([[r['attention'][k][str(l)][site][stat][:4] for l in range(nl)] for r in rows])
                    out['attention'][k][site + '.' + stat] = interval(v.mean((1, 2)))
    rng = np.random.default_rng(710)
    ix = rng.integers(len(rows), size=(4000, len(rows)))
    for relation in ['linked', 'orthogonal']:
        x, y = relation + '.D1', relation + '.D0'
        out['contrasts'][relation + '.layout'] = {name: interval(v[x] - v[y]) for name, v in metrics.items()}
        for layout in (0, 1):
            base = relation + f'.D{layout}'
            for control in ['instruction', 'single']:
                out['contrasts'][base + '.' + control] = {name: interval(v[base + '.' + control] - v[base]) for name, v in metrics.items()}
        iso = relation + '.isolated'
        blind = relation + '.blind'
        gap = means[blind] - means[iso]
        for variant in ['blind', 'common', 'centered', 'norm', 'negative_common', 'shared_frame']:
            k = relation + '.' + variant
            item = {name: interval(v[k] - v[iso]) for name, v in metrics.items()}
            item['blind_minus_isolated_margin'] = interval(gap)
            if gap.mean() > .2:
                num = means[k] - means[iso]
                ratio = num[ix].mean(1) / gap[ix].mean(1)
                item['fraction_of_blind_effect'] = {'mean': float(num.mean() / gap.mean()), 'ci95': np.quantile(ratio, [.025, .975]).tolist()}
            out['transfer'][k] = item
            out['contrasts'][k + '.minus_native'] = {name: interval(v[k] - v[x]) for name, v in metrics.items()}
        out['cooperation'][relation] = {name: interval(v[blind] - v[relation + '.common'] - v[relation + '.centered'] + v[iso]) for name, v in metrics.items()}
    out['contrasts']['relation_x_layout'] = {
        name: interval(v['linked.D1'] - v['linked.D0'] - v['orthogonal.D1'] + v['orthogonal.D0']) for name, v in metrics.items()}
    for variant in ['D0', 'D1', 'isolated', 'blind', 'common', 'centered', 'shared_frame']:
        out['contrasts'][variant + '.linked_minus_orthogonal'] = {
            name: interval(v['linked.' + variant] - v['orthogonal.' + variant]) for name, v in metrics.items()}
    (d / 'analysis.json').write_text(json.dumps(out, indent=2))
    print('native', {k: v for k, v in out['conditions'].items() if k in ['linked.D0', 'linked.D1', 'orthogonal.D0', 'orthogonal.D1']})
    print('relation_x_layout', out['contrasts']['relation_x_layout'])
    print('shared', {k: v for k, v in out['transfer'].items() if k.endswith('.shared_frame')})
    print('cooperation', out['cooperation'])


if __name__ == '__main__':
    main()
