"""Score private-parameter and shared-codebook interventions against their oracle."""
import argparse
import json
from pathlib import Path

import numpy as np


MODES = ['mixed', 'mixed_scope', 'own_dictionary', 'direct']
ORDERS = ['copy_first', 'subtract_first']
CHANGES = ['base', 'owned_a', 'owned_b', 'owned_ab', 'lexical', 'owned_ab_lexical', 'foreign_d', 'dictionary_reorder']
GROUPS = {'seen': [2, 7], 'interpolation': [3, 4, 5, 6], 'extrapolation': [0, 1, 8, 9]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    a = ap.parse_args()
    d = Path(a.directory)
    run = json.loads((d / 'run.json').read_text())
    assert run['no_op_max_error'] <= .1 and run['full_forward_max_error'] <= .1
    rows = [json.loads(line) for line in (d / 'behavior.jsonl').read_text().splitlines()]
    n = len(rows)
    assert n == run['args']['n'] and [r['context'] for r in rows] == list(range(n))
    theta = np.array([r['theta'][:2] for r in rows])
    boot = np.random.default_rng(790).integers(n, size=(4000, n))

    def ci(v):
        return {'mean': float(v.mean()), 'ci95': np.quantile(v[boot].mean(1), [.025, .975]).tolist(), 'n_contexts': n}

    def ratio(num, den):
        bd = den[boot].sum(1)
        assert (bd > 0).all()
        return {'mean': float(num.sum() / den.sum()),
                'ci95': np.quantile(num[boot].sum(1) / bd, [.025, .975]).tolist(), 'n_contexts': n}

    def rule_ci(correct, ts, xs):
        out = {}
        for t, name in [(1, 'copy'), (-1, 'subtract')]:
            mask = ts == t
            out[name + '_accuracy'] = ratio((correct[:, :, xs].mean(-1) * mask).sum(1), mask.sum(1))
        return out

    out = {'run': run, 'conditions': {}, 'responses': {}, 'contrasts': {},
           'limitations': ['A public known-copy source identifies the shared codebook.',
                          'Exact candidate scores, not native generation accuracy.',
                          'Direct table adds source parameters; own+dictionary is not literal single source.',
                          'A logical shared-codebook counterexample alone is not a novel computation theory.']}
    vs, gs, acs = {}, {}, {}
    for mode in MODES:
        for order in ORDERS:
            for change in CHANGES:
                key = mode + '.' + order + '.' + change
                v = np.array([r['scores'][key] for r in rows]).reshape(n, 3, 10, 10)
                gold = np.array([r['gold'][key] for r in rows]).reshape(n, 3, 10)
                assert np.isfinite(v).all()
                true = np.take_along_axis(v, gold[:, :, :, None], -1)[:, :, :, 0]
                other = v.copy()
                np.put_along_axis(other, gold[:, :, :, None], -np.inf, -1)
                margin = true - other.max(-1)
                correct = margin > 0
                vs[key], gs[key], acs[key] = v, gold, correct
                ts = theta.copy()
                if change in ['owned_a', 'owned_ab', 'owned_ab_lexical']:
                    ts[:, 0] *= -1
                if change in ['owned_b', 'owned_ab', 'owned_ab_lexical']:
                    ts[:, 1] *= -1
                out['conditions'][key] = {group: {'accuracy': ci(correct[:, :2, xs].mean((1, 2))),
                    'margin': ci(margin[:, :2, xs].mean((1, 2))), **rule_ci(correct[:, :2], ts, xs)} for group, xs in GROUPS.items()}
                out['conditions'][key]['codebook_lookup_accuracy'] = ci(correct[:, 2].mean(-1))
        for change in CHANGES:
            key = mode + '.both_orders.' + change
            correct = np.mean([acs[mode + '.' + o + '.' + change] for o in ORDERS], axis=0)
            ts = theta.copy()
            if change in ['owned_a', 'owned_ab', 'owned_ab_lexical']:
                ts[:, 0] *= -1
            if change in ['owned_b', 'owned_ab', 'owned_ab_lexical']:
                ts[:, 1] *= -1
            out['conditions'][key] = {group: {'accuracy': ci(correct[:, :2, xs].mean((1, 2))),
                **rule_ci(correct[:, :2], ts, xs)} for group, xs in GROUPS.items()}
            out['conditions'][key]['codebook_lookup_accuracy'] = ci(correct[:, 2].mean(-1))
        # Align every contrast to base gold versus the opposite own operation.
        responses = {}
        for order in ORDERS:
            base_key = mode + '.' + order + '.base'
            base_gold = gs[base_key][:, :2]
            alternative = gs[mode + '.' + order + '.owned_ab'][:, :2]
            assert (base_gold != alternative).all()
            novel = GROUPS['interpolation'] + GROUPS['extrapolation']
            assert np.array_equal(alternative[:, :, novel], gs[mode + '.' + order + '.lexical'][:, :2, novel])
            assert np.array_equal(base_gold[:, :, novel], gs[mode + '.' + order + '.owned_ab_lexical'][:, :2, novel])
            ld = {}
            for change in CHANGES:
                v = vs[mode + '.' + order + '.' + change][:, :2]
                ld[change] = (np.take_along_axis(v, base_gold[:, :, :, None], -1) -
                              np.take_along_axis(v, alternative[:, :, :, None], -1))[:, :, :, 0]
            for group, xs in GROUPS.items():
                for change, sources in [('owned_a', [0]), ('owned_b', [1]), ('owned_ab', [0, 1]), ('lexical', [0, 1])]:
                    value = (ld['base'] - ld[change])[:, sources][:, :, xs].mean((1, 2))
                    responses.setdefault(group + '.' + change + '_signed', []).append(value)
                for change in ['foreign_d', 'dictionary_reorder']:
                    value = (ld[change] - ld['base'])[:, :, xs].mean((1, 2))
                    responses.setdefault(group + '.' + change + '_margin_change', []).append(value)
        out['responses'][mode] = {k: ci(np.mean(values, axis=0)) for k, values in responses.items()}
    for label, ma, mb in [('own_dictionary_minus_mixed', 'own_dictionary', 'mixed'),
                         ('scope_minus_mixed', 'mixed_scope', 'mixed'), ('direct_minus_mixed', 'direct', 'mixed')]:
        delta = np.mean([acs[ma + '.' + o + '.base'].astype(float) - acs[mb + '.' + o + '.base'].astype(float) for o in ORDERS], axis=0)
        out['contrasts'][label] = {g: ci(delta[:, :2, xs].mean((1, 2))) for g, xs in GROUPS.items()}
    (d / 'analysis.json').write_text(json.dumps(out, indent=2))
    print(json.dumps({'base': {k: v for k, v in out['conditions'].items() if k.endswith('both_orders.base')},
                      'responses': out['responses'], 'contrasts': out['contrasts']}, indent=2))


if __name__ == '__main__':
    main()
